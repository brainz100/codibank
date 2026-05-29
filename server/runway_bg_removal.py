# -*- coding: utf-8 -*-
"""
runway_bg_removal.py  —  CodiBank 런웨이 배경 제거 모듈
=========================================================

런웨이(동영상) 생성 전, 착장 이미지에서 배경을 제거하는 함수입니다.
입력: OpenCV BGR ndarray (front / back 패널 각각)
출력: BGRA ndarray (alpha 채널 = 인물 마스크)

핵심 설계 (색상키의 한계를 단계로 분리해서 회피):
  ① 연결성 기반 실루엣 — flood-fill로 '테두리에 연결된 배경'만 제거.
     크림 재킷이 배경색이어도 연결성 기반이라 안 깎임.
  ② GrabCut — 배경 색분포를 학습해 다리 사이에 갇힌 배경을 제거.
     전경 잠금 시드에서 '배경색 픽셀(dist<=FG_DIST)'은 제외하는 것이 핵심.
     (이걸 빼면 와이드 진의 다리 사이 배경까지 전경으로 잠겨서 안 지워짐)
  ③ 어두운 앵커 그림자 제거 — 흰/베이지 신발과 회색 그림자는 색이 겹치므로,
     '어두운 픽셀(신발 줄무늬) 주변 회색'은 보존하고 고립된 회색만 제거.

주의 (과거 실패에서 학습):
  - '인물 내부의 큰 배경색 영역을 강제 제거'하는 로직은 절대 넣지 말 것.
    재킷·얼굴도 배경색·대면적이라 함께 날아감.
  - 단일 임계값으로 그림자·신발·다리사이를 동시에 처리하려 하면 반드시 한쪽이 깨짐.

한계:
  흰/베이지 신발, 소매 끝처럼 배경 회색과 색이 완전히 겹치는 영역엔
  미세 잔흔이 남을 수 있음. 임의 착장까지 완벽히 가리려면 USE_REMBG=True 권장.
"""

import numpy as np
import cv2

# ──────────────────────────────────────────────────────────────────
# 설정 (필요 시 여기만 조정)
# ──────────────────────────────────────────────────────────────────
EDGE_TOL      = 30      # ① 테두리 배경 검출 색거리 (작을수록 보수적)
PRBG_TOL      = 45      # ② 약한 배경 후보 색거리 (다리사이/그림자 포함)
FG_DIST       = 30      # ② 전경 잠금 시 '이 거리 이하(배경색)'는 제외 ★다리사이 핵심
CORE_ERODE    = 25      # ② 인물 코어 침식 픽셀
SHADOW_TOL    = 88      # ③ 그림자 회색 검출 색거리
SHADOW_BAND   = 0.80    # ③ 하단 이 비율 아래에서만 그림자 처리
DARK_V        = 95      # ③ 어두운 신발 앵커 기준 밝기
DARK_DILATE   = 19      # ③ 신발 주변 보호 반경 (클수록 흰후광↑, 작을수록 신발손실↑)
HOLE_FILL_MAX = 0.0015  # 작은 구멍(얼굴) 채움 면적 상한 (전체 대비)
HOLE_FILL_TOP = 0.55    # 구멍 채움은 상반신(이 비율 위)만
GRABCUT_ITER  = 8

REPLACE_BG    = None    # None=투명(알파), (B,G,R) 지정 시 그 색으로 합성
USE_REMBG     = False   # True 로 바꾸면 rembg(u2net_human_seg) 1차 → 실패 시 아래 GrabCut 폴백


# ──────────────────────────────────────────────────────────────────
# rembg 1차 경로 (USE_REMBG=True 일 때만 사용)
# ──────────────────────────────────────────────────────────────────
_RB_SESSION = None

def _rembg_session():
    global _RB_SESSION
    if _RB_SESSION is None:
        from rembg import new_session
        _RB_SESSION = new_session("u2net_human_seg")  # 사람 전용 모델
    return _RB_SESSION


def _remove_bg_rembg(img_bgr):
    """의미 분할 기반 배경 제거. 실패 시 예외를 던져 GrabCut 폴백을 유도."""
    from rembg import remove
    from PIL import Image
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    cut = remove(Image.fromarray(rgb), session=_rembg_session())  # RGBA
    rgba = np.array(cut)
    alpha = rgba[:, :, 3]
    if (alpha > 10).mean() < 0.05:           # 거의 다 지워졌으면 비정상 → 폴백
        raise RuntimeError("rembg returned near-empty mask")
    out = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2BGR)
    out = cv2.cvtColor(out, cv2.COLOR_BGR2BGRA)
    out[:, :, 3] = alpha
    return out


# ──────────────────────────────────────────────────────────────────
# GrabCut 파이프라인 (현재 기본 — 추가 의존성 없음, OpenCV만)
# ──────────────────────────────────────────────────────────────────
def _bg_color(img):
    """네 모서리에서 배경색 추정 (median)."""
    c = np.concatenate([
        img[0:25, 0:25].reshape(-1, 3),  img[0:25, -25:].reshape(-1, 3),
        img[-25:, 0:25].reshape(-1, 3),  img[-25:, -25:].reshape(-1, 3),
    ])
    return np.median(c, 0)


def _largest_cc(mask):
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n <= 1:
        return mask
    return (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8) * 255


def _remove_bg_grabcut(img):
    H, W = img.shape[:2]
    bg = _bg_color(img)
    dist = np.sqrt(((img.astype(np.float32) - bg) ** 2).sum(2))
    V = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 2]

    # ① 연결성 기반 실루엣 (재킷 보존)
    cand = (dist < EDGE_TOL).astype(np.uint8)
    ff = cand.copy()
    m = np.zeros((H + 2, W + 2), np.uint8)
    for x, y in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0), (W // 2, H - 1)]:
        if ff[y, x] == 1:
            cv2.floodFill(ff, m, (x, y), 2)
    edge_bg = (ff == 2)
    sil = _largest_cc((~edge_bg).astype(np.uint8) * 255)

    # ② GrabCut (다리 사이 배경 = 배경 색분포로 제거 / 인물 코어 잠금)
    gc = np.full((H, W), cv2.GC_PR_FGD, np.uint8)
    gc[edge_bg] = cv2.GC_BGD
    gc[(dist < PRBG_TOL) & (sil > 0)] = cv2.GC_PR_BGD
    core = cv2.erode(sil, np.ones((CORE_ERODE, CORE_ERODE), np.uint8)) > 0
    gc[core & (dist > FG_DIST)] = cv2.GC_FGD          # ★ 배경색 픽셀은 잠그지 않음
    try:
        cv2.grabCut(img, gc, None, np.zeros((1, 65)), np.zeros((1, 65)),
                    GRABCUT_ITER, cv2.GC_INIT_WITH_MASK)
        mask = np.where((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    except Exception:
        mask = sil.copy()                              # GrabCut 실패 시 실루엣으로
    mask = cv2.bitwise_and(mask, sil)
    mask = _largest_cc(mask)

    # ③ 바닥 그림자 제거 (어두운 신발 앵커 주변 회색은 보존)
    yb = int(H * SHADOW_BAND)
    mx, mn = img.max(2).astype(int), img.min(2).astype(int)
    greyish = (dist < SHADOW_TOL) & ((mx - mn) < 20) & (V > 140)
    dark_near = cv2.dilate((V < DARK_V).astype(np.uint8) * 255,
                           np.ones((DARK_DILATE, DARK_DILATE), np.uint8)) > 0
    sh = np.zeros((H, W), bool)
    sh[yb:] = greyish[yb:] & (~dark_near[yb:]) & (mask[yb:] > 0)
    mask[sh] = 0
    mask = _largest_cc(mask)

    # 작은 구멍(얼굴 하이라이트)만, 상반신에서만 채움 — 다리 사이는 건드리지 않음
    inv = 255 - mask
    nn, ll, ss, _ = cv2.connectedComponentsWithStats(inv, 8)
    small = HOLE_FILL_MAX * H * W
    for i in range(1, nn):
        touch = (ss[i, cv2.CC_STAT_LEFT] == 0 or ss[i, cv2.CC_STAT_TOP] == 0 or
                 ss[i, cv2.CC_STAT_LEFT] + ss[i, cv2.CC_STAT_WIDTH] >= W or
                 ss[i, cv2.CC_STAT_TOP] + ss[i, cv2.CC_STAT_HEIGHT] >= H)
        cy = ss[i, cv2.CC_STAT_TOP] + ss[i, cv2.CC_STAT_HEIGHT] / 2
        if (not touch) and ss[i, cv2.CC_STAT_AREA] < small and cy < HOLE_FILL_TOP * H:
            mask[ll == i] = 255

    # 마감
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    out = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    out[:, :, 3] = mask
    return out


# ──────────────────────────────────────────────────────────────────
# 공개 함수
# ──────────────────────────────────────────────────────────────────
def remove_bg_runway(img_bgr):
    """
    배경 제거 메인 진입점. front / back 패널 각각에 호출.
    img_bgr : OpenCV BGR ndarray
    return  : REPLACE_BG=None 이면 BGRA(투명), 색이 지정되면 BGR(합성).
    """
    if USE_REMBG:
        try:
            bgra = _remove_bg_rembg(img_bgr)
        except Exception as e:
            print(f"[remove_bg_runway] rembg 실패 → GrabCut 폴백: {e}")
            bgra = _remove_bg_grabcut(img_bgr)
    else:
        bgra = _remove_bg_grabcut(img_bgr)

    if REPLACE_BG is None:
        return bgra
    a = bgra[:, :, 3:4].astype(np.float32) / 255.0
    fg = bgra[:, :, :3].astype(np.float32)
    bg = np.array(REPLACE_BG, np.float32).reshape(1, 1, 3)
    return (fg * a + bg * (1 - a)).astype(np.uint8)


if __name__ == "__main__":
    import sys
    from PIL import Image
    path = sys.argv[1]
    im = cv2.cvtColor(np.array(Image.open(path).convert("RGB")), cv2.COLOR_RGB2BGR)
    res = remove_bg_runway(im)
    if res.shape[2] == 4:
        Image.fromarray(cv2.cvtColor(res, cv2.COLOR_BGRA2RGBA)).save("cutout.png")
    else:
        Image.fromarray(cv2.cvtColor(res, cv2.COLOR_BGR2RGB)).save("cutout.png")
    print("saved cutout.png")
