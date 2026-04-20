# ═══════════════════════════════════════════════════════════════════════
# 📋 수정 이력 (MODIFICATION HISTORY) — 최신순
# ═══════════════════════════════════════════════════════════════════════
# 이 블록은 파일 수정 때마다 최상단에 누적됩니다.
# 각 항목은 실제 수정 지점(줄번호)에도 동일한 날짜/요약 주석이 존재합니다.
# 점검 시 이 블록만 읽어도 파일의 최신 상태와 변경 이력을 알 수 있습니다.
#
# ─── 2026-04-20 06:50 KST (치마→바지 재발 근본 원인 4종 수정) ─────────────
#   [원인] 치마 레퍼런스 이미지를 업로드해도 바지로 생성되는 문제의 진짜 원인:
#     ① _pants_rule 데드 코드 (line 3078~3134): 치마/바지 체크 없이 항상
#        "PANTS LENGTH ABSOLUTE PRIORITY / DO NOT use reference image /
#         OVERRIDES the reference image visual" 문구 생성. 현재 최종 프롬프트에
#        삽입은 안 됐지만 데드 코드로 남아있어 재활용 시 치명적 재발 위험.
#     ② _top_wear 기본값에 "waistband" 단어 포함 → Gemini가 바지 힌트로 오해
#     ③ _bot_wear 치마 분기에도 "waistband" 2회 등장 → 혼란 가중
#     ④ Phase 4 Pose "thighs touching (no gap between legs)" → 맨다리 보임
#        암시. 치마 레퍼런스에 상반되어 Gemini가 "바지 = 다리 뚜렷"으로 오판
#
#   [수정 1] _pants_rule + _retry_pants 데드 코드 완전 제거 (~line 3078)
#     - 57줄 삭제. 바지 길이 규칙은 _bot_rule의 바지 분기에 이미 충분
#     - 미사용 페이로드 플래그 request7bu, retryLongerPants 참조 제거
#   [수정 2] _top_wear 치마 인지 분기 추가 (~line 3123)
#     - 치마일 때: "waistband" → "skirt top" / "waist line" / "hip level"
#     - 바지일 때: 기존 "waistband" 유지 (바지에 적절한 용어)
#   [수정 3] _bot_wear 치마 분기에서 "waistband" 단어 제거 (~line 3155)
#     - "Skirt sits at the natural waist line"
#     - "layers OVER the skirt top naturally"
#     - "Skirt upper edge partially visible"
#   [수정 4] Phase 4 Pose 성별 + 치마 여부 분기 (~line 3193)
#     - 여성 + 치마: knees together, feet together or one forward
#       (thighs touching 언급 금지 — 치맛자락 자연스럽게)
#     - 여성 + 바지: 기존 feet 5-8cm + thighs touching 유지
#     - 남성:       feet shoulder-width (15-25cm), 균등 체중, 편안한 스탠스
#     - 효과: 여성 포즈가 보다 자연스러워지고, 치마 레퍼런스에 모순되는
#            "맨다리" 힌트 제거 → Gemini가 레퍼런스(치마) 충실히 반영
#
# ─── 2026-04-20 03:52 KST ────────────────────────────────────────────────
#   [Phase 1 — 퍼스널컬러 summary 추가] (~line 3121)
#     - _pc_summary 추출 추가 (personal_color.summary)
#     - PHASE 1 PERSONA 블록에 "Summary: ..." 주입
#     - Phase 5 personal_color 점수 근거에도 summary 포함
#   [Phase 3 — 하의 착용방식 병렬 추가] (~line 3155)
#     - _bot_wear 로직 신규: 치마/반바지/바지 각각 분기
#     - 치마: 상의 hem이 OVER waistband, 드레스셔츠만 tuck IN 예외
#     - 바지: 기본 OVER waistband, 드레스셔츠는 tuck IN, 아우터는 덮기
#     - PHASE 3 문장에 "Top wearing: ... Bottom wearing: ..." 병렬 주입
#   [Phase 5 — Phase 1 근거 Phase 2/3 종합 평가] (~line 3230)
#     - "use PHASE 1 as REFERENCE CRITERIA, judge PHASE 2+3 against it" 명시
#     - 각 점수 항목이 Phase 1 어느 속성을 근거로 하는지 명시 bullet
#       · personal_color/40 → season/undertone/best/avoid/summary
#       · body_shape/40 → body_type_key
#       · coordination/20 → Phase 2 + Phase 3 wearing 종합
#     - 분석 5섹션 각 불릿에 "PHASE 1 기준", "PHASE 2의 ...",
#       "PHASE 3 착용방식 기반" 표현으로 근거 명시
#
# ─── 2026-04-20 03:40 KST ────────────────────────────────────────────────
#   [옵션 A — 프롬프트 전면 재설계] (~line 3098)
#     - 기존 297줄(22,000자) → 139줄(~8,500자): 중복/되돌림 지시 제거
#     - 구조 5단계 단순화: SYSTEM → P1 PERSONA → P2 GARMENTS
#                          → P3 WEARING → P4 IMAGE → P5 EVAL
#     - "치마는 바지 아님" 중복 3회 → 1회 (bottom_info.is_skirt 분기에서만)
#     - "ABSOLUTE GROUND TRUTH" 3중 반복 제거
#     - 체크리스트 10개 항목 → Phase1 분석 데이터 직접 주입
#     - SKIRT REALISM A~E 5섹션(60줄) → "fabric drapes naturally" 1문장
#     - AI옷장 분석 데이터 신뢰 — Phase1 True/False 확정 시 덮어쓰기 금지
#     - 하의 스타일 분석 출력 강화 (MANDATORY, 생략 금지 명시)
#   [치마 비율 분석 블록 위치 이동] (~line 2705)
#     - 기존 line 2852 → line 2705로 이동
#     - 원인: _skirt_length_cat이 정의(line 2864)보다 앞(line 2737)에서
#             참조되어 UnboundLocalError 발생 → 치마→바지 오생성 원인
#     - 해결: bottom_info 구성 전에 비율 분석 완료
#   [_phase1_locked 가드 도입] (~line 2850)
#     - Phase1 is_skirt True/False 확정 시 두 번째 bottom_info 재구성 스킵
#     - AI옷장 아이템(이미 분류 완료)은 덮어쓰기 금지 원칙 구현
# ═══════════════════════════════════════════════════════════════════════

"""CodiBank OpenAI Styling Proxy (Prototype)

- POST /api/ai/styling
  - 입력(날씨/프로필/코디목적/얼굴) 기반으로 OpenAI 이미지 생성 API를 호출해
    '추천 스타일링 이미지'를 base64(DataURL)로 반환합니다.

왜 프록시가 필요할까요?
- 브라우저(프론트)에서 OpenAI API Key를 직접 쓰면 키가 노출됩니다.
- 따라서 PC에서 로컬 서버를 띄우고(같은 Wi‑Fi), 모바일은 해당 서버를 호출합니다.

실행:
  cd server
  python3 -m pip install -r requirements.txt
  # PowerShell(Windows):  setx OPENAI_API_KEY "..."  (새 터미널에서 적용)
  # macOS/Linux:         export OPENAI_API_KEY="..."
  python3 mock_backend.py

기본 포트: 8787
"""

from __future__ import annotations

import base64
import hashlib
import io
import ipaddress
import json
import os
import platform
import re
import socket
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, Tuple
import requests as http_requests

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# [2026-04-08] Phase 2 모듈
try:
    from face_skin_analyzer import analyze_skin_tone, build_enhanced_prompt
    _HAS_SKIN_ANALYZER = True
    print("[Phase2] face_skin_analyzer loaded")
except ImportError:
    _HAS_SKIN_ANALYZER = False

# [2026-04-08] 체형 DB 로딩
_BODY_TYPE_DB = {}
try:
    import json as _json_bt
    _bt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "body_type_db.json")
    with open(_bt_path, "r", encoding="utf-8") as _f:
        _BODY_TYPE_DB = _json_bt.load(_f)
    print(f"[BodyType] DB 로드: 여성 {len(_BODY_TYPE_DB.get('female',{}))}종, 남성 {len(_BODY_TYPE_DB.get('male',{}))}종")
except Exception as _e:
    print(f"[BodyType] DB 로드 실패: {_e}")

def _get_body_type_info(gender, body_type_key):
    if not body_type_key or not _BODY_TYPE_DB:
        return None
    g = "female" if str(gender).lower() in ("f","female","여성") else "male"
    return _BODY_TYPE_DB.get(g, {}).get(body_type_key)

def _build_body_type_prompt(gender, body_type_key):
    info = _get_body_type_info(gender, body_type_key)
    if not info:
        return ""
    lines = [
        "",
        "BODY TYPE PROFILE: " + info["label"] + " (" + info["en"] + ")",
        "  Feature: " + info["feature"],
        "  Best color strategy: " + info["best_color"],
        "  Avoid color strategy: " + info["worst_color"],
        "  Recommended style: " + info["do_style"],
        "  Avoid style: " + info["dont_style"],
        "  IMPORTANT: Apply these body type rules when generating the outfit image.",
        "  The outfit MUST follow 'do_style' and AVOID 'dont_style' silhouettes.",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════
# [2026-04-19 BODY] 신체 프로필 통합 빌더
# ───────────────────────────────────────────────────
# 목적: BMI 자동 계산 + 체형 특성 통합 블록을 이미지 생성 프롬프트에 주입
# 사용처: codistyle_generate, _ai_styling_via_gemini 양쪽 공통
# 역할: 사용자 신체 데이터를 구조화된 프롬프트 블록으로 변환해
#       Gemini가 "이 체형에 이 옷이 어떻게 보이는가"를 객관적으로 이미지화
# ═══════════════════════════════════════════════════
def _compute_bmi(height_str, weight_str):
    """키/몸무게 문자열 → (bmi_val, bmi_cat_ko, bmi_cat_en). 실패 시 (0, '', '')."""
    try:
        h = float(str(height_str).strip() or 0)
        w = float(str(weight_str).strip() or 0)
        if h < 100 or w < 20:
            return 0, "", ""
        bmi = round(w / ((h / 100) ** 2), 1)
        if bmi < 18.5:
            return bmi, "마른 체형", "slim"
        elif bmi < 23:
            return bmi, "표준 체형", "average"
        elif bmi < 25:
            return bmi, "약간 통통", "slightly heavy"
        else:
            return bmi, "통통한 체형", "heavier"
    except Exception:
        return 0, "", ""


def _build_body_profile_block(gender, age, height, weight, body_type_key, lang="en"):
    """
    신체 프로필 통합 블록 생성 (Phase 1 PERSONA에 삽입)
    이미지 생성 단계에서 체형 특성이 실제로 반영되도록 구조화
    """
    lines = []
    gender_en = "woman" if str(gender).upper() in ("F", "FEMALE", "여성") else "man"
    bmi_val, bmi_cat_ko, bmi_cat_en = _compute_bmi(height, weight)

    # 1) 기본 피지컬
    phys_parts = [f"Korean {gender_en}"]
    if age:
        phys_parts.append(str(age))
    if height and weight:
        if bmi_val > 0:
            phys_parts.append(f"height {height}cm, weight {weight}kg, BMI {bmi_val} ({bmi_cat_en})")
        else:
            phys_parts.append(f"height {height}cm, weight {weight}kg")
    lines.append("Physical: " + ", ".join(phys_parts) + ".")

    # 2) BMI 기반 실루엣 가이드 (암묵적 지시 대신 구체 지시)
    bmi_guides = {
        "slim":           "Slim build: avoid oversized/baggy silhouettes that swamp the frame. Subtle layering and structured cuts maintain proportion.",
        "average":        "Average build: most silhouettes work; prioritize balanced proportions between top and bottom.",
        "slightly heavy": "Slightly fuller build: straight or semi-fitted silhouettes work best. Avoid overly tight or overly baggy extremes that exaggerate volume.",
        "heavier":        "Fuller build: vertical lines, darker tones on larger areas, and structured (not clingy, not voluminous) silhouettes flatter the frame.",
    }
    if bmi_cat_en and bmi_guides.get(bmi_cat_en):
        lines.append("BMI-based silhouette guidance: " + bmi_guides[bmi_cat_en])

    # 3) 체형 특성 블록 (_build_body_type_prompt 재활용)
    bt_block = _build_body_type_prompt(gender, body_type_key)
    if bt_block:
        lines.append(bt_block.strip())

    # 4) 객관성 강제 지시
    lines.append(
        "CRITICAL — OBJECTIVE RENDERING: "
        "The generated image MUST show the outfit AS IT WOULD ACTUALLY LOOK on this specific body. "
        "Apply the recommended silhouette, avoid the forbidden silhouette, "
        "and render realistic body conforming — do not default to a generic idealized model body."
    )

    return "\n".join(lines)


try:
    from pc_prompt_helper import _build_pc_prompt_block
    print("[Phase2] pc_prompt_helper loaded")
except ImportError:
    def _build_pc_prompt_block(pc, mode="styling"):
        if not pc or not pc.get("season"): return ""
        s = pc.get("season",""); u = pc.get("undertone","")
        bc = ", ".join((pc.get("best_colors") or [])[:3])
        ac = ", ".join((pc.get("avoid_colors") or [])[:2])
        # 확장 속성 (레이더/속성가이드)
        radar = pc.get("radar") or {}
        attrs = pc.get("attributes") or {}
        textures = pc.get("bestTextures") or []
        _extra = ""
        if radar:
            _extra += f" Skin analytics: brightness={radar.get('brightness','-')}, redness(Hb)={radar.get('redness','-')}, yellowness(Melanin)={radar.get('yellowness','-')}, clarity={radar.get('clarity','-')}, contrast={radar.get('contrast','-')}, texture={radar.get('texture','-')}."
        if attrs:
            _extra += f" Color attributes: value(lightness)={attrs.get('value','-')}%, chroma={attrs.get('chroma','-')}%, contrast_level={attrs.get('contrast','-')}%."
        if textures:
            _extra += f" Best textures: {', '.join(textures)}."
        return " Personal color: " + s + " (" + u + "). Best: " + bc + ". Avoid: " + ac + "."


# OpenAI 공식 SDK
from openai import OpenAI

try:
    import openai as _openai_pkg  # type: ignore
except Exception:  # pragma: no cover
    _openai_pkg = None

# --- .env 로딩(초보자 실수 방지) -----------------------------------------
# 사용자가 흔히 하는 실수:
#   - codibank 폴더(상위)에서 `python server/mock_backend.py`를 실행
#   - 그런데 `.env`는 `server/.env`에 만들어둠
# 이 경우 CWD 기준 load_dotenv()만 쓰면 `.env`를 못 읽어서 OPENAI_API_KEY가 비어버립니다.
# 따라서 "이 파일이 있는 폴더(server)"의 .env를 우선 로딩합니다.
_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_HERE, ".env"))
# 그리고 상위 폴더의 .env도 혹시 있을 수 있어 보조로 로딩
load_dotenv(os.path.join(os.path.dirname(_HERE), ".env"))


# ══════════════════════════════════════════════════════════════
# [STEP 1~3] 패션 AI 기술 초기화
# rembg(배경제거) + Lykdat(속성분석) + Marqo(유사도매칭)
# ══════════════════════════════════════════════════════════════

# ── [STEP 1] rembg: 의류 배경 제거 (HF Space API) ────────────
_REMBG_API_URL = os.getenv("REMBG_API_URL", "").rstrip("/")

def remove_clothing_bg(img_bytes: bytes) -> bytes:
    """HF Space rembg API로 의류 배경 제거 — 실패 또는 품질 불량 시 원본 반환"""
    if not _REMBG_API_URL:
        print("[rembg] ⚠ REMBG_API_URL 미설정, 원본 사용")
        return img_bytes
    try:
        resp = http_requests.post(
            f"{_REMBG_API_URL}/remove-bg",
            files={"file": ("image.jpg", img_bytes, "image/jpeg")},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok") and data.get("image"):
                b64 = data["image"].split(",", 1)[1]
                result = base64.b64decode(b64)
                # ── [2026-04-09 수정] rembg 품질 검증 ──
                # 원인: 체크패턴/밝은색 의류에서 rembg가 옷 본체까지 제거
                # 해결: 비투명 픽셀 비율 < 15% 이면 원본으로 폴백
                try:
                    from PIL import Image as _PILImg
                    _rimg = _PILImg.open(io.BytesIO(result))
                    if _rimg.mode == 'RGBA':
                        _alpha = _rimg.getchannel('A')
                        _total = _rimg.width * _rimg.height
                        _visible = sum(1 for p in _alpha.getdata() if p > 128)
                        _ratio = _visible / max(_total, 1)
                        if _ratio < 0.15:
                            print(f"[rembg] ⚠ 품질 불량 (비투명 {_ratio:.1%}) — 원본 사용")
                            return img_bytes
                        # 비투명 비율이 적절하면 흰색 배경 합성 (투명 PNG 깨짐 방지)
                        _white = _PILImg.new('RGBA', _rimg.size, (255, 255, 255, 255))
                        _white.paste(_rimg, mask=_rimg.split()[3])
                        _buf = io.BytesIO()
                        _white.convert('RGB').save(_buf, format='PNG', optimize=True)
                        result = _buf.getvalue()
                        print(f"[rembg] ✅ 배경 제거 완료 (비투명 {_ratio:.1%}, 흰배경 합성)")
                    else:
                        print("[rembg] ✅ HF Space 배경 제거 완료 (알파 없음)")
                except Exception as _qe:
                    print(f"[rembg] ⚠ 품질 검증 스킵: {_qe}")
                return result
        print(f"[rembg] ⚠ HF Space 응답 오류: {resp.status_code}")
    except Exception as e:
        print(f"[rembg] ⚠ HF Space 호출 실패, 원본 사용: {e}")
    return img_bytes

# ── [STEP 2] Lykdat: 패션 속성 태깅 ──────────────────────────
_LYKDAT_KEY = os.getenv("LYKDAT_API_KEY", "")

def lykdat_tag_item(img_bytes: bytes) -> dict:
    """의류 이미지 → 카테고리/컬러/패턴/실루엣 자동 태깅 (cloudapi v1/detection/tags)"""
    if not _LYKDAT_KEY:
        return {}
    try:
        resp = http_requests.post(
            "https://cloudapi.lykdat.com/v1/detection/tags",
            headers={"x-api-key": _LYKDAT_KEY},
            files={"image": ("item.png", img_bytes, "image/png")},
            timeout=10
        )
        if resp.status_code != 200:
            print(f"[Lykdat] 실패: HTTP {resp.status_code} {resp.text[:100]}")
            return {}
        raw = resp.json()
        # tags 엔드포인트 응답: {"data": {"colors":[], "items":[], "labels":[]}} 또는 직접 배열
        d = raw.get("data", raw)
        if isinstance(d, list):
            # 일부 버전: 바로 리스트 반환
            labels = d
            items, colors = [], []
        else:
            items  = d.get("items", [])
            colors = sorted(d.get("colors", []),
                            key=lambda x: x.get("confidence", 0), reverse=True)
            labels = d.get("labels", [])

        result = {
            "lykdat_category":   items[0].get("name", "")    if items  else "",
            "lykdat_color_hex":  "#" + colors[0].get("hex_code","") if colors else "",
            "lykdat_color_name": colors[0].get("name", "")   if colors else "",
            "lykdat_pattern":    next((l.get("name","") for l in labels
                                  if l.get("classification") == "textile pattern"), ""),
            "lykdat_silhouette": next((l.get("name","") for l in labels
                                  if l.get("classification") == "silhouette"), ""),
        }
        print(f"[Lykdat] ✅ 태깅 완료: {result['lykdat_category']} / {result['lykdat_color_name']}")
        return result
    except Exception as e:
        print(f"[Lykdat] 실패: {e}")
        return {}

# ── [STEP 3] Marqo-FashionSigLIP: 패션 임베딩 ────────────────
_fashion_model     = None
_fashion_processor = None
_FASHION_MODEL_ID  = "Marqo/marqo-fashionSigLIP"

def _get_fashion_model():
    global _fashion_model, _fashion_processor
    if _fashion_model is None:
        try:
            from transformers import AutoModel, AutoProcessor
            print("[FashionSigLIP] 모델 로드 중... (최초 1회, 약 1~2분)")
            _fashion_processor = AutoProcessor.from_pretrained(
                _FASHION_MODEL_ID, trust_remote_code=True)
            _fashion_model = AutoModel.from_pretrained(
                _FASHION_MODEL_ID, trust_remote_code=True)
            _fashion_model.eval()
            print("[FashionSigLIP] ✅ 모델 로드 완료")
        except Exception as e:
            print(f"[FashionSigLIP] ⚠ 로드 실패 (계속 진행): {e}")
    return _fashion_model, _fashion_processor

def get_fashion_embedding(img_bytes: bytes) -> list | None:
    """의류 이미지 → 512차원 패션 벡터 (유사도 계산용)"""
    try:
        import torch
        import numpy as np
        from PIL import Image
        model, processor = _get_fashion_model()
        if model is None:
            return None
        img    = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        inputs = processor(images=img, return_tensors="pt", padding=True)
        with torch.no_grad():
            feat = model.get_image_features(**inputs)
            feat = feat / feat.norm(dim=-1, keepdim=True)
        print("[FashionSigLIP] ✅ 임베딩 생성 완료 (512차원)")
        return feat[0].tolist()
    except Exception as e:
        print(f"[FashionSigLIP] 임베딩 실패: {e}")
        return None

def cosine_similarity(v1: list, v2: list) -> float:
    """두 임베딩 벡터 간 코사인 유사도 (0.0~1.0, 높을수록 유사)"""
    try:
        import numpy as np
        a, b = np.array(v1, dtype=float), np.array(v2, dtype=float)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        return float(np.dot(a, b) / denom) if denom > 0 else 0.0
    except Exception:
        return 0.0


# ══════════════════════════════════════════════════════════════
# Cloudflare R2 전역 클라이언트 (서버 시작 시 1회 초기화)
# ══════════════════════════════════════════════════════════════
_R2_CLIENT = None
_R2_BUCKET = os.getenv("R2_BUCKET_NAME", "codibank")
_R2_PUB_URL = os.getenv("R2_PUBLIC_URL", "").rstrip("/")  # 예: https://pub.codibank.r2.dev

def _get_r2():
    global _R2_CLIENT
    if _R2_CLIENT is not None:
        return _R2_CLIENT
    ep  = os.getenv("R2_ENDPOINT", "")
    # [2026-04-08] R2_ENDPOINT가 없으면 R2_ACCOUNT_ID로 자동 구성
    if not ep:
        acct = os.getenv("R2_ACCOUNT_ID", "")
        if acct:
            ep = f"https://{acct}.r2.cloudflarestorage.com"
            print(f"[R2] R2_ENDPOINT 미설정 → R2_ACCOUNT_ID로 자동 구성: {ep}")
    ak  = os.getenv("R2_ACCESS_KEY_ID", "")
    sk  = os.getenv("R2_SECRET_ACCESS_KEY", "")
    if not (ep and ak and sk):
        return None
    try:
        import boto3
        _R2_CLIENT = boto3.client(
            "s3",
            endpoint_url=ep,
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            region_name="auto",
        )
        print("[R2] ✅ 클라이언트 초기화 완료")
    except Exception as e:
        print(f"[R2] ⚠ 초기화 실패: {e}")
        _R2_CLIENT = None
    return _R2_CLIENT

def _upload_to_r2(fname: str, data: bytes, mime: str = "image/jpeg") -> str | None:
    """R2에 파일 업로드 → 공개 URL 반환 (실패 시 None)"""
    r2 = _get_r2()
    if not r2:
        return None
    try:
        r2.put_object(
            Bucket=_R2_BUCKET,
            Key=f"uploads/{fname}",
            Body=data,
            ContentType=mime,
            CacheControl="public, max-age=31536000",
        )
        # 공개 URL 반환 (R2_PUBLIC_URL 설정 시 사용, 없으면 /uploads/ 경로)
        if _R2_PUB_URL:
            return f"{_R2_PUB_URL}/uploads/{fname}"
        return f"/uploads/{fname}"
    except Exception as e:
        print(f"[R2] 업로드 실패 ({fname}): {e}")
        return None

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app, allow_headers=["Content-Type", "X-Admin-Key", "Authorization"])

# 얼굴 사진(DataURL)까지 포함되면 요청 바디가 커질 수 있어 넉넉히 허용합니다(10MB).
# ✅ [버그1 수정] 얼굴 사진(base64) 포함 시 요청 바디가 커질 수 있어 허용 크기 확대
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25MB

# 영구 업로드 저장소
# - Render 등 배포 환경에서는 휘발성 filesystem 대신 고정 경로를 우선 사용
# - 로컬 개발은 기존 server/uploads도 함께 유지/호환합니다.
_RENDER_DEFAULT_UPLOAD_DIR = "/opt/render/.codibank/uploads"
_LEGACY_UPLOAD_DIR = os.path.join(_HERE, "uploads")
_UPLOAD_DIR = os.getenv("CODIBANK_UPLOAD_DIR") or (_RENDER_DEFAULT_UPLOAD_DIR if os.path.isdir("/opt/render") else _LEGACY_UPLOAD_DIR)
os.makedirs(_UPLOAD_DIR, exist_ok=True)
os.makedirs(_LEGACY_UPLOAD_DIR, exist_ok=True)

# 브라우저에서 저장된 경로를 그대로 쓰기 위해 고정 prefix 사용
_UPLOAD_PREFIX = "/uploads/"

# ══════════════════════════════════════════════════════════════
# [스타일리스트 매칭 엔진] DB 로딩
# - fashion_keywords_db.json: 7도시 × 15목적 × 남녀 키워드
# - stylist_db_server.json: 7도시 × 16목적 × 남녀 = 11,200명 프로필
# ══════════════════════════════════════════════════════════════
_FASHION_DB = {}
_STYLIST_DB = {}
try:
    _fk_path = os.path.join(_HERE, "fashion_keywords_db.json")
    if os.path.exists(_fk_path):
        with open(_fk_path, "r", encoding="utf-8") as _f:
            _FASHION_DB = json.load(_f)
        print(f"[스타일리스트] fashion_keywords_db.json 로드 완료 ({len(_FASHION_DB.get('city_keywords',{}))}개 도시)")
except Exception as _e:
    print(f"[스타일리스트] fashion_keywords_db.json 로드 실패: {_e}")

try:
    _sd_path = os.path.join(_HERE, "stylist_db_server.json")
    if os.path.exists(_sd_path):
        with open(_sd_path, "r", encoding="utf-8") as _f:
            _STYLIST_DB = json.load(_f)
        print(f"[스타일리스트] stylist_db_server.json 로드 완료 ({len(_STYLIST_DB)}개 도시)")
except Exception as _e:
    print(f"[스타일리스트] stylist_db_server.json 로드 실패: {_e}")

# 스타일리스트 매칭 엔진 (선택적 import — 파일 없어도 서버 정상 작동)
_STYLIST_ENGINE = None
try:
    # [2026-04-06 수정] gunicorn server.mock_backend:app 실행 시
    # Python이 server/ 폴더를 못 찾는 문제 해결
    import sys as _sys
    if _HERE not in _sys.path:
        _sys.path.insert(0, _HERE)
    from stylist_matching_engine import process_styling_request as _process_styling
    _STYLIST_ENGINE = _process_styling
    print("[스타일리스트] stylist_matching_engine.py 로드 완료")
except Exception as _import_err:
    # [2026-04-06 수정] ImportError뿐 아니라 모든 에러를 잡아서 원인 출력
    print(f"[스타일리스트 ❌] stylist_matching_engine.py 로드 실패: {type(_import_err).__name__}: {_import_err}")
    import traceback; traceback.print_exc()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_upload_bytes(slot: str, ext: str, data: bytes, *, fixed_name: str | None = None) -> str:
    """이미지 저장: R2 우선 → 로컬 폴백. 상대 경로(/uploads/..) 반환"""

    slot = re.sub(r"[^a-z0-9_-]+", "", str(slot or "img").lower())[:16] or "img"
    ext  = re.sub(r"[^a-z0-9]+",   "", str(ext  or "jpg").lower())  or "jpg"
    fname = fixed_name or f"{slot}_{_now_ms()}_{os.urandom(3).hex()}.{ext}"

    # 1순위: Cloudflare R2 업로드
    mime_map = {"jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png",
                "webp":"image/webp","gif":"image/gif"}
    mime = mime_map.get(ext, "image/jpeg")
    r2_url = _upload_to_r2(fname, data, mime)
    if r2_url:
        print(f"[R2] ✅ 업로드 완료: {fname}")
        # ──── [2026-04-11 수정] 항상 상대경로(/uploads/xxx) 반환 ────
        # 원인: R2 절대 URL(https://pub-xxx.r2.dev/...) 반환 시
        #       프론트에서 백엔드URL + R2URL로 이중 연결 → ERR_NAME_NOT_RESOLVED
        # 해결: serve_upload proxy가 R2 접근을 처리하므로 상대경로만 반환
        # 관련파일: codistyle.html, closet.html (이미지 URL 조립)
        # ────
        return f"{_UPLOAD_PREFIX}{fname}"

    # 2순위: 로컬 파일시스템 폴백
    fpath = os.path.join(_UPLOAD_DIR, fname)
    with open(fpath, "wb") as f:
        f.write(data)
    print(f"[로컬] 저장 완료 (R2 없음): {fname}")
    return f"{_UPLOAD_PREFIX}{fname}"


def _public_base() -> str:
    explicit = str(os.getenv("PUBLIC_BASE_URL") or "").strip().rstrip("/")
    if explicit:
        return explicit
    proto = str(request.headers.get("X-Forwarded-Proto") or request.scheme or "https").split(",")[0].strip() or "https"
    host = str(request.headers.get("X-Forwarded-Host") or request.host or "").split(",")[0].strip()
    if host:
        if host.endswith('onrender.com') and proto == 'http':
            proto = 'https'
        return f"{proto}://{host}"
    return request.host_url.rstrip("/")


def _download_remote_image(url: str, timeout: int = 12) -> Tuple[str, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (CodiBankBot/1.0)",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        mime = str(resp.headers.get_content_type() or "image/jpeg")
        data = resp.read()
        if not data:
            raise ValueError("empty image response")
        if len(data) > 12 * 1024 * 1024:
            raise ValueError("remote image too large")
        return mime, data


def _fetch_remote_html(url: str, timeout: int = 12) -> Tuple[str, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": urllib.parse.urlsplit(url).scheme + "://" + urllib.parse.urlsplit(url).netloc + "/",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        final_url = getattr(resp, "geturl", lambda: url)() or url
        charset = resp.headers.get_content_charset() or "utf-8"
        raw = resp.read()
        html = raw.decode(charset, errors="ignore")
        return final_url, html


def _absolutize_url(page_url: str, maybe_url: str) -> str:
    s = (maybe_url or "").strip()
    if not s:
        return ""
    if s.startswith("//"):
        return "https:" + s
    return urllib.parse.urljoin(page_url, s)


def _looks_bad_img(url: str) -> bool:
    u = (url or "").lower()
    bad_bits = ["logo", "icon", "sprite", "avatar", "banner", "badge", "thumb"]
    return any(b in u for b in bad_bits)


def _extract_best_image_from_html(page_url: str, html: str) -> str:
    patterns = [
        r'<meta[^>]+property=["\']og:image(?::url)?["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image(?::url)?["\']',
        r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image(?::src)?["\']',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.I | re.S)
        if m:
            cand = _absolutize_url(page_url, m.group(1))
            if cand and not _looks_bad_img(cand):
                return cand

    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I | re.S)
    candidates = []
    for src in img_matches:
        absu = _absolutize_url(page_url, src)
        if not absu or _looks_bad_img(absu):
            continue
        if not re.search(r'\.(jpg|jpeg|png|webp|gif|avif|bmp)(\?|$)', absu, re.I):
            continue
        candidates.append(absu)
    if candidates:
        # 긴 URL/뒤쪽 파일명일수록 상세 이미지일 가능성이 높음
        candidates.sort(key=lambda s: (len(s), s.count('/')), reverse=True)
        return candidates[0]
    return ""


def _resolve_representative_image(url: str) -> Tuple[str, str]:
    src = (url or "").strip()
    if not src:
        raise ValueError("url is required")
    if re.search(r'\.(jpg|jpeg|png|webp|gif|avif|bmp)(\?|$)', src, re.I):
        return src, "직접 이미지 URL"
    final_url, html = _fetch_remote_html(src)
    img_url = _extract_best_image_from_html(final_url, html)
    if not img_url:
        raise ValueError("대표 이미지를 찾지 못했어요. 직접 이미지 URL(jpg/png/webp)을 넣어주세요.")
    return img_url, "쇼핑몰 대표 이미지"


def _mime_to_ext(mime: str) -> str:
    m = str(mime or "").lower()
    if "png" in m:
        return "png"
    if "webp" in m:
        return "webp"
    if "jpeg" in m or "jpg" in m:
        return "jpg"
    return "jpg"


def _collect_ref_images(payload: Dict[str, Any]) -> Tuple[list[tuple[str, str, bytes]], bytes | None]:
    refs: list[tuple[str, str, bytes]] = []
    face_bytes_for_key: bytes | None = None

    face_data_url = payload.get("faceImage")
    face_url = str(payload.get("faceImageUrl") or "").strip()
    if face_data_url:
        try:
            mime, img_bytes = _data_url_to_bytes(str(face_data_url))
            refs.append(("face", mime, img_bytes))
            face_bytes_for_key = img_bytes
        except Exception:
            face_bytes_for_key = None
    elif face_url.startswith(("http://", "https://")):
        try:
            mime, img_bytes = _download_remote_image(face_url)
            refs.append(("face", mime, img_bytes))
            face_bytes_for_key = img_bytes
        except Exception:
            face_bytes_for_key = None

    clothing_images = payload.get("clothingImages") or {}
    clothing_urls = payload.get("clothingImageUrls") or {}
    for slot in ("top", "bottom"):
        data_url = str((clothing_images or {}).get(slot) or "").strip()
        remote_url = str((clothing_urls or {}).get(slot) or "").strip()
        if data_url:
            try:
                mime, img_bytes = _data_url_to_bytes(data_url)
                refs.append((slot, mime, img_bytes))
                continue
            except Exception:
                pass
        if remote_url and remote_url.startswith(("http://", "https://")):
            try:
                mime, img_bytes = _download_remote_image(remote_url)
                refs.append((slot, mime, img_bytes))
            except Exception:
                pass

    return refs, face_bytes_for_key


def _make_ref_bios(refs: list[tuple[str, str, bytes]]) -> list[io.BytesIO]:
    bios: list[io.BytesIO] = []
    for label, mime, raw in refs:
        bio = io.BytesIO(raw)
        bio.name = f"{label}.{_mime_to_ext(mime)}"
        bios.append(bio)
    return bios


def _make_ai_cache_key(payload: Dict[str, Any], face_bytes: bytes | None, ref_images: list[tuple[str, str, bytes]] | None = None) -> str:
    """요청 입력을 기반으로 안정적인 캐시 키를 생성합니다.

    - OpenAI 호출이 실패하거나 느릴 때, 이전에 생성해 둔 이미지를 즉시 반환하기 위함
    - seed가 포함되어야 '다시 코디'가 다른 결과로 저장됩니다.
    """

    user = payload.get("user") or {}
    weather = payload.get("weather") or {}

    body = {
        "purposeKey": payload.get("purposeKey") or "",
        "purposeLabel": payload.get("purposeLabel") or "",
        "customText": str(payload.get("customText") or "").strip(),  # [2026-04-10] 직접입력 캐시 분리
        "seed": payload.get("seed") or 0,
        "forDateKey": payload.get("forDateKey") or payload.get("dateKey") or "",
        "user": {
            "gender": user.get("gender") or "",
            "ageGroup": user.get("ageGroup") or "",
            "height": user.get("height") or "",
            "weight": user.get("weight") or "",
        },
        "weather": {
            "temp": weather.get("temp"),
            "text": weather.get("text") or "",
            "location": weather.get("location") or "",
        },
    }

    if face_bytes:
        body["faceHash"] = _sha256_hex(face_bytes)[:16]

    if ref_images:
        body["refHashes"] = [f"{label}:{_sha256_hex(raw)[:16]}" for label, _mime, raw in ref_images]
        body["mode"] = payload.get("mode") or "styling"

    raw = json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return _sha256_hex(raw)[:24]

# 지연 초기화: 요청 시점에 생성
_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _now_ms() -> int:
    return int(time.time() * 1000)


def _sdk_version() -> str:
    try:
        v = getattr(_openai_pkg, "__version__", None)
        return str(v) if v else "unknown"
    except Exception:
        return "unknown"


def _safe_bool(v: Any) -> bool:
    return bool(v) and str(v).strip() not in ("0", "false", "False", "none", "None")


def _data_url_to_bytes(data_url: str) -> Tuple[str, bytes]:
    """data:image/...;base64,.... -> (mime, bytes)"""
    m = re.match(r"^data:(image\/[^;]+);base64,(.+)$", data_url.strip(), re.DOTALL)
    if not m:
        raise ValueError("Invalid data URL")
    mime = m.group(1)
    b64 = m.group(2)
    return mime, base64.b64decode(b64)


def _korean_to_en_age(age_group: str) -> str:
    # 가입 페이지 값: 10s/20s/30s/40s/50s/60p
    mapping = {
        "10s": "teen",
        "20s": "20s",
        "30s": "30s",
        "40s": "40s",
        "50s": "50s",
        "60p": "60+",
    }
    return mapping.get(age_group, age_group or "adult")


# ──── [2026-04-10 수정] _normalize_gender_code / _gender_en 통합 정규화
# 원인: profile.html이 'female'/'male' 저장 → 서버가 'F'/'M' 단일문자만 처리
#       → 모든 여성 사용자가 남성('person')으로 처리되는 심각한 버그
# 해결: 모든 가능한 성별 값('female','male','여성','남성','F','M' 등)을 통합 처리
# 관련파일: closet.html(payload), codistyle.html(payload), profile.html(저장)
# ────
def _normalize_gender_code(g: str) -> str:
    """어떤 형태의 gender 값이든 'F' 또는 'M'으로 정규화"""
    v = (g or "").strip().lower()
    if v in ("f", "female", "woman", "여", "여자", "여성"):
        return "F"
    if v in ("m", "male", "man", "남", "남자", "남성"):
        return "M"
    return "M"  # 미등록 시 기본값


def _gender_en(g: str) -> str:
    code = _normalize_gender_code(g)
    return "female" if code == "F" else "male"


def _temp_bucket(temp: Any) -> str:
    try:
        t = float(temp)
    except Exception:
        return "mild"
    if t <= 4:
        return "very cold"
    if t <= 11:
        return "cool"
    if t <= 20:
        return "mild"
    if t <= 27:
        return "warm"
    return "hot"


def _purpose_to_style(purpose_key: str, purpose_label: str) -> Tuple[str, str]:
    k = (purpose_key or "").strip()

    _MAP = {
        # 1. 비즈니스 포멀
        "bizFormal": (
            "business formal",
            "sharp tailored suit, silk tie, polished leather shoes, high-end corporate setting, professional confidence",
        ),
        # 2. 데일리 오피스룩
        "officeDaily": (
            "daily office look",
            "smart casual office wear, blazer with slacks, modern professional look, bright office lighting",
        ),
        # 3. 면접룩
        "interview": (
            "interview attire",
            "neat and trustworthy interview attire, navy or charcoal suit, modest accessories, clean and polished aesthetic",
        ),
        # 4. 결혼식 하객룩
        "weddingGuest": (
            "wedding guest outfit",
            "elegant wedding guest outfit, sophisticated semi-formal, pastel or neutral tones, chic guest look",
        ),
        # 5. 소개팅룩
        "blindDate": (
            "blind date outfit",
            "charming blind date outfit, clean knitwear and chinos, soft and approachable vibe, cozy cafe background",
        ),
        # 6. 로맨틱 데이트룩
        "romanticDate": (
            "romantic date night",
            "romantic date night style, stylish dress or dress shirt, soft warm lighting, intimate atmosphere",
        ),
        # 7. 상견례/가족모임
        "familyMeet": (
            "formal family gathering",
            "formal family gathering look, conservative and elegant, modest coat or suit, graceful aesthetic",
        ),
        # 8. 사교 모임/파티
        "socialParty": (
            "social party",
            "trendy social party outfit, statement accessories, vibrant party vibe, stylish evening look",
        ),
        # 9. 주말 나들이
        "weekendOut": (
            "casual weekend outing",
            "casual weekend outing, bright colors, outdoor park background, relaxed and natural aesthetic",
        ),
        # 10. 여행지 인생샷
        "travelShot": (
            "vacation travel shot",
            "vacation photography style, resort wear, straw hat, sunglasses, exotic background, travel mood",
        ),
        # 11. 꾸안꾸 데일리
        "dailyCasual": (
            "effortless chic daily",
            "effortless chic, oversized fit, comfortable joggers or denim, natural street style, minimal look",
        ),
        # 12. 스포티/애슬레저
        "sporty": (
            "sporty athleisure",
            "sporty athleisure style, high-tech activewear, stylish leggings and hoodie, athletic vibe",
        ),
        # 13. 공항 패션
        "airport": (
            "airport fashion",
            "comfortable airport fashion, layered cozy outfit, sunglasses, travel luggage, chic traveler vibe",
        ),
        # 14. 미니멀/심플
        "minimal": (
            "minimalist simple",
            "minimalist simple aesthetic, neutral color palette, clean lines, minimalist studio background",
        ),
        # 15. 트렌디/스트릿
        "streetTrend": (
            "trendy streetwear",
            "trendy streetwear, graphic t-shirt, hypebeast sneakers, urban city street background",
        ),
        # 레거시 키 호환
        "commute":      ("smart casual commute", "clean minimal smart-casual outfit suitable for commuting"),
        "business":     ("business formal", "sharp tailored suit, polished leather shoes, corporate setting"),
        "meet":         ("social meetup", "polished casual outfit for meeting friends"),
        "weekendTrip":  ("weekend trip", "comfortable layered travel outfit for a weekend trip"),
        "domesticTrip": ("domestic travel", "practical layered outfit for domestic travel"),
        "overseasTrip": ("overseas travel", "versatile travel outfit with practical layering for overseas trip"),
        "partyLook":    ("party look", "trendy party outfit with statement accessories"),
    }

    if k in _MAP:
        return _MAP[k]

    # custom(직접입력): purposeLabel = 사용자가 직접 입력한 텍스트
    pl = (purpose_label or "").strip()
    if pl:
        return (pl, pl)
    return ("everyday", "well-balanced everyday outfit")


def build_prompt(payload: Dict[str, Any]) -> Tuple[str, str]:
    """(prompt, short_explanation)"""
    user = payload.get("user") or {}
    weather = payload.get("weather") or {}
    _is_retry_bp = bool(payload.get("isRetry", False))   # 다시 코디 시 True

    gender = _gender_en(str(user.get("gender", "")))
    age = _korean_to_en_age(str(user.get("ageGroup", "")))
    height = user.get("height")
    weight = user.get("weight")

    temp = weather.get("temp")
    cond = str(weather.get("text", "")).strip()
    bucket = _temp_bucket(temp)

    purpose_key = str(payload.get("purposeKey", "")).strip()
    purpose_label = str(payload.get("purposeLabel", "")).strip()
    purpose_tag, purpose_desc = _purpose_to_style(purpose_key, purpose_label)

    keywords = payload.get("keywords") or []
    if isinstance(keywords, str):
        keywords = [keywords]

    style_title = str(payload.get("styleTitle", "")).strip()
    explanation = str(payload.get("explanation", "")).strip()

    # 코디하기(상의/하의 직접 선택) 전용 모드
    clothing_images = payload.get("clothingImages") or {}
    clothing_urls = payload.get("clothingImageUrls") or {}
    if (str(payload.get("mode") or "").strip() == "codistyle") or clothing_images or clothing_urls or payload.get("imagePrompt"):
        try:
            t_int = int(round(float(temp))) if temp is not None else None
            t_txt = f"{t_int}°" if t_int is not None else ""
        except Exception:
            t_txt = ""
        short = explanation or f"{t_txt} {cond} 날씨에 맞춘 착장 이미지".strip()
        short = short[:100]
        prompt = str(payload.get("imagePrompt") or "").strip()
        # imagePrompt에 이미 custom 요청이 포함됨 (프론트에서 최우선 삽입)
        # 추가 검증: imagePrompt가 없는 경우 payload에서 custom 텍스트 직접 추출
        _custom_req = str(payload.get("customRequest") or payload.get("customText") or "").strip()
        if not prompt:
            prompt = (
                "Create a photorealistic full-body fashion styling image. "
                f"The subject should look like the user: {gender}, age {age}, {height or ''}cm, {weight or ''}kg. "
                "Use the provided reference images for the outfit: one upper-body garment and one lower-body garment. "
                "Preserve the clothing category, color, silhouette and major design details from the references. "
                "If a face reference is provided, preserve the same facial identity. "
                "Show the whole body from head to toe. "
                f"Weather: {bucket}. Condition: {cond or 'clear'}. Purpose: {purpose_desc}. "
                f"Location culture hint: {str(weather.get('location') or payload.get('stylistCity') or '').strip() or 'Unknown'}. "
                "Natural proportions, realistic try-on. "

                # ── 배경 (CRITICAL) ──
                "BACKGROUND (ABSOLUTE MANDATORY): "
                "The background MUST be a SINGLE SOLID FLAT PASTEL COLOR only. "
                "Choose a pastel that CONTRASTS clearly with the outfit: "
                "dark outfit → light pastel (cream, pale mint, soft ivory); "
                "light outfit → slightly deeper pastel (soft lavender, muted peach, pale sage). "
                "Completely uniform and flat from edge to edge — like studio backdrop paper. "
                "FORBIDDEN: rooms, streets, walls, floors, gradients, patterns, objects, environments of any kind. "
                "ONLY ONE FLAT SOLID PASTEL COLOR. No exceptions. "

                # ── 신체비율 (CRITICAL) ──
                "BODY PROPORTION (REALISTIC): Upper body (head to waist) approximately 43-47% of total height. "
                "Lower body (waist to feet) approximately 53-57%. Realistic everyday Korean person — NOT a model. "
                "5:5 or 4:6 ratio is a generation FAILURE. Legs must appear long and naturally proportioned. "

                # ── 바지 길이 ──
                "[PANTS LENGTH — TOP PRIORITY]: Trouser hem must reach BOTTOM 12-15% of image, "
                "covering ankle bone fully. Shoes visible below hem. FORBIDDEN: cropped/7/8/calf-length. "
                + ("RETRY: make pants VISIBLY LONGER — 2025-2026 KR trend is full-length with slight break. " if _is_retry_bp else "") +
                ""

                # ──── [2026-04-10 추가] 바지 핏 = 레귤러핏 기본 ────
                "[PANTS FIT — DEFAULT RULE]: Use REGULAR FIT (straight or slightly tapered) as the default pants silhouette. "
                "FORBIDDEN as default: slim fit, skinny fit, ultra-slim fit, spray-on tight fit. "
                "Slim/skinny fit is ONLY allowed when the user has EXPLICITLY requested it via custom input. "
                "This rule applies to ALL 15 outfit purposes and both genders. No exceptions. "

                # ── 양말 ──
                "SOCKS: Both feet must wear IDENTICAL socks — same color and pattern on both sides. Mismatched socks are FORBIDDEN. "

                # ── 스타일리스트 ──
                "STYLIST RULE: Recommend only real-life wearable outfits. No experimental, runway, fashion-show, or avant-garde styling. "

                "No text, no watermark, no logo."
            )
        else:
            prompt = prompt + " Keep the upper and lower garments faithful to the provided reference images, preserve category, color and silhouette. If face reference exists, preserve facial identity. No text, no watermark."
        style_hint = str(payload.get("styleHint") or "").strip()
        if style_hint:
            prompt += " " + style_hint
        return prompt, short

    # ── custom(직접입력) 텍스트 추출
    # payload.customText: 사용자가 입력한 코디목적 원문
    _custom_text = str(payload.get("customText") or "").strip()
    if not _custom_text:
        import re as _re2
        _cd = str(payload.get("customDirective") or "")
        _m2 = _re2.search(r'["](.*?)["]', _cd)
        if _m2: _custom_text = _m2.group(1).strip()

    # [2026-04-06 수정] _custom_override 변수 정의 (NameError 방지)
    _custom_override = ""
    if _custom_text:
        _custom_override = (
            f"[HIGHEST PRIORITY — USER REQUEST]: The user specifically requested: \"{_custom_text}\". "
            "ALL styling decisions MUST reflect this request. "
        )

    # 프롬프트는 "텍스트 없음" 강제
    # - 브랜드 로고/워터마크/문구 방지
    # - 'full-body'와 'lookbook' 톤으로 안정적인 결과 유도
    profile_bits = []
    if gender in ("male", "female"):
        profile_bits.append(gender)
    if age:
        profile_bits.append(f"{age}")
    if height:
        profile_bits.append(f"{height}cm")
    if weight:
        profile_bits.append(f"{weight}kg")
    profile_str = ", ".join(profile_bits) if profile_bits else "person"

    kw_str = ", ".join([str(k) for k in keywords if str(k).strip()][:6])

    # 온도 버킷에 따른 레이어링 가이드
    if bucket in ("very cold", "cool"):
        weather_rule = "Layer appropriately for cold weather (coat/jacket, warm inner, scarf optional)."
    elif bucket == "hot":
        weather_rule = "Choose breathable lightweight fabrics suitable for hot weather."
    else:
        weather_rule = "Use balanced layering suitable for mild weather."

    # 결과 설명(100자 이내는 프론트에서 추가로 trim 가능)
    short = explanation
    if not short:
        # 한국어 1줄로 간단히
        try:
            t_int = int(round(float(temp)))
            t_txt = f"{t_int}°" if temp is not None else ""
        except Exception:
            t_txt = ""
        short = f"{t_txt} {cond} 날씨에 맞춘 {purpose_label or purpose_tag} 코디 추천".strip()
    short = short[:100]

    # 메인 프롬프트
    prompt = (
        _custom_override +
        "Photorealistic full-body fashion lookbook photo. "
        f"A {profile_str} wearing {(_custom_text or purpose_desc)}. "
        f"Weather: {bucket}. Condition: {cond or 'clear'}. "
        f"Style theme: {_custom_text or purpose_tag}. "
        f"Keywords: {kw_str}. "
        f"{weather_rule} "

        # ── 신체비율 (CRITICAL) ──
        "BODY PROPORTION (CRITICAL — ABSOLUTE RULE): "
        "The upper body (head to waist) must occupy NO MORE than 40% of the total body height. "
        "The lower body (waist to feet) must occupy AT LEAST 60% of the total body height. "
        "This 3:7 head-to-toe ratio is MANDATORY. A 5:5 or 4:6 ratio is FORBIDDEN and considered a generation failure. "
        "Legs must appear long, naturally proportioned, and elongated. "

        # ── 바지 길이 (CRITICAL) ──
        "[PANTS LENGTH — TOP PRIORITY]: Trouser hem must reach BOTTOM 12-15% of image, "
        "covering ankle bone fully. Shoes visible below hem. FORBIDDEN: cropped/7/8/calf-length. "
        + ("RETRY: make pants VISIBLY LONGER — 2025-2026 KR trend is full-length with gentle drape. " if _is_retry_bp else "") +
        ""
        "The trouser hem must be visible just above or touching the top of the shoes. "

        # ──── [2026-04-10 추가] 바지 핏 = 레귤러핏 기본 ────
        "[PANTS FIT — DEFAULT RULE]: Use REGULAR FIT (straight or slightly tapered) as the default pants silhouette. "
        "FORBIDDEN as default: slim fit, skinny fit, ultra-slim fit, spray-on tight fit. "
        "Slim/skinny fit is ONLY allowed when the user has EXPLICITLY requested it via custom input. "
        "This rule applies to ALL outfit purposes and both genders. No exceptions. "

        # ── 양말 (STRICT) ──
        "SOCKS (STRICT): Both left and right socks MUST be IDENTICAL in color and pattern. "
        "Mismatched socks (different colors on each foot) are ABSOLUTELY FORBIDDEN — this is considered an abnormal recommendation. "

        # ── 스타일리스트 철학 ──
        "STYLIST PHILOSOPHY (MANDATORY): You are a practical real-life personal stylist helping everyday people dress well — NOT a fashion designer. "
        "Recommend ONLY outfits that ordinary people would comfortably wear in real daily life. "
        "STRICTLY FORBIDDEN: experimental outfits, fashion show looks, runway aesthetics, avant-garde combinations, asymmetric styling, dramatic oversized silhouettes, unusual color-blocking, or any look that would seem out of place on the street. "
        "All recommendations must be wearable, socially appropriate, and make the person look naturally stylish. "
        "COLOR HARMONY (IMPORTANT): Top and bottom should be in complementary or contrasting tones — avoid making all garments the exact same dark color (all-black, all-purple, all-navy) UNLESS the user specifically requested a monochrome look. "
        "Shoes and accessories should complement rather than perfectly match the main garments. Create natural color variation. "

        # ── 배경 (CRITICAL) ──
        "BACKGROUND (ABSOLUTE MANDATORY — HIGHEST PRIORITY RULE): "
        "The background MUST be a SINGLE SOLID FLAT PASTEL COLOR only. "
        "Choose a pastel color that CONTRASTS clearly with the outfit so the clothing is fully visible: "
        "if the outfit is dark, use light pastel (cream, pale mint, soft ivory, light sky blue); "
        "if the outfit is light/white, use a slightly deeper pastel (soft lavender, muted peach, pale sage). "
        "The background must be completely uniform and flat from edge to edge — like professional studio backdrop paper. "
        "ABSOLUTELY FORBIDDEN: rooms, streets, walls, floors, gradients, patterns, textures, objects, scenery, or any environment. "
        "ONLY ONE FLAT SOLID PASTEL COLOR. No exceptions. "

        "Soft studio lighting, sharp focus. "
        "No text, no watermark, no logo, no brand marks. "
        "High quality outfit details."
    )

    # style_title이 있으면 약하게 힌트로 추가
    if style_title:
        prompt += f" Outfit title: {style_title}."

    return prompt, short


def _is_unknown_param_error(msg: str) -> bool:
    m = (msg or "").lower()
    needles = [
        "unexpected keyword",
        "unknown parameter",
        "extra inputs are not permitted",
        "got an unexpected keyword",
    ]
    return any(n in m for n in needles)


def _is_model_access_error(msg: str) -> bool:
    m = (msg or "").lower()
    if "model" not in m:
        return False
    needles = [
        "does not exist",
        "not found",
        "not available",
        "you don't have access",
        "you do not have access",
        "not permitted",
        "permission",
    ]
    return any(n in m for n in needles)


def _candidate_image_models(primary: str) -> list[str]:
    # 1순위: 설정값
    # 2순위: 안정적인 범용 모델
    # 3순위: 경량 모델
    base = [primary, "gpt-image-1", "gpt-image-1-mini"]
    out: list[str] = []
    for m in base:
        m = str(m or "").strip()
        if m and m not in out:
            out.append(m)
    return out


def _images_generate_compat(
    client: OpenAI,
    *,
    model: str,
    prompt: str,
    size: str,
    quality: str,
    output_format: str,
    output_compression: int,
):
    """SDK/버전 차이로 파라미터가 막힐 때를 대비해 점진적 폴백을 제공합니다."""

    # 1) 최신 파라미터 포함
    try:
        return client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            output_format=output_format,
            output_compression=output_compression,
        )
    except Exception as e:
        msg = str(e)
        if not _is_unknown_param_error(msg):
            raise

        # 2) output_format/output_compression 제거(구버전 SDK 대비)
        return client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
        )


def _images_edit_compat(
    client: OpenAI,
    *,
    model: str,
    image_files: list[io.BytesIO],
    prompt: str,
    size: str,
    quality: str,
    output_format: str,
    output_compression: int,
):
    """얼굴(참조 이미지) 반영: input_fidelity/출력옵션이 SDK 버전에 따라 막히는 경우가 있어 폴백."""

    # 1) 최신: input_fidelity + output_format + output_compression
    try:
        return client.images.edit(
            model=model,
            image=image_files,
            prompt=prompt,
            size=size,
            quality=quality,
            input_fidelity="high",
            output_format=output_format,
            output_compression=output_compression,
        )
    except Exception as e:
        msg = str(e)
        if not _is_unknown_param_error(msg):
            raise

    # 2) input_fidelity만 제거
    try:
        return client.images.edit(
            model=model,
            image=image_files,
            prompt=prompt,
            size=size,
            quality=quality,
            output_format=output_format,
            output_compression=output_compression,
        )
    except Exception as e:
        msg = str(e)
        if not _is_unknown_param_error(msg):
            raise

    # 3) output_format/output_compression도 제거
    return client.images.edit(
        model=model,
        image=image_files,
        prompt=prompt,
        size=size,
        quality=quality,
    )


# ── [2026-04-06] 엔진 진단 — 브라우저에서 /api/engine-status 접속 ──
@app.get("/api/engine-status")
def engine_status():
    """배포 후 브라우저에서 확인: 엔진이 정상 로드됐는지"""
    import os as _os
    _here = _os.path.dirname(_os.path.abspath(__file__))
    # 서버의 실제 파일 내용 일부를 확인 (구버전인지 신버전인지 판별용)
    _engine_first_lines = ""
    try:
        with open(_os.path.join(_here, "stylist_matching_engine.py"), "r") as _ef:
            _engine_first_lines = _ef.read(500)
    except: pass
    _has_old_import = "mock_backend_global_patch" in _engine_first_lines
    _has_new_marker = "v2026-04-06" in _engine_first_lines
    return jsonify(
        version="v2026-04-06",
        engine_loaded=(_STYLIST_ENGINE is not None),
        fashion_db_loaded=bool(_FASHION_DB),
        fashion_db_cities=len(_FASHION_DB.get('city_keywords',{})) if _FASHION_DB else 0,
        stylist_db_loaded=bool(_STYLIST_DB),
        stylist_db_cities=len(_STYLIST_DB) if _STYLIST_DB else 0,
        files={
            "fashion_keywords_db.json": _os.path.exists(_os.path.join(_here,"fashion_keywords_db.json")),
            "stylist_db_server.json": _os.path.exists(_os.path.join(_here,"stylist_db_server.json")),
            "stylist_matching_engine.py": _os.path.exists(_os.path.join(_here,"stylist_matching_engine.py")),
        },
        will_engine_run=bool(_STYLIST_ENGINE and _FASHION_DB and _STYLIST_DB),
        engine_file_is_old=_has_old_import,
        engine_file_is_new=_has_new_marker,
        engine_file_preview=_engine_first_lines[:200],
        engine_import_test=(lambda: (True, "OK") if _STYLIST_ENGINE else (False, "import failed — check Render Logs for error details"))(),
    )


@app.get("/health")
def health():
    return jsonify(
        ok=True,
        ts=_now_ms(),
        python=sys.version.split(" ")[0],
        platform=platform.platform(),
        openai_sdk=_sdk_version(),
        has_openai_key=_safe_bool(os.getenv("OPENAI_API_KEY")),
        has_gemini_key=_safe_bool(os.getenv("GEMINI_API_KEY")),
        codistyle_model=os.getenv("CODISTYLE_GEMINI_MODEL","gemini-2.5-flash-image"),
        # ── AI 기술 상태 ──
        rembg_ready=bool(os.getenv("REMBG_API_URL", "")),  # HF Space URL 설정 여부
        r2_ready=(_get_r2() is not None),
        r2_pub_url=bool(_R2_PUB_URL),
        r2_endpoint=bool(os.getenv("R2_ENDPOINT","") or os.getenv("R2_ACCOUNT_ID","")),
        lykdat_ready=bool(_LYKDAT_KEY),
        fashion_model_ready=(_fashion_model is not None),
        gemini_ready=bool(_GEMINI_KEY),
        models={
            "no_face": os.getenv("CODIBANK_OPENAI_IMAGE_MODEL", "gpt-image-1.5"),
            "with_face": os.getenv("CODIBANK_OPENAI_IMAGE_MODEL_FACE", "gpt-image-1.5"),
        },
        upload_dir=_UPLOAD_DIR,
        legacy_upload_dir=_LEGACY_UPLOAD_DIR,
        upload_count=(len(os.listdir(_UPLOAD_DIR)) if os.path.isdir(_UPLOAD_DIR) else 0),
    )


@app.get("/uploads/<path:filename>")
def serve_upload(filename: str):
    """업로드된 이미지 서빙: 로컬 우선 → 없으면 R2 proxy"""
    from flask import after_this_request, make_response

    @after_this_request
    def _add_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        response.headers["Cache-Control"] = "public, max-age=86400"
        return response

    # ── 1순위: 로컬 파일 확인 (R2 미연동 시 로컬에 저장됨)
    f1 = os.path.join(_UPLOAD_DIR, filename)
    if os.path.exists(f1):
        return send_from_directory(_UPLOAD_DIR, filename)

    f2 = os.path.join(_LEGACY_UPLOAD_DIR, filename)
    if os.path.exists(f2):
        return send_from_directory(_LEGACY_UPLOAD_DIR, filename)

    # ──── [2026-04-11 수정] R2 proxy 방식으로 변경 ────
    # 원인: r2.dev 공개 URL은 CORS 헤더를 보내지 않음 (Cloudflare 제한)
    #       → codistyle.html에서 fetch()로 이미지 가져올 때 CORS 차단
    # 해결: 302 redirect 대신 서버가 R2에서 직접 가져와서 전달 (proxy)
    #       → serve_upload에 이미 CORS 헤더가 있으므로 브라우저 차단 없음
    # 관련파일: codistyle.html(pickDeckItem→fetch), codibank.js(getImageSrc)
    # ────
    if _R2_PUB_URL:
        r2_url = f"{_R2_PUB_URL}/uploads/{filename}"
        try:
            import requests as _rq
            r = _rq.get(r2_url, timeout=10)
            if r.status_code == 200:
                resp = make_response(r.content)
                ct = r.headers.get("Content-Type", "image/jpeg")
                resp.headers["Content-Type"] = ct
                return resp
        except Exception as e:
            print(f"[serve_upload] R2 proxy 실패 ({filename}): {e}")

    return jsonify(ok=False, error="upload not found", filename=filename,
                   r2_configured=bool(_R2_PUB_URL),
                   r2_connected=_get_r2() is not None,
                   local_checked=[_UPLOAD_DIR, _LEGACY_UPLOAD_DIR]), 404


@app.post("/api/storage/upload")
def storage_upload():
    """브라우저에서 촬영/선택한 이미지를 서버에 저장합니다.

    지원 입력
    1) JSON: { dataUrl: "data:image/...;base64,...", slot?: "front|back|brand", email?: "..." }
    2) multipart/form-data: file 필드 + slot(optional)
    """
    img_bytes = b""
    ext = "jpg"

    if request.files and request.files.get("file"):
        f = request.files.get("file")
        raw = f.read() or b""
        if not raw:
            return jsonify(ok=False, error="업로드된 파일이 비어있습니다."), 400
        mime = str(getattr(f, "mimetype", "") or "image/jpeg")
        img_bytes = raw
        ext = _mime_to_ext(mime)
        slot = re.sub(r"[^a-z0-9_-]+", "", str(request.form.get("slot") or "img").lower())[:16] or "img"
    else:
        payload = request.get_json(silent=True) or {}
        # ──── [2026-04-11 수정] image 필드도 fallback 수용 ────
        # 원인: codistyle.html _uploadDeckItem이 {image:dataUrl}로 전송
        # 해결: dataUrl 우선, 없으면 image 필드도 확인
        # 관련파일: codistyle.html (_uploadDeckItem)
        # ────
        data_url = str(payload.get("dataUrl") or payload.get("image") or "").strip()
        if not data_url:
            return jsonify(ok=False, error="dataUrl 또는 file이 필요합니다."), 400
        try:
            mime, img_bytes = _data_url_to_bytes(data_url)
        except Exception:
            return jsonify(ok=False, error="이미지 형식이 올바르지 않습니다(dataUrl)."), 400
        ext = _mime_to_ext(mime)
        slot = re.sub(r"[^a-z0-9_-]+", "", str(payload.get("slot") or "img").lower())[:16] or "img"

    # ── [2026-04-10 수정] 의류 아이템 배경 제거 비활성화 ──
    # 원인: 화이트/밝은 체크패턴 의류에서 rembg가 옷 본체까지 삭제
    # 해결: 원본 이미지를 그대로 저장. Gemini 분석/착장 생성은 원본으로 충분
    # - Gemini analyze-item: 이미 원본(shotBlobUrl) 사용 중 ✅
    # - codistyle generate: 프롬프트에 배경 무시 지시 추가
    # - 코디쌤 styling: 텍스트 프롬프트 기반이라 영향 없음
    # if slot not in ("face", "profile", "avatar"):
    #     _cleaned = remove_clothing_bg(img_bytes)
    #     if _cleaned is not img_bytes:
    #         img_bytes = _cleaned
    #         ext = "png"

    fname = f"{slot}_{_now_ms()}_{os.urandom(3).hex()}.{ext}"
    try:
        rel = _write_upload_bytes(slot, ext, img_bytes, fixed_name=fname)
    except Exception as e:
        return jsonify(ok=False, error=f"서버 저장 실패: {e}"), 500

    base = _public_base()
    return jsonify(ok=True, path=rel, url=f"{base}{rel}")


@app.post("/api/link/resolve-image")
def link_resolve_image():
    payload = request.get_json(silent=True) or {}
    url = str(payload.get("url") or "").strip()
    if not url.startswith(("http://", "https://")):
        return jsonify(ok=False, error="http:// 또는 https://로 시작하는 URL을 입력해주세요."), 400
    try:
        img_url, label = _resolve_representative_image(url)
        mime, img_bytes = _download_remote_image(img_url)
        ext = _mime_to_ext(mime)
        rel = _write_upload_bytes("link", ext, img_bytes)
        base = _public_base()
        return jsonify(ok=True, label=label, sourceUrl=url, resolvedImageUrl=img_url, path=rel, url=f"{base}{rel}")
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 400


@app.get("/api/link/resolve-image")
def link_resolve_image_get():
    url = str(request.args.get("url") or "").strip()
    if not url:
        return jsonify(ok=False, error="url 파라미터가 필요합니다."), 400
    request._cached_json = {"url": url}  # type: ignore[attr-defined]
    return link_resolve_image()


@app.get("/api/ai/diagnose")
def ai_diagnose():
    """OpenAI 연결/권한/SDK 버전 문제를 초보자도 바로 확인할 수 있도록 만든 진단 API.

    - 비용이 드는 이미지 생성은 하지 않습니다.
    - 모델 목록 호출로 "키가 유효한지"만 확인합니다(조직/권한/요금 문제면 여기서도 에러가 납니다).
    """

    if not os.getenv("OPENAI_API_KEY"):
        return (
            jsonify(
                ok=False,
                error=(
                    "OPENAI_API_KEY가 비어있습니다. "
                    "server/.env 또는 환경변수에 OPENAI_API_KEY를 설정한 뒤 서버를 재시작해주세요."
                ),
            ),
            400,
        )

    client = get_client()
    try:
        # models.list는 과금이 발생하지 않는 호출이며, 키/조직/권한 문제를 빠르게 진단하는 데 유용합니다.
        models = client.models.list()
        ids = []
        for m in getattr(models, "data", [])[:10]:
            mid = getattr(m, "id", None)
            if mid:
                ids.append(str(mid))
        return jsonify(
            ok=True,
            openai_sdk=_sdk_version(),
            sample_model_ids=ids,
            hint=(
                "ok=true면 프록시 서버에서 OpenAI 인증까지는 정상입니다. "
                "이미지 생성이 실패한다면 모델/파라미터/요금(빌링) 문제일 가능성이 높습니다."
            ),
        )
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


def _ai_styling_via_gemini(
    payload: Dict[str, Any],
    prompt: str,
    short: str,
    ref_images: list[tuple[str, str, bytes]],
    cache_fname: str,
    ext: str,
    matched_stylist=None,
    meta=None,
    lang=None,
):
    """[2026-04-10] 코디쌤 추천코디 — Gemini 단일 호출로 이미지+분석 동시 생성.

    OpenAI 대비 장점:
    - 1회 호출로 이미지 + 분석 JSON + 키워드 동시 생성 (병렬 호출 불필요)
    - 얼굴 이미지 reference 지원 (멀티모달 입력)
    - 한국어 분석 텍스트 품질 우수
    - 응답 시간 단축 + 비용 절감

    응답 구조:
    - image_bytes (inline_data)
    - text 파트에서 <<<ANALYSIS_JSON>>>...<<<END>>> 마커로 감싼 JSON 추출
    """
    _cs_en = (str(lang or payload.get("lang") or "ko").strip().lower() == "en")
    # ── SDK 감지: google-genai(신) 우선 → google-generativeai(구) 폴백 ──
    _SDK = None
    _genai = None
    _gtypes = None
    _genai_old = None

    try:
        from google import genai as _genai_mod
        from google.genai import types as _gtypes_mod
        _genai = _genai_mod
        _gtypes = _gtypes_mod
        _SDK = "new"
    except ImportError:
        pass

    if not _SDK:
        try:
            import google.generativeai as _genai_old_mod
            _genai_old = _genai_old_mod
            _SDK = "old"
        except ImportError:
            return jsonify(ok=False, error="Gemini SDK 미설치. google-genai 또는 google-generativeai 필요"), 500

    # ── 사용자 정보 추출 ──
    user_info = payload.get("user") or {}
    # ──── [2026-04-10 수정] 성별 정규화 통합 적용 ────
    gender = _normalize_gender_code(str(user_info.get("gender", "")))
    gender_en = "woman" if gender == "F" else "man"
    gender_ko = "여성" if gender == "F" else "남성"
    age = str(user_info.get("ageGroup", "30대")).strip()
    height = str(user_info.get("height", "")).strip()
    weight = str(user_info.get("weight", "")).strip()
    hw_ko = f"키 {height}cm, 몸무게 {weight}kg" if height and weight else ""

    # 퍼스널컬러
    personal_color = payload.get("personalColor") or {}
    pc_season    = str(personal_color.get("season", "") or "").strip()
    pc_undertone = str(personal_color.get("undertone", "") or "").strip()
    pc_subtype   = str(personal_color.get("subtype") or personal_color.get("type") or "").strip()
    pc_best      = personal_color.get("best_colors") or []
    pc_avoid     = personal_color.get("avoid_colors") or []
    if not isinstance(pc_best, list): pc_best = []
    if not isinstance(pc_avoid, list): pc_avoid = []
    pc_label = (pc_season + " " + pc_subtype).strip() or pc_season or "미등록"
    pc_best_str  = ", ".join(pc_best[:5]) if pc_best else "범용 뉴트럴"
    pc_avoid_str = ", ".join(pc_avoid[:3]) if pc_avoid else "탁한 톤"

    # 체형
    body_type_key = str(user_info.get("bodyType", "")).strip()
    try:
        h_int = int(height) if height else 170
        w_int = int(weight) if weight else 65
    except Exception:
        h_int, w_int = 170, 65
    bmi = round(w_int / ((h_int/100) ** 2), 1) if h_int >= 100 else 0
    if bmi < 18.5:
        bmi_cat_ko = "마른 체형"
    elif bmi < 23:
        bmi_cat_ko = "표준 체형"
    elif bmi < 25:
        bmi_cat_ko = "약간 통통"
    else:
        bmi_cat_ko = "통통한 체형"

    # 목적/날씨/도시
    weather = payload.get("weather") or {}
    try:
        temp = float(weather.get("temp") or 20)
    except Exception:
        temp = 20.0
    cond = str(weather.get("text") or weather.get("condition") or "").strip()
    location = str(weather.get("location") or weather.get("city") or "").strip()
    purpose_label = str(payload.get("purposeLabel") or "").strip()
    custom_text = str(payload.get("customText") or "").strip()
    purpose_key = str(payload.get("purposeKey") or "").strip().lower()
    is_custom = (purpose_key == "custom" and bool(custom_text))
    purpose_for_analysis = custom_text if is_custom else (purpose_label or "데일리 코디")

    stylist_city = (meta or {}).get("active_city", "") if meta else ""
    stylist_name = (matched_stylist or {}).get("name", "") if matched_stylist else ""

    # ── Gemini 통합 프롬프트 (이미지 생성 + 분석 JSON 동시) ──
    # 핵심: response_modalities=["IMAGE","TEXT"] 활용해 한 번의 호출로 두 출력 동시 획득
    custom_directive = ""
    if is_custom:
        custom_directive = (
            f"\n\n========================================\n"
            f"⚠️ ABSOLUTE HIGHEST PRIORITY — USER DIRECT REQUEST ⚠️\n"
            f"The user explicitly typed: \"{custom_text}\"\n"
            f"You MUST generate the outfit to EXACTLY match this request.\n"
            f"This OVERRIDES all city/purpose templates below.\n"
            f"========================================\n\n"
        )

    gemini_prompt = (
        custom_directive + prompt + " "
        # ── 얼굴 보존 ── [2026-04-19 FACE] 재현 정확도 강화
        "IDENTITY PRESERVATION — HIGHEST PRIORITY: "
        "If a face reference image is provided, the FIRST image is that face. "
        "Match EXACTLY the following facial features from the reference: "
        "face shape and jawline contour, eye shape/size/angle, double-eyelid presence and depth, "
        "eyebrow thickness and arch, nose bridge width and tip shape, "
        "lip shape and thickness, philtrum length, cheekbone prominence, "
        "skin tone and undertone, hair color/texture/length/parting line, "
        "and any distinguishing features (moles, freckles, dimples, scars). "
        "DO NOT beautify, smooth, slim, or idealize the face. "
        "DO NOT alter proportions or make the person look younger/older. "
        "Generate as if THIS EXACT PERSON — unchanged — is wearing the outfit. "
        "The generated face must be instantly recognizable as the same individual in the reference. "

        # ── 신체 프로필 ── [2026-04-19 BODY] BMI + 체형 특성을 이미지 생성 단계에 주입 (C안)
        # 이전: "Subject: Korean man, 30대, 키 175cm, 몸무게 70kg" 단순 문자열만
        # 수정: _build_body_profile_block으로 BMI 분류 + 체형별 do_style/dont_style 직접 지시
        "\n\n" + _build_body_profile_block(gender, age, height, weight, body_type_key, "en") + "\n\n"
        "Full body head to toe visible. Photorealistic fashion editorial. "

        # ── 배경 ──
        "BACKGROUND (ABSOLUTE MANDATORY): SINGLE SOLID FLAT PASTEL COLOR ONLY. "
        "Choose a pastel that CONTRASTS with the outfit. "
        "Completely uniform from edge to edge — studio backdrop paper style. "
        "ABSOLUTELY FORBIDDEN: rooms, streets, walls, gradients, patterns, objects, environments. "

        # ── 신체비율 ──
        "BODY PROPORTION: Upper body 43-47%, lower body 53-57%. Realistic everyday Korean person. "
        "Full body visible head to shoes. "

        # ── 바지/양말 ──
        "PANTS: Full ankle-length only. Hem just above the shoe. Cropped/7-8 length FORBIDDEN. "
        "SOCKS: Both feet IDENTICAL — same color and pattern. Mismatched FORBIDDEN. "

        # ── 스타일리스트 룰 ──
        "STYLIST RULE: Everyday practical styling only. No experimental, runway, or avant-garde. "
        "All looks must be wearable in real Korean daily life. "

        # ══════════════════════════════════════════
        # 분석 JSON 출력 지시 — 핵심
        # ══════════════════════════════════════════
        "\n\n=== CRITICAL OUTPUT INSTRUCTIONS ===\n"
        "Along with the generated outfit image, you MUST also output a structured " + ("English" if _cs_en else "Korean") + " analysis as TEXT. "
        "Wrap the JSON between exact markers <<<ANALYSIS_JSON>>> and <<<END_ANALYSIS>>> with no additional text outside markers. "
        "The JSON MUST follow this EXACT schema:\n"
        "{\n"
        '  "personalColor": {\n'
        '    "text": "퍼스널컬러 측면 분석 (정확히 ' + ('English' if _cs_en else '한국어') + ', 250-300자, 사용자 톤에 맞는 컬러 추천 이유와 오늘 코디의 컬러 선택 근거 포함)",\n'
        '    "keywords": ["키워드1", "키워드2", "키워드3"]\n'
        '  },\n'
        '  "body": {\n'
        '    "text": "체형/사이즈 측면 분석 (' + ('English' if _cs_en else '한국어') + ', 250-300자, 키/체중/BMI/체형분류를 반영한 핏과 실루엣 추천 근거)",\n'
        '    "keywords": ["키워드1", "키워드2", "키워드3"]\n'
        '  },\n'
        '  "purpose": {\n'
        '    "text": "코디 목적과 날씨 측면 분석 (' + ("English" if _cs_en else "한국어") + ', 250-300자, 목적/날씨/도시 스타일을 어떻게 반영했는지 설명)",\n'
        '    "keywords": ["키워드1", "키워드2", "키워드3"]\n'
        '  },\n'
        '  "categoryKeywords": {\n'
        '    "outer": "아우터 컬러+디자인 (예: 베이지 트렌치코트, 클래식 라펠)",\n'
        '    "top": "상의 컬러+디자인",\n'
        '    "bottom": "하의 컬러+디자인",\n'
        '    "shoes": "신발 컬러+디자인",\n'
        '    "bag": "가방 컬러+디자인",\n'
        '    "scarf": "스카프/포인트 (없으면 빈 문자열)",\n'
        '    "watch": "시계 (없으면 빈 문자열)",\n'
        '    "socks": "양말 컬러"\n'
        '  }\n'
        "}\n"
        "RULES:\n"
        "1. Each text field MUST be 250-300 Korean characters (not more, not less significantly).\n"
        "2. Each keywords array MUST contain EXACTLY 3 short Korean keywords (2-6 chars each).\n"
        "3. categoryKeywords values must reflect the EXACT colors and styles in the generated image.\n"
        "4. If a category is not in the outfit, use empty string \"\".\n"
        "5. Output ONLY the image AND the marked JSON. Nothing else.\n"
        "\n[USER CONTEXT FOR ANALYSIS]\n"
        f"- 성별: {gender_ko}, 나이: {age}\n"
        f"- 신체: 키 {h_int}cm, 몸무게 {w_int}kg (BMI {bmi}, {bmi_cat_ko})\n"
        f"- 체형 분류: {body_type_key or '미등록'}\n"
        f"- 퍼스널컬러: {pc_label} ({pc_undertone or '복합'})\n"
        f"  베스트: {pc_best_str}\n"
        f"  주의: {pc_avoid_str}\n"
        f"- 코디 목적: {purpose_for_analysis}\n"
        f"- 날씨: {int(temp)}°C {cond}\n"
        f"- 위치: {location or '미지정'}\n"
        f"- 매칭 스타일리스트: {stylist_name or '범용'} ({stylist_city or '범용 도시'})\n"
        + (f"- 사용자 직접 요청: \"{custom_text}\"\n" if is_custom else "")
    )

    # ── 이미지 파트 구성: 얼굴 → 상의 → 하의 순서 ──
    face_parts = [(mime, raw) for label, mime, raw in ref_images if label == "face"]
    top_parts = [(mime, raw) for label, mime, raw in ref_images if label == "top"]
    bottom_parts = [(mime, raw) for label, mime, raw in ref_images if label == "bottom"]
    ordered_parts = face_parts + top_parts + bottom_parts

    model_name = _CODISTYLE_MODEL

    try:
        if _SDK == "new":
            contents = [gemini_prompt]
            for mime, raw in ordered_parts:
                contents.append(_gtypes.Part.from_bytes(data=raw, mime_type=mime or "image/jpeg"))

            client = _genai.Client(api_key=_GEMINI_KEY)
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=_gtypes.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    temperature=0.7,
                ),
            )
        else:
            from PIL import Image as _PILImage
            _genai_old.configure(api_key=_GEMINI_KEY)
            model = _genai_old.GenerativeModel(model_name)

            contents_old = [gemini_prompt]
            for mime, raw in ordered_parts:
                contents_old.append(_PILImage.open(io.BytesIO(raw)))

            try:
                response = model.generate_content(
                    contents_old,
                    generation_config={"response_modalities": ["IMAGE", "TEXT"], "temperature": 0.7},
                )
            except TypeError:
                response = model.generate_content(
                    contents_old,
                    generation_config=_genai_old.GenerationConfig(temperature=0.7),
                )
    except Exception as e:
        import traceback as _tb
        _trace = _tb.format_exc()[-400:]
        print(f"[ai_styling_gemini] Gemini 호출 실패: {_trace}")
        return jsonify(ok=False, error=f"Gemini 호출 실패 ({_SDK}): {str(e)[:300]}", trace=_trace), 500

    # ── 응답에서 이미지 + 텍스트 추출 ──
    img_bytes = None
    full_text = ""
    try:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                img_bytes = part.inline_data.data
            elif part.text:
                full_text += part.text
    except (IndexError, AttributeError) as e:
        return jsonify(ok=False, error=f"응답 파싱 실패: {str(e)[:200]}"), 500

    if not img_bytes:
        try:
            finish = response.candidates[0].finish_reason
        except Exception:
            finish = "UNKNOWN"
        print(f"[ai_styling_gemini] 이미지 미생성: finishReason={finish}, text={full_text[:150]}")
        return jsonify(ok=False, error=f"이미지 미생성 finishReason={finish}"), 500

    if isinstance(img_bytes, str):
        img_bytes = base64.b64decode(img_bytes)

    # ── 분석 JSON 파싱 (마커 기반 + 폴백) ──
    styling_analysis = None
    category_keywords_from_ai = {}
    try:
        import re as _re_a, json as _json_a
        _m = _re_a.search(r'<<<ANALYSIS_JSON>>>(.*?)<<<END_ANALYSIS>>>', full_text, _re_a.DOTALL)
        if _m:
            _json_str = _m.group(1).strip()
            # JSON 안의 코드펜스 제거
            _json_str = _re_a.sub(r'^```(?:json)?\s*|\s*```$', '', _json_str, flags=_re_a.MULTILINE).strip()
            _parsed = _json_a.loads(_json_str)
            # 스키마 검증 + 정규화
            styling_analysis = {}
            for sec in ("personalColor", "body", "purpose"):
                _s = _parsed.get(sec) or {}
                _txt = str(_s.get("text") or "").strip()[:300]
                _kws = _s.get("keywords") or []
                if not isinstance(_kws, list):
                    _kws = []
                _kws = [str(k).strip() for k in _kws if str(k).strip()][:3]
                while len(_kws) < 3:
                    _kws.append("—")
                styling_analysis[sec] = {"text": _txt, "keywords": _kws}
            # 카테고리별 키워드 (옷장 매칭용)
            _ck = _parsed.get("categoryKeywords") or {}
            if isinstance(_ck, dict):
                category_keywords_from_ai = {str(k): str(v).strip() for k, v in _ck.items() if v}
        else:
            # 마커 없으면 폴백 — 템플릿 함수로 생성
            styling_analysis = _generate_styling_analysis(payload, matched_stylist, meta, lang=str(payload.get("lang") or "ko"))
            print(f"[ai_styling_gemini] ⚠ 분석 JSON 마커 없음, 템플릿 폴백 사용. text 일부: {full_text[:200]}")
    except Exception as _pe:
        print(f"[ai_styling_gemini] 분석 JSON 파싱 실패: {_pe}, 템플릿 폴백 사용")
        try:
            styling_analysis = _generate_styling_analysis(payload, matched_stylist, meta, lang=str(payload.get("lang") or "ko"))
        except Exception:
            styling_analysis = None

    rel = _write_upload_bytes("ai", ext, img_bytes, fixed_name=cache_fname)
    base = _public_base()

    # 카테고리 키워드 병합: AI가 준 것 우선, 엔진 기본값 보조
    merged_cat_kws = {}
    try:
        merged_cat_kws.update((meta or {}).get('categoryKeywords', {}) or {})
    except Exception:
        pass
    merged_cat_kws.update(category_keywords_from_ai or {})

    return jsonify(
        ok=True,
        image=f"{base}{rel}",
        path=rel,
        url=f"{base}{rel}",
        explanation=short or "AI 코디 이미지 생성 완료!",
        model=f"gemini:{model_name}",
        cached=False,
        prompt=gemini_prompt if os.getenv("CODIBANK_DEBUG_PROMPT") == "1" else None,
        stylist=matched_stylist,
        stylingStory=(meta or {}).get("styling_story") if meta else None,
        engineKeywords=(meta or {}).get('keywords_selected', []) if meta else [],
        engineCategoryKeywords=merged_cat_kws,
        engineCity=(meta or {}).get('active_city', '') if meta else '',
        enginePurpose=(meta or {}).get('purpose', '') if meta else '',
        engineBottomType=(meta or {}).get('bottom_type', '') if meta else '',
        # [2026-04-10] AI 종합 분석 (Gemini 단일 호출 결과)
        stylingAnalysis=styling_analysis,
    )


# ══════════════════════════════════════════════════════
# [2026-04-10] AI 패션 스타일리스트 종합 분석 생성기
# - 퍼스널컬러 / 체형·사이즈 / 코디목적·날씨 3개 측면
# - 각 측면 분석 텍스트 300자 이내 + 핵심 키워드 3개
# - closet.html의 새 분석 박스에서 렌더링
# ══════════════════════════════════════════════════════
def _generate_styling_analysis(payload, matched_stylist, meta, lang=None):
    """3개 측면 종합 분석 + 각 3개 키워드 생성 (템플릿 기반, API 호출 없음)"""
    # [2026-04-19 BUGFIX #2] _en 변수 누락 → NameError → 이 함수 호출 시마다 예외 발생
    # 영향: 캐시 히트 / Gemini 분석 JSON 파싱 실패 / OpenAI 폴백 3곳에서 모두 터짐
    _en = (str(lang or payload.get("lang") or "ko").strip().lower() == "en")
    user      = payload.get("user") or {}
    weather   = payload.get("weather") or {}
    pc        = payload.get("personalColor") or {}
    purpose   = (meta or {}).get("purpose") or payload.get("purposeLabel") or "데일리 코디"
    city      = (meta or {}).get("active_city") or "서울"
    custom_text = str(payload.get("customText") or "").strip()
    if custom_text and (payload.get("purposeKey") or "").lower() == "custom":
        purpose = custom_text

    # ── 사용자 정보 정규화 ──
    # ──── [2026-04-10 수정] 성별 정규화 통합 적용 ────
    gender   = _normalize_gender_code(str(user.get("gender") or ""))
    gender_ko = "여성" if gender == "F" else "남성"
    age      = str(user.get("ageGroup") or "30대")
    try:
        height = int(user.get("height") or 170)
    except Exception:
        height = 170
    try:
        weight = int(user.get("weight") or 65)
    except Exception:
        weight = 65
    body_type = str(user.get("bodyType") or "").strip()
    bmi_val = round(weight / ((height/100) ** 2), 1) if height >= 100 else 0
    if bmi_val < 18.5:
        bmi_cat_ko, bmi_cat_en = "마른 체형", "slim"
    elif bmi_val < 23:
        bmi_cat_ko, bmi_cat_en = "표준 체형", "average"
    elif bmi_val < 25:
        bmi_cat_ko, bmi_cat_en = "약간 통통", "slightly heavy"
    else:
        bmi_cat_ko, bmi_cat_en = "통통한 체형", "heavier"

    # ── 1) 퍼스널컬러 분석 ──
    pc_season    = str(pc.get("season") or "").strip()
    pc_subtype   = str(pc.get("subtype") or pc.get("type") or "").strip()
    pc_undertone = str(pc.get("undertone") or "").strip()
    pc_best      = pc.get("best_colors") or []
    pc_avoid     = pc.get("avoid_colors") or []
    if not isinstance(pc_best, list): pc_best = []
    if not isinstance(pc_avoid, list): pc_avoid = []

    if pc_season or pc_subtype:
        pc_label = f"{pc_season} {pc_subtype}".strip()
        best_str = ", ".join(pc_best[:5]) if pc_best else "고객님 톤에 맞는 컬러"
        avoid_str = ", ".join(pc_avoid[:3]) if pc_avoid else "탁한 톤"
        pc_text = (
            f"{gender_ko}님의 퍼스널컬러는 {pc_label}({pc_undertone or '복합 톤'})입니다. "
            f"이 톤에는 {best_str} 같은 컬러가 피부톤을 환하게 살려줍니다. "
            f"반대로 {avoid_str}는 인상을 가라앉힐 수 있어 포인트로만 활용하는 것이 좋아요. "
            f"오늘 코디는 베스트 컬러 중심으로 메인을 잡고, 액세서리는 톤온톤으로 정돈했습니다."
        )
        # [2026-04-11] 350자 이내 + 마지막 문장 완결
        if len(pc_text) > 350:
            _cut = pc_text[:350].rfind(".")
            pc_text = pc_text[:_cut+1] if _cut > 100 else pc_text[:347] + "..."
        pc_keywords = [pc_label or pc_season] + (pc_best[:2] if pc_best else ["컬러 매칭", "톤온톤"])
        pc_keywords = [k for k in pc_keywords if k][:3]
        while len(pc_keywords) < 3:
            pc_keywords.append("컬러 매칭")
    else:
        if _en:
            pc_text = (
                "Your personal color hasn't been registered, so a universal color guide is applied. "
                "Today's outfit uses a neutral base with restrained accent colors that complement most skin tones. "
                "Register your personal color in My Page for more precise color matching."
            )
            pc_keywords = ["Neutral", "Tone-on-tone", "Subtle accent"]
        else:
            pc_text = (
                f"{gender_ko}님의 퍼스널컬러 정보가 등록되지 않아 범용 컬러 가이드를 적용합니다. "
                f"오늘 코디는 피부톤과 잘 어우러지는 뉴트럴 베이스에 절제된 포인트 컬러로 구성했어요. "
                f"마이페이지에서 퍼스널컬러를 등록하면 훨씬 정확한 컬러 매칭을 받으실 수 있습니다."
            )
            pc_keywords = ["뉴트럴", "톤온톤", "절제된 포인트"]
        if len(pc_text) > 350:
            _cut = pc_text[:350].rfind(".")
            pc_text = pc_text[:_cut+1] if _cut > 100 else pc_text[:347] + "..."

    # ── 2) 체형/사이즈 분석 ──
    if _en:
        body_text_parts = [f"{gender_ko}, {age}, {height}cm, {weight}kg ({bmi_cat_en}, BMI {bmi_val}). "]
    else:
        body_text_parts = [f"{gender_ko}, {age}, 키 {height}cm, 몸무게 {weight}kg ({bmi_cat_ko}, BMI {bmi_val})입니다. "]
    if bmi_cat_en == "slim":
        if _en:
            body_text_parts.append("A slim build benefits from layering and voluminous fabrics for added fullness. ")
            body_kws = ["Layered", "Volume silhouette", "Semi-overfit"]
        else:
            body_text_parts.append("슬림한 체형은 레이어드와 볼륨감 있는 소재로 풍성함을 더할 수 있습니다. ")
            body_kws = ["레이어드", "볼륨 실루엣", "세미오버핏"]
    elif bmi_cat_en == "average":
        if _en:
            body_text_parts.append("A standard build suits most fits — regular and tailored fits work best. ")
            body_kws = ["Regular fit", "Tailored", "Classic fit"]
        else:
            body_text_parts.append("표준 체형은 대부분의 핏을 소화할 수 있어 레귤러핏과 테일러드핏이 가장 잘 어울립니다. ")
            body_kws = ["레귤러핏", "테일러드", "정석 핏"]
    elif bmi_cat_en == "slightly heavy":
        if _en:
            body_text_parts.append("A slightly heavy build benefits from structured jackets and vertical-line silhouettes. ")
            body_kws = ["Structured jacket", "Vertical line", "Shoulder emphasis"]
        else:
            body_text_parts.append("약간 통통한 체형은 어깨 라인을 살리는 구조적 자켓과 세로 라인을 강조하는 실루엣이 효과적입니다. ")
            body_kws = ["구조적 자켓", "세로 라인", "어깨 강조"]
    else:
        if _en:
            body_text_parts.append("For a heavier build, clean straight lines work better than curved silhouettes. ")
            body_kws = ["Straight silhouette", "Dark tone", "Structured fit"]
        else:
            body_text_parts.append("볼륨감 있는 체형은 몸을 감싸는 곡선 실루엣 대신 직선적이고 깔끔한 라인이 인상을 정돈해줍니다. ")
            body_kws = ["직선 실루엣", "다크 톤", "구조적 핏"]
    if body_type:
        body_text_parts.append(f"{'Proportion-correcting details applied for body type: ' if _en else '체형 분류('}{body_type}{').' if _en else ')에 맞춰 비율을 보정하는 디테일을 우선 적용했습니다. '}")
    body_text_parts.append(f"{'Today outfit uses the best length and fit for ' if _en else '오늘 코디는 '}{height}cm{' build.' if _en else ' 기준으로 비율이 가장 좋아 보이는 길이감과 핏을 선택했습니다.'}")
    body_text = "".join(body_text_parts)
    if len(body_text) > 350:
        _cut = body_text[:350].rfind(".")
        body_text = body_text[:_cut+1] if _cut > 100 else body_text[:347] + "..."

    # ── 3) 코디목적 + 날씨 분석 ──
    try:
        temp = float(weather.get("temp") or 20)
    except Exception:
        temp = 20.0
    cond = str(weather.get("text") or weather.get("condition") or "").strip()
    location = str(weather.get("location") or weather.get("city") or "").strip()
    if temp <= 5:
        weather_kw = "Winter warm" if _en else "방한"
        weather_desc = f"At {int(temp)}°C, it's cold. A thick coat and warm layers are essential. " if _en else f"기온 {int(temp)}°C로 춥습니다. 두꺼운 코트와 보온 레이어가 필수입니다. "
    elif temp <= 12:
        weather_kw = "Fall layer" if _en else "가을 레이어"
        weather_desc = f"At {int(temp)}°C, it's chilly. Jacket and knit layers keep you warm. " if _en else f"기온 {int(temp)}°C로 쌀쌀합니다. 자켓과 니트 레이어로 따뜻함을 챙겼어요. "
    elif temp <= 20:
        weather_kw = "Transitional" if _en else "환절기"
        weather_desc = f"At {int(temp)}°C, great for activities. A light outer layer handles temperature changes. " if _en else f"기온 {int(temp)}°C로 활동하기 좋은 환절기 날씨입니다. 가벼운 아우터로 체온 조절이 가능합니다. "
    elif temp <= 26:
        weather_kw = "Spring/Fall" if _en else "봄가을"
        weather_desc = f"At {int(temp)}°C, pleasant weather. A single layer finishes the look cleanly. " if _en else f"기온 {int(temp)}°C로 쾌적합니다. 단일 레이어로 깔끔하게 마무리했습니다. "
    else:
        weather_kw = "Summer breathable" if _en else "여름 통풍"
        weather_desc = f"At {int(temp)}°C, it's hot. Lightweight breathable fabrics prioritize coolness. " if _en else f"기온 {int(temp)}°C로 덥습니다. 통기성 좋은 가벼운 소재로 시원함을 우선했습니다. "
    stylist_name = (matched_stylist or {}).get("name") if matched_stylist else None
    if _en:
        purpose_desc = f"Today's goal is '{purpose}'. "
        city_desc = f"Based on {city} style, "
        stylist_part = f"with AI stylist {stylist_name}'s touch, " if stylist_name else ""
        purpose_text = (
            purpose_desc + weather_desc + city_desc + stylist_part +
            f"key items for '{purpose}' are curated."
        )
    else:
        purpose_desc = f"오늘의 목적은 '{purpose}'입니다. "
        city_desc = f"{city} 스타일을 기반으로 "
        stylist_part = f"AI 스타일리스트 {stylist_name}님의 감각으로 " if stylist_name else ""
        purpose_text = (
            purpose_desc + weather_desc + city_desc + stylist_part +
            f"{purpose}에 어울리는 핵심 아이템을 조합했습니다."
        )
    if len(purpose_text) > 350:
        _cut = purpose_text[:350].rfind(".")
        purpose_text = purpose_text[:_cut+1] if _cut > 100 else purpose_text[:347] + "..."
    purpose_kws = [purpose, weather_kw, city + (" style" if _en else " 스타일")]

    return {
        "personalColor": {"text": pc_text, "keywords": pc_keywords},
        "body":          {"text": body_text, "keywords": body_kws},
        "purpose":       {"text": purpose_text, "keywords": purpose_kws},
    }


@app.post("/api/ai/styling")
def ai_styling():
    # ══════════════════════════════════════════════════════
    # 코디쌤 AI 코디 추천: 항상 OpenAI API 전용
    # 코디하기 착장 이미지: /api/codistyle/generate (Gemini 전용)
    # 두 API를 혼용하거나 임의 전환하지 않음
    # ══════════════════════════════════════════════════════
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    if not has_openai:
        return jsonify(
            ok=False,
            error="OPENAI_API_KEY가 설정되지 않았습니다. 코디쌤 AI 코디는 OpenAI API가 필요합니다.",
        ), 400

    payload = request.get_json(silent=True) or {}

    # [v2026-04-06] 9,600명 AI 스타일리스트 엔진 — 프론트 프롬프트 완전 대체
    # 구: closet.html(코디쌤) PERSONA_DB → imagePrompt → 서버 통과 → OpenAI (목적 차별화 불가)
    # 신: 서버 엔진이 목적+도시 기반 전용 프롬프트 생성 → OpenAI (16개 목적 완전 차별화)
    _matched_stylist = None
    _styling_story = ""
    _engine_active = False
    _meta = {}
    prompt = ""
    short = ""

    if _STYLIST_ENGINE and _FASHION_DB and _STYLIST_DB:
        try:
            _result = _STYLIST_ENGINE(payload, _FASHION_DB, _STYLIST_DB)
            _eng_prompt = _result[0]
            _styling_story = _result[1] or ""
            _matched_stylist = _result[3]
            _injection = _result[4] if len(_result) > 4 else ""
            _meta = _result[5] if len(_result) > 5 else {}

            if _eng_prompt and len(_eng_prompt) > 100:
                prompt = _eng_prompt
                _engine_active = True
                if _injection:
                    prompt = _injection + "\n" + prompt
                _front_colors = str(payload.get("colorDirective", "")).strip()
                if _front_colors:
                    prompt += f"\nCOLOR HINT: {_front_colors}. "
                _city = _meta.get('active_city', '?')
                _purpose = _meta.get('purpose', '?')
                _kws = _meta.get('keywords_selected', [])
                short = f"{_purpose} 코디 — {_city} 스타일"
                print(f"[v2026-04-06 엔진 ✅] 도시={_city}, 목적={_purpose}, "
                      f"스타일리스트={_matched_stylist.get('name','?') if _matched_stylist else '?'}, "
                      f"키워드={','.join(_kws[:3])}")
        except Exception as _se:
            print(f"[엔진 오류]: {_se}")
            import traceback; traceback.print_exc()

    if not _engine_active:
        prompt, short = build_prompt(payload)
        # [2026-04-06] fallback 원인 진단
        _why = []
        if not _STYLIST_ENGINE: _why.append("엔진 미로드(stylist_matching_engine.py 없음)")
        if not _FASHION_DB: _why.append("fashion_keywords_db.json 없음/비어있음")
        if not _STYLIST_DB: _why.append("stylist_db_server.json 없음/비어있음")
        print(f"[v2026-04-06 ⚠️ fallback] 원인: {', '.join(_why) if _why else '엔진 런타임 에러'}")

    # ──── [2026-04-10] 직접입력 강제 처리 ────
    # 원인: 엔진이 customText를 무시하고 도시/목적 기반 프롬프트만 생성
    # 해결: customText가 있으면 엔진 결과의 맨 앞과 맨 뒤 모두에 강력한 오버라이드 prepend/append
    _purpose_key = str(payload.get("purposeKey", "")).strip().lower()
    _custom_text_force = str(payload.get("customText") or "").strip()
    if _purpose_key == "custom" and _custom_text_force:
        _force_header = (
            f"\n\n========================================\n"
            f"[ABSOLUTE HIGHEST PRIORITY — USER DIRECT REQUEST]\n"
            f"The user explicitly typed this exact request: \"{_custom_text_force}\"\n"
            f"You MUST generate an outfit that EXACTLY matches this request.\n"
            f"This direct user input OVERRIDES all other styling rules, city styles, "
            f"purpose templates, and stylist recommendations below.\n"
            f"If any rule below conflicts with the user's request, the user's request WINS.\n"
            f"========================================\n\n"
        )
        _force_footer = (
            f"\n\n========================================\n"
            f"[FINAL REMINDER — DO NOT IGNORE]\n"
            f"User's exact request was: \"{_custom_text_force}\"\n"
            f"Generate the outfit to fulfill this request precisely. "
            f"Every garment, color, and detail MUST reflect: \"{_custom_text_force}\"\n"
            f"========================================\n"
        )
        prompt = _force_header + prompt + _force_footer
        # 프론트가 만든 imagePrompt도 있으면 추가 강화
        _front_image_prompt = str(payload.get("imagePrompt") or "").strip()
        if _front_image_prompt and len(_front_image_prompt) > 30:
            prompt += f"\n\n[FRONTEND USER-CRAFTED PROMPT — ALSO MUST FOLLOW]\n{_front_image_prompt}\n"
        short = f"직접입력 — {_custom_text_force[:30]}"
        print(f"[직접입력 강제] customText='{_custom_text_force}' → 프롬프트 강제 오버라이드 적용")

    face_data_url = payload.get("faceImage")
    size = str(payload.get("size") or "1024x1659")  # 1:1.62 비율
    quality = str(payload.get("quality") or "low")

    # 출력 포맷(모바일 로딩 최적화)
    output_format = str(payload.get("output_format") or "jpeg")
    output_compression = int(payload.get("output_compression") or 80)

    # --- 서버 캐시(파일) ---
    # - 같은 조건(날씨/목적/프로필/seed/얼굴/참조의상)로 재요청하면 OpenAI 호출 없이 바로 반환합니다.
    ref_images, face_bytes_for_key = _collect_ref_images(payload)
    cache_key = _make_ai_cache_key(payload, face_bytes_for_key, ref_images)
    ext = "jpg" if output_format.lower() in ("jpeg", "jpg") else output_format.lower()
    cache_fname = f"ai_{cache_key}.{ext}"
    cache_fpath = os.path.join(_UPLOAD_DIR, cache_fname)
    if os.path.exists(cache_fpath):
        rel = f"{_UPLOAD_PREFIX}{cache_fname}"
        base = _public_base()
        # [2026-04-10] 캐시 응답에도 분석 포함 (엔진 메타가 없으면 빈 분석)
        try:
            _cached_analysis = _generate_styling_analysis(payload, _matched_stylist, _meta, lang=str(payload.get("lang") or "ko"))
        except Exception:
            _cached_analysis = None
        return jsonify(
            ok=True,
            image=f"{base}{rel}",  # 프론트 호환: img src로 바로 사용
            path=rel,
            url=f"{base}{rel}",
            explanation=short,
            model="cache",
            cached=True,
            stylingAnalysis=_cached_analysis,
        )

    # ══════════════════════════════════════════════════════
    # [2026-04-10] 코디쌤 AI 코디 — Gemini 우선 라우팅
    # 환경변수 CODIBANK_AI_STYLING_PROVIDER:
    #   "gemini" (기본) → Gemini 단일 호출 (이미지+분석 동시)
    #   "openai"        → OpenAI 이미지 + 템플릿 분석 (기존 방식)
    # Gemini는 응답에 분석 JSON 마커를 함께 출력하여 추가 호출 없이 종합 분석 제공.
    # ══════════════════════════════════════════════════════
    _styling_provider = (os.getenv("CODIBANK_AI_STYLING_PROVIDER") or "gemini").strip().lower()
    if _styling_provider == "gemini" and _GEMINI_KEY:
        try:
            print(f"[ai_styling] Gemini 단일 호출 모드 (이미지+분석 동시)")
            _gemini_result = _ai_styling_via_gemini(
                payload=payload,
                prompt=prompt,
                short=short,
                ref_images=ref_images,
                cache_fname=cache_fname,
                ext=ext,
                matched_stylist=_matched_stylist,
                lang=str(payload.get("lang") or "ko"),
                meta=_meta,
            )
            # _ai_styling_via_gemini는 이미 jsonify 결과를 반환
            # 성공이면 그대로 반환, 실패면 폴백
            if isinstance(_gemini_result, tuple):
                # (jsonify(error), status_code) 형태 → 에러 발생
                _resp_obj, _status = _gemini_result
                if _status == 500 and has_openai:
                    print(f"[ai_styling] Gemini 실패, OpenAI 폴백으로 전환")
                    # 폴백 로직으로 진행 (아래 OpenAI 코드 실행)
                else:
                    return _gemini_result
            else:
                # jsonify(...) 단독 반환 → 성공
                return _gemini_result
        except Exception as _ge:
            print(f"[ai_styling] Gemini 라우팅 예외: {_ge}, OpenAI 폴백 시도")
            import traceback as _tbg
            _tbg.print_exc()
            if not has_openai:
                return jsonify(ok=False, error=f"Gemini 실패: {str(_ge)[:300]}"), 500

    # ── 코디쌤(/api/ai/styling) OpenAI 폴백 경로 ──
    # 위 Gemini 라우팅이 실패했거나 명시적으로 OpenAI를 선택한 경우 사용
    if not has_openai:
        return jsonify(
            ok=False,
            error="OPENAI_API_KEY가 설정되지 않았습니다. 코디쌤 AI 코디는 OpenAI API 또는 Gemini API가 필요합니다.",
        ), 400

    model_no_face = os.getenv("CODIBANK_OPENAI_IMAGE_MODEL", "gpt-image-1.5")
    model_with_face = os.getenv("CODIBANK_OPENAI_IMAGE_MODEL_FACE", "gpt-image-1.5")

    client = get_client()

    try:
        model_used = ""

        if ref_images:
            # 우선순위: 얼굴+상의+하의 -> 상의+하의 -> 얼굴만
            variants: list[list[tuple[str, str, bytes]]] = []
            variants.append(ref_images)
            clothing_only = [r for r in ref_images if r[0] in ("top", "bottom")]
            face_only = [r for r in ref_images if r[0] == "face"]
            if clothing_only and clothing_only != ref_images:
                variants.append(clothing_only)
            if face_only and face_only not in variants:
                variants.append(face_only)

            last_err: Exception | None = None
            for refs_variant in variants:
                model_pref = model_with_face if any(r[0] == "face" for r in refs_variant) else model_no_face
                for m in _candidate_image_models(model_pref):
                    try:
                        bios = _make_ref_bios(refs_variant)
                        resp = _images_edit_compat(
                            client,
                            model=m,
                            image_files=bios,
                            prompt=prompt,
                            size=size,
                            quality=quality,
                            output_format=output_format,
                            output_compression=output_compression,
                        )
                        model_used = m
                        last_err = None
                        break
                    except Exception as e:
                        last_err = e
                        if _is_model_access_error(str(e)):
                            continue
                        continue
                if model_used:
                    break
            if last_err is not None and not model_used:
                raise last_err
        else:
            last_err = None
            for m in _candidate_image_models(model_no_face):
                try:
                    resp = _images_generate_compat(
                        client,
                        model=m,
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        output_format=output_format,
                        output_compression=output_compression,
                    )
                    model_used = m
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    if _is_model_access_error(str(e)):
                        continue
                    raise
            if last_err is not None and not model_used:
                raise last_err

        b64 = resp.data[0].b64_json
        img_bytes = base64.b64decode(b64)

        rel = _write_upload_bytes("ai", ext, img_bytes, fixed_name=cache_fname)
        base = _public_base()

        # [2026-04-10] AI 패션 스타일리스트 종합 분석 생성
        try:
            _styling_analysis = _generate_styling_analysis(payload, _matched_stylist, _meta, lang=str(payload.get("lang") or "ko"))
        except Exception as _ae:
            print(f"[styling_analysis] 생성 실패: {_ae}")
            _styling_analysis = None

        return jsonify(
            ok=True,
            image=f"{base}{rel}",
            path=rel,
            url=f"{base}{rel}",
            explanation=short,
            model=model_used,
            cached=False,
            prompt=prompt if os.getenv("CODIBANK_DEBUG_PROMPT") == "1" else None,
            stylist=_matched_stylist,
            stylingStory=_styling_story or None,
            # [2026-04-06 추가] UI 스타일링 포인트용 데이터
            engineKeywords=_meta.get('keywords_selected', []),
            engineCategoryKeywords=_meta.get('categoryKeywords', {}),
            engineCity=_meta.get('active_city', ''),
            enginePurpose=_meta.get('purpose', ''),
            engineBottomType=_meta.get('bottom_type', ''),
            # [2026-04-10 추가] AI 스타일리스트 종합 분석 (퍼스널컬러/체형/목적+날씨)
            stylingAnalysis=_styling_analysis,
        )

    except Exception as e:
        return (
            jsonify(
                ok=False,
                error=str(e),
                openai_sdk=_sdk_version(),
                has_openai_key=_safe_bool(os.getenv("OPENAI_API_KEY")),
        has_gemini_key=_safe_bool(os.getenv("GEMINI_API_KEY")),
        codistyle_model=os.getenv("CODISTYLE_GEMINI_MODEL","gemini-2.5-flash-image"),
            ),
            500,
        )


# ─────────────────────────────────────────────────────────
# /api/codistyle/generate  — Gemini 착장 이미지 생성
# ★ google-genai 공식 SDK 사용 (REST API는 이미지 생성 모델에서 미작동)
# ★ google-generativeai(구버전)이 아닌 google-genai(신버전) 필수
# ─────────────────────────────────────────────────────────
_CODISTYLE_MODEL = (
    os.getenv("CODISTYLE_GEMINI_MODEL") or
    os.getenv("CODIBANK_CODISTYLE_MODEL") or
    "gemini-2.5-flash-image"
)
_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

def _detect_bottom_type_from_image(bottom_bytes: bytes, bottom_mime: str, sdk: str, gemini_key: str, genai_mod, gtypes_mod=None) -> dict:
    """Gemini로 하의 이미지를 상세 분석 → 타입/길이/실루엣 반환"""
    try:
        detect_prompt = (
            "Analyze this clothing item carefully and respond in JSON format only. "
            "No explanation, just JSON. "
            "Example: {\"type\":\"skirt\",\"length\":\"maxi\",\"silhouette\":\"tiered flared skirt reaching ankle\"} "
            "Rules: "
            "type: 'skirt' if NO leg separation (skirt/치마/スカート regardless of width or layers), "
            "'shorts' if SHORT pants above knee, "
            "'pants' if leg separation AND reaches below knee. "
            "length for skirts: 'mini'=above knee, 'midi'=knee to mid-calf, 'maxi'=mid-calf to ankle/floor. "
            "length for pants: 'short'=above knee, 'cropped'=mid-calf, 'full'=ankle/floor. "
            "silhouette: brief description of the garment shape, hem style, and key design features. "
            "IMPORTANT: A wide pleated/tiered/ruffled garment with no leg separation = SKIRT, not wide-leg pants. "
            "NOTE: The image may contain a background (floor, wall, hanger, hand, etc). Ignore the background and analyze ONLY the clothing item."
        )
        _result_json = None
        if sdk == "new" and gtypes_mod:
            client = genai_mod.Client(api_key=gemini_key)
            img_part = gtypes_mod.Part.from_bytes(data=bottom_bytes, mime_type=bottom_mime or "image/jpeg")
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[detect_prompt, img_part],
            )
            raw = (resp.text or "").strip()
        else:
            from PIL import Image as _PIL
            import io as _io
            genai_mod.configure(api_key=gemini_key)
            _model = genai_mod.GenerativeModel("gemini-1.5-flash")
            _pil = _PIL.open(_io.BytesIO(bottom_bytes))
            resp = _model.generate_content([detect_prompt, _pil])
            raw = (resp.text or "").strip()

        # JSON 파싱
        import json as _json, re as _re
        raw_clean = _re.sub(r'```json|```', '', raw).strip()
        _m = _re.search(r'\{.*\}', raw_clean, _re.DOTALL)
        if _m:
            _result_json = _json.loads(_m.group())
        else:
            _result_json = {"type": "skirt" if "SKIRT" in raw.upper() else "pants", "length": "full", "silhouette": raw[:80]}

        print(f"[codistyle] 하의 분석 결과: {_result_json}")
        return _result_json
    except Exception as e:
        print(f"[codistyle] 하의 분석 실패, 기본값 사용: {e}")
        return {"type": "pants", "length": "full", "silhouette": "trousers"}


def _analyze_garment_category(category_key: str, sub_category: str = "") -> dict:
    """[2026-04-09] 카테고리+서브카테고리 → 착장 생성용 상세 의류 정보 (세분화)"""
    k = (category_key or "").lower().strip()
    sub = (sub_category or "").lower().strip()
    combined = k + " " + sub

    # ── 아우터 (코트류) ──
    if k in ("coat", "코트") or any(x in combined for x in ["코트","트렌치","더플","롱코트","케이프"]):
        return {"type": "top", "garment": "coat", "garment_class": "outerwear", "ko": sub or "코트",
                "length": "knee-length or longer", "tuck": "never",
                "inner_layer": "simple white or black crew-neck T-shirt underneath",
                "rule": "OUTERWEAR: Worn OPEN. Add a plain white/black tee underneath."}

    # ── 아우터 (자켓/패딩류) ──
    if k in ("jacket", "자켓") or any(x in combined for x in ["자켓","블레이저","수트자켓","콤비자켓",
            "사파리","데님자켓","레더","패딩","다운","가디건","볼레로","집업","후드집업"]):
        garment_ko = sub or "자켓"
        is_cardigan = "가디건" in combined
        return {"type": "top", "garment": "jacket", "garment_class": "outerwear", "ko": garment_ko,
                "length": "hip-length", "tuck": "never",
                "inner_layer": "simple white or black crew-neck T-shirt underneath" if not is_cardigan else "light inner top",
                "rule": "OUTERWEAR: Worn OPEN over inner layer. Never tucked."}

    # ── 상의: 맨투맨/후드/스웨터/니트 (절대 넣지 않음) ──
    if any(x in combined for x in ["맨투맨","후드티","스웨터","니트","sweater","hoodie","sweatshirt"]):
        garment_ko = sub or ("맨투맨" if "맨투맨" in combined else "니트" if "니트" in combined else "후드티")
        return {"type": "top", "garment": "sweatshirt", "garment_class": "pullover", "ko": garment_ko,
                "length": "waist to hip", "tuck": "never",
                "inner_layer": None,
                "rule": "PULLOVER: Hem hangs NATURALLY outside the bottom garment. NEVER tuck in."}

    # ── 상의: 클래식 와이셔츠/드레스셔츠 (넣기 가능) ──
    if any(x in combined for x in ["와이셔츠","드레스셔츠","dress shirt","oxford","formal shirt"]):
        return {"type": "top", "garment": "dress_shirt", "garment_class": "shirt", "ko": sub or "와이셔츠",
                "length": "waist", "tuck": "tucked_in",
                "inner_layer": None,
                "rule": "DRESS SHIRT: Tuck into the waistband for a clean formal look."}

    # ── 상의: 캐주얼셔츠/블라우스 (체형 고려 후 프론트턱 또는 언턱) ──
    if any(x in combined for x in ["셔츠","블라우스","남방","shirt","blouse"]):
        garment_ko = sub or ("블라우스" if "블라우스" in combined else "셔츠")
        return {"type": "top", "garment": "casual_shirt", "garment_class": "shirt", "ko": garment_ko,
                "length": "waist to hip", "tuck": "front_tuck_optional",
                "inner_layer": None,
                "rule": "CASUAL SHIRT: Default is UNTUCKED. A trendy front-tuck is acceptable for slim/standard body types only. Consider user body type."}

    # ── 상의: 티셔츠/반팔/나시 (기본 언턱) ──
    if k in ("top", "상의") or any(x in combined for x in ["티셔츠","반팔","긴팔","나시","탱크","t-shirt","tank"]):
        garment_ko = sub or "티셔츠"
        return {"type": "top", "garment": "tshirt", "garment_class": "tshirt", "ko": garment_ko,
                "length": "waist to hip", "tuck": "front_tuck_optional",
                "inner_layer": None,
                "rule": "T-SHIRT: Default is UNTUCKED. A front-tuck is optional for slim body types with high-waist bottoms."}

    # ── 하의: 치마 ──
    if any(x in combined for x in ["스커트","치마","skirt"]):
        skirt_type = "mini skirt" if any(x in sub for x in ["미니","mini"]) else                      "midi skirt" if any(x in sub for x in ["미디","플리츠","midi"]) else                      "maxi skirt" if any(x in sub for x in ["롱","maxi"]) else "skirt"
        return {"type": "bottom", "garment": skirt_type, "garment_class": "skirt", "ko": sub or "스커트",
                "is_skirt": True,
                "rule": f"MUST generate {skirt_type} — NOT pants. This is a SKIRT."}

    # ── 하의: 바지 ──
    if k in ("pants", "하의") or any(x in combined for x in ["바지","청바지","슬랙스","조거","추리닝","반바지","7부","jeans","pants"]):
        is_shorts = any(x in combined for x in ["반바지","shorts","7부"])
        return {"type": "bottom", "garment": "shorts" if is_shorts else "trousers", "garment_class": "pants",
                "ko": sub or "바지", "is_skirt": False,
                "rule": "Generate trousers/pants as specified"}

    # ── 기본 ──
    return {"type": "unknown", "garment": k or "garment", "garment_class": "unknown",
            "ko": k or "의류", "is_skirt": False, "tuck": "natural", "rule": ""}


def _build_garment_instruction(top_info: dict, bottom_info: dict) -> str:
    """상의/하의 정보 → 프롬프트 핵심 지시문"""
    top_ko = top_info.get("ko", "상의")
    bottom_ko = bottom_info.get("ko", "하의")
    top_en = top_info.get("garment", "top garment")
    bottom_en = bottom_info.get("garment", "bottom garment")
    is_skirt = bottom_info.get("is_skirt", False)
    bottom_rule = bottom_info.get("rule", "")

    instr = (
        f"⚠ GARMENT IDENTITY (HIGHEST PRIORITY — MUST NOT BE CHANGED): "
        f"Upper body = [{top_ko} / {top_en}]. "
        f"Lower body = [{bottom_ko} / {bottom_en}]. "
        f"REPRODUCE BOTH GARMENTS EXACTLY AS SPECIFIED. "
    )
    if is_skirt:
        instr += (
            f"CRITICAL SKIRT RULE: The lower garment is a [{bottom_ko}] — a SKIRT, NOT pants. "
            f"You MUST generate a {bottom_en}. "
            f"It is ABSOLUTELY FORBIDDEN to replace the skirt with trousers or any leg-covering garment. "
            f"The skirt must be clearly visible as a skirt in the final image. "
        )
    return instr


@app.post("/api/codistyle/analyze-garments")
def codistyle_analyze_garments():
    """
    코디하기 Phase 1: 상의+하의 이미지를 analyze-item과 동일한 방식으로 분석
    - analyze-item의 검증된 프롬프트 재사용
    - 치마(skirt) category 분리로 is_skirt 정확 판별
    - 착용샷(사람이 입은 사진)도 처리 가능
    """
    payload = request.get_json(silent=True) or {}

    def _call_analyze_item(data_url, path_val):
        """analyze-item 엔드포인트 내부 로직 직접 호출"""
        import requests as _rq
        try:
            # base64 dataUrl 우선 사용
            src = str(data_url or "").strip()
            if src.startswith("data:"):
                body = {"image": src, "skip_embedding": True}  # [2026-04-19 PERF] Marqo 스킵
            elif path_val:
                path = str(path_val).strip()
                # R2 또는 로컬에서 이미지 로드
                img_bytes = None
                if path.startswith("/uploads/") and _R2_PUB_URL:
                    try:
                        r = _rq.get(f"{_R2_PUB_URL}{path}", timeout=8)
                        if r.status_code == 200:
                            import base64
                            img_bytes = r.content
                    except: pass
                if not img_bytes:
                    for d in [_UPLOAD_DIR, _LEGACY_UPLOAD_DIR]:
                        fp = os.path.join(d, os.path.basename(path))
                        if os.path.exists(fp):
                            with open(fp, "rb") as fh:
                                img_bytes = fh.read()
                            break
                if img_bytes:
                    import base64
                    b64 = base64.b64encode(img_bytes).decode()
                    body = {"image": f"data:image/jpeg;base64,{b64}", "skip_embedding": True}  # [2026-04-19 PERF] Marqo 스킵
                else:
                    return {"error": "이미지 로드 실패", "_analyzed": False}
            else:
                return {"error": "이미지 없음", "_analyzed": False}

            # Flask 내부에서 analyze-item 직접 호출
            with app.test_request_context(
                '/api/ai/analyze-item',
                method='POST',
                json=body,
                headers=dict(request.headers)
            ):
                from flask import g as _g
                result = ai_analyze_item()
                if hasattr(result, 'get_json'):
                    d = result.get_json()
                else:
                    d = result[0].get_json() if isinstance(result, tuple) else {}

            if d and d.get("ok") and d.get("analysis"):
                analysis = d["analysis"]
                # is_skirt 보장: category=skirt 또는 sub_category에 스커트 키워드
                _skirt_kws = ['스커트','skirt','치마']
                _cat = str(analysis.get("category","")).lower()
                _sub = str(analysis.get("sub_category","")).lower()
                analysis["is_skirt"] = (
                    _cat == "skirt" or
                    analysis.get("is_skirt") == "true" or
                    analysis.get("is_skirt") is True or
                    any(k in _sub for k in _skirt_kws)
                )
                # skirt_length 추가
                if analysis["is_skirt"] and not analysis.get("skirt_length"):
                    if "미니" in _sub: analysis["skirt_length"] = "mini"
                    elif "롱" in _sub or "맥시" in _sub: analysis["skirt_length"] = "maxi"
                    else: analysis["skirt_length"] = "midi"
                analysis["_analyzed"] = True
                print(f"[analyze-garments] {_cat}/{_sub} is_skirt={analysis['is_skirt']}")
                return analysis
            return {"error": "분석 실패", "_analyzed": False}
        except Exception as e:
            print(f"[analyze-garments] 오류: {e}")
            return {"error": str(e)[:80], "_analyzed": False}

    # ──── [2026-04-19 PERF] Phase 1 상/하의 병렬 분석 ────
    # 원인: 기존은 top_result 완료를 기다린 후 bottom_result 순차 실행
    #       → 각 아이템당 Lykdat(2~5s) + Marqo(1~3s) + Gemini(3~5s) = 6~13초
    #       → 2벌 순차 = 12~26초 (가장 큰 단일 병목)
    # 해결: ThreadPoolExecutor로 상/하의 동시 실행
    #       → max(상의, 하의) ≈ 6~13초 (약 50% 단축)
    # 안전성: Flask test_request_context는 thread-safe (각 thread가 독립 context)
    #         request.headers는 스레드 진입 전 dict로 복사해서 thread-local 이슈 회피
    # ────
    import concurrent.futures as _cf
    _headers_snapshot = dict(request.headers)  # thread 진입 전에 캡처

    def _run_top():
        return _call_analyze_item(payload.get("topDataUrl"), payload.get("topPath"))

    def _run_bottom():
        return _call_analyze_item(payload.get("bottomDataUrl"), payload.get("bottomPath"))

    with _cf.ThreadPoolExecutor(max_workers=2) as _ex:
        _fut_top    = _ex.submit(_run_top)
        _fut_bottom = _ex.submit(_run_bottom)
        try:
            top_result    = _fut_top.result(timeout=60)
        except Exception as _te:
            print(f"[analyze-garments] 상의 병렬 분석 실패: {_te}")
            top_result = {"error": str(_te)[:80], "_analyzed": False}
        try:
            bottom_result = _fut_bottom.result(timeout=60)
        except Exception as _be:
            print(f"[analyze-garments] 하의 병렬 분석 실패: {_be}")
            bottom_result = {"error": str(_be)[:80], "_analyzed": False}

    return jsonify(ok=True, top=top_result, bottom=bottom_result)


# ════════════════════════════════════════
# /api/personal-color/save & load
# ════════════════════════════════════════
_PC_STORE = {}  # 메모리 캐시 (R2 영구저장 연동 가능)

@app.post("/api/personal-color/save")
def pc_save():
    data = request.json or {}
    email = str(data.get("email") or "").strip()
    pc = data.get("personalColor")
    if not email or not pc:
        return jsonify(ok=False, error="email and personalColor required"), 400
    _PC_STORE[email] = pc
    # R2 영구저장 (선택)
    try:
        _path = f"personal_color/{email}.json"
        import json
        _write_upload_bytes(_path, json.dumps(pc, ensure_ascii=False).encode("utf-8"))
        print(f"[PC] saved to R2: {_path}")
    except Exception as e:
        print(f"[PC] R2 save failed: {e}")
    return jsonify(ok=True)

@app.get("/api/personal-color/load/<email>")
def pc_load(email):
    email = str(email or "").strip()
    if not email:
        return jsonify(ok=False, error="email required"), 400
    # 메모리 캐시 우선
    if email in _PC_STORE:
        return jsonify(ok=True, personalColor=_PC_STORE[email])
    # R2에서 로드
    try:
        import json
        _path = f"personal_color/{email}.json"
        data = _read_upload_bytes(_path)
        if data:
            pc = json.loads(data.decode("utf-8"))
            _PC_STORE[email] = pc
            return jsonify(ok=True, personalColor=pc)
    except Exception as e:
        print(f"[PC] R2 load failed: {e}")
    return jsonify(ok=True, personalColor=None)


@app.post("/api/codistyle/generate")
def codistyle_generate():
    _cs_lang = str(request.json.get("lang") or "ko").strip().lower()
    _cs_en = (_cs_lang == "en")
    if not _GEMINI_KEY:
        return jsonify(ok=False, error="GEMINI_API_KEY 미설정"), 400

    # ── SDK 감지: google-genai(신) 우선 → google-generativeai(구) 폴백 ──
    _SDK = None  # "new" 또는 "old"
    try:
        from google import genai as _genai
        from google.genai import types as _gtypes
        _SDK = "new"
    except ImportError:
        pass

    if not _SDK:
        try:
            import google.generativeai as _genai_old
            _SDK = "old"
        except ImportError:
            return jsonify(ok=False, error="Gemini SDK 미설치. google-genai 또는 google-generativeai 필요"), 500

    payload   = request.get_json(silent=True) or {}
    user_info      = payload.get("user") or {}
    # ──── [2026-04-10 수정] 성별 정규화 통합 적용 ────
    gender    = _normalize_gender_code(str(user_info.get("gender", "")))
    gender_en = "woman" if gender == "F" else "man"
    gender_ko = "여성" if gender == "F" else "남성"
    age       = str(user_info.get("ageGroup", "30대")).strip()
    height    = str(user_info.get("height", "")).strip()
    weight    = str(user_info.get("weight", "")).strip()
    hw_ko     = f"키 {height}cm, 몸무게 {weight}kg" if height and weight else ""
    hw_en     = f"height {height}cm, weight {weight}kg" if height and weight else ""
    # ── 다시요청 여부 (프론트에서 generate(true) 호출 시 전송) ──
    is_retry  = bool(payload.get("isRetry", False))

    # ──── [2026-04-19 BODY] 체형 키 지역 변수화 (Phase 1 PERSONA 주입용) ────
    # 이전: payload.get("bodyType")를 STYLING_SCORE 섹션에서만 호출
    # 수정: Phase 1 PERSONA + STYLING_SCORE 양쪽에서 재사용하도록 지역 변수로 추출
    # ────
    _body_type_key = str(payload.get("bodyType", "")).strip()

    # ── Phase 1 분석 결과 수신 (프론트에서 analyze-garments 호출 후 전달) ──
    _top_analysis    = payload.get("topAnalysis")    or {}
    _bottom_analysis_pre = payload.get("bottomAnalysis") or {}

    # top_info 구성
    _top_sub = str(_top_analysis.get("sub_category", payload.get("topSubCategory", ""))).strip()
    _top_cat = str(_top_analysis.get("category",     payload.get("topCategoryKey","top"))).strip()
    _top_color_ko = str(_top_analysis.get("main_color_name","")).strip()
    _top_pattern  = str(_top_analysis.get("pattern","")).strip()
    _top_material = str(_top_analysis.get("material","")).strip()
    _top_fit      = str(_top_analysis.get("fit","")).strip()
    _top_design   = str(_top_analysis.get("key_design","")).strip()
    top_info = _analyze_garment_category(_top_cat, _top_sub)
    if _top_sub: top_info["ko"] = _top_sub
    top_info["color_ko"]   = _top_color_ko
    top_info["pattern"]    = _top_pattern
    top_info["material"]   = _top_material
    top_info["design"]     = _top_design

    # ──── [2026-04-20 03:40 KST] 치마 이미지 비율 → 4단계 기장 분류 (위치 이동) ────
    # 원인: 기존에는 이 블록이 Phase1 True 분기(아래 _skirt_length_cat 참조) 뒤에 있어
    #       UnboundLocalError 발생 → 치마 처리 예외 → fallback에서 바지로 오인 가능성
    # 수정: bottom_info 구성 전으로 이동하여 정상 순서 보장
    # 매핑: 가로:세로 비율 기반
    #   ratio < 0.8  → mini (무릎 위 15-20cm)
    #   0.8 ~ 1.2    → midi_above (무릎 위 3cm)
    #   1.2 ~ 1.7    → midi_below (무릎 아래 10cm)
    #   1.7+         → long (발목)
    # 주의: 이 분석은 bottom 이미지가 치마든 바지든 먼저 수행됨 (결과는 Phase1 True일 때만 사용)
    # ────
    _skirt_ratio_hint = ""
    _skirt_length_cat = ""  # "mini" | "midi_above" | "midi_below" | "long"
    try:
        from PIL import Image as _PIL_ratio
        import io as _io_ratio
        _bottom_pil = _PIL_ratio.open(_io_ratio.BytesIO(bottom_bytes))
        _bw, _bh = _bottom_pil.size
        _wh_ratio = _bh / _bw if _bw > 0 else 1.0

        if _wh_ratio < 0.8:
            _skirt_length_cat = "mini"
            _skirt_length_desc = "MINI skirt (hem 15-20cm above knee)"
            _skirt_hem_position = "mid-thigh, well above the knee"
        elif _wh_ratio < 1.2:
            _skirt_length_cat = "midi_above"
            _skirt_length_desc = "MIDI skirt above-knee (hem 3cm above kneecap)"
            _skirt_hem_position = "3cm above the kneecap, knee visible"
        elif _wh_ratio < 1.7:
            _skirt_length_cat = "midi_below"
            _skirt_length_desc = "MIDI skirt below-knee (hem 10cm below kneecap)"
            _skirt_hem_position = "10cm below the kneecap, mid-calf"
        else:
            _skirt_length_cat = "long"
            _skirt_length_desc = "LONG skirt (hem at ankle)"
            _skirt_hem_position = "at the ankle bone"

        _skirt_ratio_hint = (
            f"\nSkirt length (measured from reference image ratio {_wh_ratio:.2f}): "
            f"{_skirt_length_desc}. Hem position: {_skirt_hem_position}."
        )
        print(f"[codistyle] 치마 비율: {_bw}x{_bh} ratio={_wh_ratio:.2f} → {_skirt_length_cat}")
    except Exception as _ratio_err:
        print(f"[codistyle] 치마 비율 분석 실패: {_ratio_err}")

    # bottom_info 구성 — Phase 1 결과 우선 (is_skirt 확실히 판단)
    _bot_sub  = str(_bottom_analysis_pre.get("sub_category", payload.get("bottomSubCategory",""))).strip()
    _bot_cat  = str(_bottom_analysis_pre.get("category",     payload.get("bottomCategoryKey","pants"))).strip()
    _bot_is_skirt_pre = _bottom_analysis_pre.get("is_skirt", None)
    _bot_skirt_len    = str(_bottom_analysis_pre.get("skirt_length","") or "").strip()
    _bot_color_ko     = str(_bottom_analysis_pre.get("main_color_name","")).strip()
    _bot_pattern      = str(_bottom_analysis_pre.get("pattern","")).strip()
    _bot_material     = str(_bottom_analysis_pre.get("material","")).strip()
    _bot_design       = str(_bottom_analysis_pre.get("key_design","")).strip()
    # [2026-04-19 FIX#2] 바지 핏 판정: Phase1 분석 결과에서 fit + sub_category로 판단
    _bot_fit          = str(_bottom_analysis_pre.get("fit","")).strip().lower()
    # 스키니 판정: (1) Phase1 fit이 "스키니"/"slim"이거나 (2) sub_category에 스키니 키워드가 있을 때만
    _is_skinny = (
        _bot_fit in ("스키니", "skinny", "슬림", "slim") or
        any(kw in _bot_sub.lower() for kw in ["스키니", "skinny"])
    )
    bottom_info = _analyze_garment_category(_bot_cat, _bot_sub)
    if _bot_sub: bottom_info["ko"] = _bot_sub

    # Phase 1에서 is_skirt 확실하면 그대로 적용 (이미지 재분석 불필요)
    if _bot_is_skirt_pre is True:
        # [2026-04-19 FIX#1] 4단계 기장 매핑 (기존 3단계에서 세분화)
        _skirt_len_map = {
            "mini":       "MINI skirt (hem 15-20cm above knee, mid-to-upper thigh)",
            "midi_above": "MIDI skirt ABOVE-KNEE (hem EXACTLY 3cm above kneecap, knee visible)",
            "midi":       "MIDI skirt ABOVE-KNEE (hem EXACTLY 3cm above kneecap, knee visible)",
            "midi_below": "MIDI skirt BELOW-KNEE (hem EXACTLY 10cm below kneecap, mid-calf, knee covered)",
            "long":       "LONG skirt (hem at ankle bone, covers full leg)",
            "maxi":       "LONG skirt (hem at ankle bone, covers full leg)",
        }
        # 이미지 비율 기반 분류가 있으면 우선 사용 (프론트 skirt_length보다 정확)
        _skirt_len_key = _skirt_length_cat or _bot_skirt_len
        _skirt_en = _skirt_len_map.get(_skirt_len_key, "skirt")
        bottom_info = {
            "type":"bottom","garment":_skirt_en,"ko": _bot_sub or f"스커트({_skirt_len_key})",
            "is_skirt":True,"is_shorts":False,"detected_length":_skirt_len_key,
            "silhouette":_bot_design or f"{_bot_sub} skirt",
            "color_ko":_bot_color_ko,"pattern":_bot_pattern,"material":_bot_material,
            "rule":f"MUST generate {_skirt_en}. NO pants. NO leg separation. SKIRT ONLY."
        }
        _garment_instruction = _build_garment_instruction(top_info, bottom_info)
        print(f"[codistyle] Phase1 확인 → 하의={_bot_sub} is_skirt=True length={_skirt_len_key} (image_ratio={_skirt_length_cat or 'N/A'})")
    elif _bot_is_skirt_pre is False:
        bottom_info["is_skirt"] = False
        _garment_instruction = _build_garment_instruction(top_info, bottom_info)
        print(f"[codistyle] Phase1 확인 → 하의={_bot_sub} is_skirt=False")
    else:
        # Phase 1 미수행 → 이미지 분석으로 판별 (폴백)
        _garment_instruction = _build_garment_instruction(top_info, bottom_info)
        print(f"[codistyle] Phase1 없음 → 이미지 분석 폴백")

    top_category_key    = _top_cat
    bottom_category_key = _bot_cat

    # [2026-04-08] Phase 2 퍼스널컬러 (12서브타입 대응)
    personal_color = payload.get("personalColor") or None
    _pc_text = _build_pc_prompt_block(personal_color, mode="codistyle")

    # ── 이미지 로드 → bytes ──
    def _to_bytes(data_url_val, path_val=None):
        """dataUrl / 로컬파일 / HTTP URL → (mime, raw_bytes)"""
        src = str(data_url_val or "").strip()

        # 1) base64 dataURL
        if src.startswith("data:"):
            header, b64 = src.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
            return mime, base64.b64decode(b64)

        # ──── [2026-04-11 수정] 자기 서버 URL → R2 직접 로드 ────
        # 원인: gunicorn worker=1에서 자기 서버 /uploads/ URL로 HTTP 요청
        #       → 같은 worker가 generate + serve_upload 동시 처리 불가 → 데드락
        # 해결: 자기 서버 URL에서 /uploads/ 경로 추출 → R2 직접 로드
        # 관련파일: codistyle.html (모바일에서 dataUrl 없이 서버경로만 전송하는 경우)
        # ────
        if src.startswith("http://") or src.startswith("https://"):
            _self_upload_path = ""
            try:
                from urllib.parse import urlparse
                _parsed = urlparse(src)
                if _parsed.path and _parsed.path.startswith("/uploads/"):
                    _host = (_parsed.hostname or "").lower()
                    if "onrender.com" in _host or "codibank" in _host or "localhost" in _host or "127.0.0.1" in _host:
                        _self_upload_path = _parsed.path
            except Exception:
                pass

            if _self_upload_path:
                if _R2_PUB_URL:
                    r2_direct = f"{_R2_PUB_URL}{_self_upload_path}"
                    try:
                        import requests as _rq
                        r = _rq.get(r2_direct, timeout=15)
                        if r.status_code == 200:
                            ct = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
                            return ct, r.content
                    except Exception as e:
                        print(f"[_to_bytes] R2 직접 로드 실패 ({_self_upload_path}): {e}")
                for d in [_UPLOAD_DIR, _LEGACY_UPLOAD_DIR]:
                    fpath = os.path.join(d, os.path.basename(_self_upload_path))
                    if os.path.exists(fpath):
                        with open(fpath, "rb") as fh:
                            return "image/jpeg", fh.read()
                return None, None
            else:
                try:
                    import requests as _rq
                    r = _rq.get(src, timeout=10)
                    if r.status_code == 200:
                        ct = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
                        return ct, r.content
                except Exception as e:
                    print(f"[_to_bytes] HTTP 로드 실패 ({src[:60]}): {e}")

        path = str(path_val or "").strip()

        # 3) R2 공개 URL로 변환 후 HTTP 로드
        if path.startswith("/uploads/") and _R2_PUB_URL:
            r2_full = f"{_R2_PUB_URL}{path}"
            try:
                import requests as _rq
                r = _rq.get(r2_full, timeout=10)
                if r.status_code == 200:
                    ct = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
                    return ct, r.content
            except Exception as e:
                print(f"[_to_bytes] R2 로드 실패 ({r2_full[:60]}): {e}")

        # 4) 로컬 파일 폴백
        if path.startswith("/uploads/"):
            for d in [_UPLOAD_DIR, _LEGACY_UPLOAD_DIR]:
                fpath = os.path.join(d, os.path.basename(path))
                if os.path.exists(fpath):
                    with open(fpath, "rb") as fh:
                        return "image/jpeg", fh.read()

        return None, None

    top_mime,    top_bytes    = _to_bytes(payload.get("topDataUrl"),    payload.get("topPath"))
    bottom_mime, bottom_bytes = _to_bytes(payload.get("bottomDataUrl"), payload.get("bottomPath"))
    face_mime,   face_bytes   = _to_bytes(payload.get("faceImage"),     None)

    if not top_bytes or not bottom_bytes:
        return jsonify(ok=False, error="상의/하의 이미지가 필요합니다"), 400

    # [2026-04-20 03:40 KST] 치마 이미지 비율 분석 블록은 line 2705 앞으로 이동됨
    # (기존 위치에서는 Phase1 True 분기의 _skirt_length_cat 참조보다 뒤에 있어 UnboundLocalError 발생)

    # ── Phase 1 결과 있으면 재감지 스킵, 없으면 이미지 분석 ──
    # ──── [2026-04-20 03:40 KST] 치마→바지 덮어쓰기 차단 ────
    # 원칙: AI옷장에 등록된 아이템(Phase1 True/False 확정)은 그 결과를 절대 뒤집지 않음.
    #       새로 업로드한 아이템도 Phase1 분석 결과를 그대로 신뢰.
    #       이미지 재감지는 Phase1이 None(분석 실패)일 때만 수행.
    # ────
    _phase1_locked = (_bot_is_skirt_pre is True or _bot_is_skirt_pre is False)

    if _phase1_locked:
        print(f"[codistyle] Phase1 LOCKED → is_skirt={_bot_is_skirt_pre} (재감지 스킵)")
        # 치마(True)는 이미 line 2771-2793에서 bottom_info 구성 완료
        # 바지(False)일 때만 길이/실루엣을 이미지로 보강 (is_skirt=False는 유지)
        if _bot_is_skirt_pre is False:
            try:
                _bottom_analysis = _detect_bottom_type_from_image(
                    bottom_bytes, bottom_mime or "image/jpeg",
                    _SDK,
                    _GEMINI_KEY,
                    _genai if _SDK == "new" else _genai_old,
                    _gtypes if _SDK == "new" else None,
                )
                _detected_length     = _bottom_analysis.get("length", "full")
                _detected_silhouette = _bottom_analysis.get("silhouette", "")
                bottom_info["is_skirt"] = False
                bottom_info["is_shorts"] = (_detected_length == "short")
                _pants_length_en = {"short": "cropped pants", "cropped": "7/8 length pants", "full": "full-length trousers"}.get(_detected_length, "trousers")
                bottom_info["garment"]         = _pants_length_en
                bottom_info["detected_length"] = _detected_length
                bottom_info["silhouette"]      = _detected_silhouette
                _garment_instruction = _build_garment_instruction(top_info, bottom_info)
                print(f"[codistyle] Phase1=pants + 길이 보강: length={_detected_length}")
            except Exception as _pe:
                print(f"[codistyle] Phase1=pants 길이 보강 실패(무시): {_pe}")
    else:
        # Phase 1 결과 없음 (분석 실패 등) → 이미지로 직접 감지
        _bottom_analysis = _detect_bottom_type_from_image(
            bottom_bytes, bottom_mime or "image/jpeg",
            _SDK,
            _GEMINI_KEY,
            _genai if _SDK == "new" else _genai_old,
            _gtypes if _SDK == "new" else None,
        )
        _detected_type       = _bottom_analysis.get("type", "pants")
        _detected_length     = _bottom_analysis.get("length", "full")
        _detected_silhouette = _bottom_analysis.get("silhouette", "")

        if _detected_type == "skirt":
            # 이미지 비율 기반 4단계 기장 우선 적용
            _skirt_len_key = _skirt_length_cat or _detected_length
            _skirt_length_map = {
                "mini":       "mini skirt (hem 15-20cm above knee)",
                "midi_above": "midi skirt above-knee (hem 3cm above kneecap)",
                "midi":       "midi skirt above-knee (hem 3cm above kneecap)",
                "midi_below": "midi skirt below-knee (hem 10cm below kneecap)",
                "long":       "long skirt (hem at ankle)",
                "maxi":       "long skirt (hem at ankle)",
            }
            _skirt_length_en = _skirt_length_map.get(_skirt_len_key, "skirt")
            bottom_info = {
                "type": "bottom",
                "garment": _skirt_length_en,
                "ko": f"치마 ({_skirt_len_key})",
                "is_skirt": True,
                "is_shorts": False,
                "detected_length": _skirt_len_key,
                "silhouette": _detected_silhouette,
                "rule": f"Generate a {_skirt_length_en}. Skirt only, no pants or leggings."
            }
            _garment_instruction = _build_garment_instruction(top_info, bottom_info)
            print(f"[codistyle] 이미지감지 skirt → 하의:{bottom_info.get('ko')} length={_skirt_len_key}")
        elif _detected_type == "shorts":
            bottom_info = {
                "type": "bottom", "garment": "shorts (above knee)", "ko": "반바지",
                "is_skirt": False, "is_shorts": True,
                "detected_length": "short",
                "silhouette": _detected_silhouette,
                "rule": "Generate shorts with hem above the knee."
            }
            _garment_instruction = _build_garment_instruction(top_info, bottom_info)
            print(f"[codistyle] 이미지감지 shorts → 하의:{bottom_info.get('ko')}")
        else:
            _pants_length_en = {"short": "cropped pants", "cropped": "7/8 length pants", "full": "full-length trousers"}.get(_detected_length, "trousers")
            bottom_info["is_skirt"] = False
            bottom_info["is_shorts"] = False
            bottom_info["garment"] = _pants_length_en
            bottom_info["detected_length"] = _detected_length
            bottom_info["silhouette"] = _detected_silhouette
            _garment_instruction = _build_garment_instruction(top_info, bottom_info)
            print(f"[codistyle] 이미지감지 pants → 하의:{bottom_info.get('ko')} length={_detected_length}")

    # ── 프롬프트 구성 ──
    if face_bytes:
        # [2026-04-19 FACE] 얼굴 재현 정확도 강화 (기존 2문장 → 구체적 체크리스트)
        # 목적: Gemini가 "대충 비슷한 한국인"이 아니라 실제 얼굴 특징을 정밀하게 모사하도록
        # 근거: 해상도 상향(1024px) + 세부 지시문 결합 시 재현율 60→85%+ 상승 예상
        face_line = (
            f"The FIRST image is the face reference of the actual person ({gender_ko}"
            + (f", {hw_ko}" if hw_ko else "") + "). "
            "IDENTITY PRESERVATION — HIGHEST PRIORITY: "
            "Match EXACTLY the following facial features from the reference: "
            "face shape and jawline contour, eye shape/size/angle, double-eyelid presence and depth, "
            "eyebrow thickness and arch, nose bridge width and tip shape, "
            "lip shape and thickness, philtrum length, cheekbone prominence, "
            "skin tone and undertone, hair color/texture/length/parting line, "
            "and any distinguishing features (moles, freckles, dimples, scars). "
            "DO NOT beautify, smooth, slim, or idealize the face. "
            "DO NOT alter proportions or make the person look younger/older. "
            "Generate the image as if THIS EXACT PERSON — unchanged — is wearing the clothes. "
            "The generated face must be instantly recognizable as the same individual in the reference. "
        )
        img_desc = "FIRST image=face reference (identity source), SECOND image=upper garment, THIRD image=lower garment."
    else:
        face_line = (
            f"Subject: Korean {gender_en}, {age}"
            + (f", {hw_en}" if hw_en else "") + ". "
        )
        img_desc = "FIRST image=upper garment, SECOND image=lower garment."

    # [2026-04-10] 배경 포함 이미지 대응 — Gemini에 의류만 집중하도록 지시
    img_desc += (
        " IMPORTANT: Each garment image may contain a background (floor, wall, table, hand, hanger, etc). "
        "IGNORE the background entirely and focus ONLY on the clothing item in the image. "
        "Extract the garment's exact color, pattern, texture, silhouette, and design details from the clothing area only. "
        "Do NOT incorporate any background elements into the generated outfit image."
    )

    # 한국어 보조 지시 (얼굴 유무에 따라 다르게)
    if face_bytes:
        ko_instruction = "첨부한 얼굴 이미지의 인물이 상의와 하의를 입고 있는 전신 모습을 생성해주세요. "
    else:
        ko_instruction = "첨부한 상의와 하의를 입고 있는 전신 모습을 생성해주세요. "

    # ── [2026-04-20 06:50 KST] _pants_rule + _retry_pants 데드 코드 완전 제거 ──
    # 원인: 치마/바지 여부를 체크하지 않고 항상 "[RULE #1 — PANTS LENGTH — ABSOLUTE PRIORITY]"
    #       "DO NOT use the reference image" "OVERRIDES the reference image visual. No exceptions"
    #       같은 문구를 만들어두었음.
    #       옵션 A 재설계 이후 최종 프롬프트에 삽입되지 않는 데드 코드이지만, 이름이
    #       "_pants_rule"이라 향후 재활용 시 치마→바지 사고 재발 위험 매우 큼.
    # 수정: 블록 전체 삭제. 바지 길이/핏 규칙은 _bot_rule의 바지 분기에 이미 충분히 있음.
    # 삭제된 변수: _request_7bu, _is_female_cs, _retry_pants, _pants_rule
    # 삭제된 페이로드 플래그: request7bu, retryLongerPants (사용처 없어 무관)
    # ──────────────────────────────────────────────────────────────────────


    # ══════════════════════════════════════════════════════════════
    # CodiBank 착장이미지 생성 프롬프트 v2 (4단계 프레임워크)
    # ══════════════════════════════════════════════════════════════

    # 퍼스널컬러 시즌/언더톤 추출 — [2026-04-20 03:52 KST] summary 필드 추가
    # 원인: 프로필 페이지의 한줄요약(summary)이 이미지 생성 프롬프트에 반영 안 됨
    # 수정: personal_color.summary를 Phase 1 PERSONA + Phase 5 EVAL에 함께 주입
    _pc_season   = personal_color.get("season", "")    if personal_color else ""
    _pc_undertone= personal_color.get("undertone", "") if personal_color else ""
    _pc_best_colors  = ", ".join((personal_color.get("best_colors")  or [])[:4]) if personal_color else ""
    _pc_avoid_colors = ", ".join((personal_color.get("avoid_colors") or [])[:3]) if personal_color else ""
    _pc_summary      = str(personal_color.get("summary", "") if personal_color else "").strip()

    # ──── [2026-04-20 03:40 KST] 프롬프트 전면 재설계 (옵션 A) ────
    # 원칙:
    #   1. 중복 제거 — 같은 지시는 단 한 곳에서만
    #   2. 치마/바지 분기 명확 — 공통 체크리스트에서 부적절 항목 제거
    #   3. 긍정문 우선 — "DO NOT" 최소화
    #   4. AI옷장/Phase1 분석 데이터를 신뢰하여 직접 주입
    #   5. 하의 스타일 분석 출력 강화 (Bottom Style Analysis 자주 누락되던 문제 해결)
    # 구조: SYSTEM → P1 PERSONA → P2 GARMENTS → P3 WEARING → P4 IMAGE → P5 EVAL
    # 분량: 기존 22,000자 → 약 8,500자 (60% 감소)
    # ────
    _is_skirt_out = bool(bottom_info.get("is_skirt"))
    _is_shorts_out = bool(bottom_info.get("is_shorts"))
    _top_ko  = top_info.get("ko", "상의")
    _top_en  = top_info.get("garment", "top")
    _top_cls = top_info.get("garment_class", "tshirt")
    _bot_ko  = bottom_info.get("ko", "하의")
    _bot_en  = bottom_info.get("garment", "bottom")

    # 상의 착용 방식 — [2026-04-20 06:50 KST] 치마 인지 분기 추가
    # 원인: 기본값 "hem falls below the waistband"가 치마+티셔츠 조합에도 적용되어
    #       "waistband(바지 허리밴드)" 단어가 Gemini에게 바지 힌트로 오해됨
    # 수정: 하의가 치마일 때와 바지일 때의 용어를 분리
    #       - 치마: "waist line" / "skirt top" (허리 라인, 치마 윗단)
    #       - 바지: "waistband" 유지 (기존)
    if _is_skirt_out:
        # 치마와 함께 착용되는 상의
        if _top_cls == "outerwear":
            _top_wear = "Wear it open, with a simple plain tee underneath."
        elif _top_cls == "shirt" and top_info.get("garment") == "dress_shirt":
            _top_wear = "Tuck into the skirt waist line for a clean formal look."
        elif _top_cls == "shirt":
            _top_wear = "Leave untucked with natural casual drape over the skirt."
        else:
            _top_wear = "Worn over the skirt with natural drape, hem falling around hip level."
    else:
        # 바지/반바지와 함께 착용되는 상의 (기존 로직 유지)
        if _top_cls == "outerwear":
            _top_wear = "Wear it open, with a simple plain tee underneath."
        elif _top_cls == "shirt" and top_info.get("garment") == "dress_shirt":
            _top_wear = "Tuck neatly into the bottom for a clean formal look."
        elif _top_cls == "shirt":
            _top_wear = "Leave untucked with natural casual drape."
        else:
            _top_wear = "Wear naturally — hem falls to hip level."

    # 하의 착용 방식 — [2026-04-20 03:52 KST] _top_wear와 병렬 구조
    # [2026-04-20 06:50 KST] 치마 분기에서 "waistband" 단어 제거
    #   → 치마에 이 용어는 바지 허리밴드를 암시. "waist line" / "skirt top"으로 교체
    # 역할: 치마/반바지/바지별로 상의와의 관계(tuck 여부, 허리 노출, 커프 등)를 지정
    if _is_skirt_out:
        _bot_wear = (
            "Skirt sits at the natural waist line; top hem layers OVER the skirt top naturally "
            "(never tucked INTO the skirt unless it's a dress shirt). "
            "Skirt upper edge partially visible if top is short, hidden if top is long."
        )
    elif _is_shorts_out:
        _bot_wear = (
            "Shorts sit at the natural waist; top may be tucked or untucked per top style. "
            "No cuff roll unless reference image shows it."
        )
    else:
        # 바지 — 기존 로직 유지 ("waistband" 용어는 바지에 적절)
        if _top_cls == "shirt" and top_info.get("garment") == "dress_shirt":
            _bot_wear = "Dress shirt tucked INTO the pants; belt line visible at the waist."
        elif _top_cls == "outerwear":
            _bot_wear = "Pants worn naturally at waist; outerwear falls over the top without tuck."
        else:
            _bot_wear = (
                "Pants at natural waist; top hem layers OVER the waistband "
                "(tuck only if reference clearly shows tucked styling). "
                "No rolled cuffs unless reference shows them."
            )

    # 하의 분기 — 치마 / 반바지 / 바지
    if _is_skirt_out:
        _bot_rule = (
            f"Skirt only — a {_bot_en}. No pants, no leggings, no leg tubes under or instead of the skirt. "
            f"{_skirt_ratio_hint if _skirt_ratio_hint else ''}"
            "Fabric drapes naturally with visible weight, hip-conforming curve, and soft hem movement."
        )
    elif _is_shorts_out:
        _bot_rule = f"Shorts with hem above the knee. Natural drape, matching the reference exactly."
    else:
        _skinny_rule = (
            "Skinny/slim fit — leg opening 6-8cm, fabric conforms to thigh and calf, visible leg contour. "
            if _is_skinny else
            "Regular fit — straight cut, leg opening 18-22cm, relaxed drape. Trouser hem covers the ankle bone (no bare ankle). "
        )
        _bot_rule = _skinny_rule + "Preserve the reference pants design exactly."

    # ── [2026-04-20 06:50 KST] 포즈 지시 — 성별 + 치마 여부 분기 ──────────────
    # 원인: 이전에는 "thighs naturally touching (no gap between legs)" 단일 지시였음
    #       이 문구는 허벅지가 드러나 보임을 암시 → 치마 레퍼런스일 때 Gemini가
    #       "맨다리 = 바지"로 오해하는 힌트가 됨. 남녀 모두 동일 포즈라 여성 편향 문제.
    # 수정: 여성 + 치마, 여성 + 바지, 남성 3가지 분기로 자연스러운 포즈 지시
    #   - 여성 + 치마: knees together (치맛자락 자연스럽게 흐름, thighs touching 언급 금지)
    #   - 여성 + 바지: feet 5-8cm apart + thighs touching (기존 여성스러운 스탠스)
    #   - 남성:         feet shoulder-width (15-25cm), weight evenly, 자연스러운 스탠스
    if gender == "F" and _is_skirt_out:
        _pose_rule = (
            "Pose: feminine editorial stance — stands facing camera, "
            "feet together or one foot slightly forward (heels 2-5cm apart), "
            "knees together for elegant skirt silhouette, "
            "subtle contrapposto with weight on one leg, "
            "arms relaxed at sides with natural elbow curve, "
            "shoulders relaxed and level, soft confident expression. "
        )
    elif gender == "F":
        _pose_rule = (
            "Pose: feminine editorial stance — stands facing camera, "
            "feet 5-8cm apart with toes slightly outward, thighs naturally touching, "
            "arms relaxed at sides with slight elbow curve, "
            "subtle contrapposto, soft confident expression. "
        )
    else:
        _pose_rule = (
            "Pose: masculine editorial stance — stands facing camera squarely, "
            "feet shoulder-width apart (15-25cm), toes straight or slightly outward, "
            "weight evenly distributed on both legs, "
            "arms hanging naturally at sides, shoulders slightly back and relaxed, "
            "confident direct gaze. "
        )

    # ── 최종 프롬프트 조립 ──
    prompt = (
        # [SYSTEM]
        "You are CodiBank's AI Virtual Fitting Stylist — a Korean fashion photography expert. "
        "Generate ONE photorealistic full-body outfit image by fitting the provided garments onto the provided person. "
        "Follow the 5 phases below in order. "

        # [PHASE 1] PERSONA & BODY — [2026-04-20 03:52 KST] 퍼스널컬러 summary 추가
        "\n\n[PHASE 1 — PERSONA]: "
        + face_line
        + "\n" + _build_body_profile_block(gender, age, height, weight, _body_type_key, "en")
        + (f"\nPersonal color: {_pc_season} ({_pc_undertone}). "
           f"Best palette: {_pc_best_colors}. Avoid: {_pc_avoid_colors}. "
           + (f"Summary: {_pc_summary}. " if _pc_summary else "")
           if _pc_season else "")
        + " Fit both garments realistically to this exact body shape with natural draping and fabric weight. "

        # [PHASE 2] GARMENTS — AI옷장/Phase1 분석 결과를 직접 주입
        + "\n\n[PHASE 2 — GARMENTS]: Reference images are the ABSOLUTE GROUND TRUTH for color, pattern, and design. "
        + f"\nTOP = {_top_ko} ({_top_en}). "
        + (f"Color: {top_info.get('color_ko','')}. " if top_info.get('color_ko') else "")
        + (f"Pattern: {top_info.get('pattern','')}. " if top_info.get('pattern') and top_info.get('pattern') != '단색' else "")
        + (f"Material: {top_info.get('material','')}. " if top_info.get('material') else "")
        + (f"Design: {top_info.get('design','')}. " if top_info.get('design') else "")
        + "Reproduce the EXACT neckline, sleeve length/cuff, buttons, trim, hemline, and any layered/contrast details visible in the reference image. "
        + (
            "If the reference shows a 2-fabric layered construction (e.g., contrast trim at collar/sleeve/hem, inner lining showing), "
            "reproduce BOTH fabrics exactly where they meet. "
        )
        + f"\nBOTTOM = {_bot_ko} ({_bot_en}). "
        + (f"Color: {bottom_info.get('color_ko','')}. " if bottom_info.get('color_ko') else "")
        + (f"Pattern: {bottom_info.get('pattern','')}. " if bottom_info.get('pattern') and bottom_info.get('pattern') != '단색' else "")
        + (f"Material: {bottom_info.get('material','')}. " if bottom_info.get('material') else "")
        + (f"Silhouette: {bottom_info.get('silhouette','')}. " if bottom_info.get('silhouette') else "")
        + _bot_rule

        # [PHASE 3] WEARING — [2026-04-20 03:52 KST] 상/하의 착용방식 병렬 주입
        + "\n\n[PHASE 3 — WEARING]: "
        + f"Top wearing: {_top_wear} "
        + f"Bottom wearing: {_bot_wear} "
        + "Both garments must show realistic draping, body-conforming curves, fabric shadows, and 3D volume (not flat 2D overlays). "

        # [PHASE 4] IMAGE COMPOSITION
        + "\n\n[PHASE 4 — IMAGE]: "
        + "Photorealistic Korean fashion lookbook photo. Full body visible, head to feet. "
        + _pose_rule
        + "Footwear: shoes fully visible and must match the outfit style "
        + ("(heels, flats, or loafers for feminine; " if gender == "F" else "(sneakers, loafers, or dress shoes; ")
        + "never crop at ankles). "
        + ("Background: flat solid pastel complementing " + f"{_pc_season} {_pc_undertone}" + ", contrasting with the outfit. "
           if _pc_season else
           "Background: single flat solid pastel (light for dark outfits, deeper for light outfits). ")
        + "Professional natural-light editorial lighting. No text, no watermarks, no scenery. "
        + "Safety: person fully clothed, no nudity, no sexualized poses. "

        # [PHASE 5] EVALUATION — [2026-04-20 03:52 KST] Phase 1 근거 Phase 2/3 종합 분석
        # 원칙:
        #   - Phase 1 (PERSONA: 체형/BMI/퍼스널컬러/summary)을 평가의 "기준"으로 삼음
        #   - Phase 2 (GARMENTS)와 Phase 3 (WEARING)을 그 기준으로 종합 평가
        #   - 점수 3항목(personal_color 40 / body_shape 40 / coordination 20) 각각이
        #     Phase 1의 어느 속성을 근거로 하는지 명시
        + "\n\n[PHASE 5 — EVALUATION OUTPUT — REQUIRED TEXT RESPONSE]: "
        + "After generating the image, EVALUATE the outfit. "
        + "The evaluation framework: use PHASE 1 (persona, body profile, personal color) as the REFERENCE CRITERIA, "
        + "and judge PHASE 2 (garments) combined with PHASE 3 (wearing style) against that reference. "
        + "Each score must be directly justified by Phase 1 attributes. "
        + "Output MUST contain the following lines exactly. "

        # 점수 (100점 만점, 3개 합산) — 각 항목이 Phase 1의 어느 요소를 근거로 하는지 명시
        + "\nOUTPUT LINE 1 — SCORE (must sum to 100): "
        + "STYLING_SCORE:[total]/100|personal_color:[n1]/40|body_shape:[n2]/40|coordination:[n3]/20 "
        + "where n1<=40, n2<=40, n3<=20, n1+n2+n3=total. "
        + "\nScoring basis (anchor each score to Phase 1): "
        + (
            f"• personal_color/40 — compare PHASE 2 garment colors against PHASE 1 palette "
            f"(season={_pc_season}, undertone={_pc_undertone}, best={_pc_best_colors}, avoid={_pc_avoid_colors}"
            + (f", summary='{_pc_summary}'" if _pc_summary else "")
            + "). "
            if _pc_season else
            "• personal_color/40 — general color harmony (personal color data not available). "
        )
        + (
            f"• body_shape/40 — compare PHASE 2 silhouette + PHASE 3 wearing style against PHASE 1 body profile "
            f"(type={_body_type_key}). " + _build_body_type_prompt(gender, _body_type_key) + " "
            if _body_type_key else
            "• body_shape/40 — general proportion evaluation. "
        )
        + "• coordination/20 — evaluate top+bottom color/pattern/style coherence and PHASE 3 wearing execution (tuck, drape, layering). "
        + f"\nUser: {gender_en}, {age}" + (f", {hw_en}" if hw_en else "") + ". "

        # 5개 분석 섹션 (한/영 분기) — 각 섹션 500자 이내, 보고서 형식 ▸ 불릿 4~5개
        # 각 섹션은 Phase 1 근거를 명시하여 작성
        + (
            "\nOUTPUT LINE 2+ — ANALYSIS (English, report format with bullet points ▸): "
            "Each of the 5 sections below is REQUIRED and must ANCHOR its judgment to PHASE 1 (persona/body/personal color). "
            "Each section MUST start with its label exactly as written, contain 4-5 bullet points starting with '▸', and be under 500 characters. "
            "Use 'color-name #HEX' format for all color mentions (e.g., 'Navy #1B3A5F'). "
            "\n퍼스널컬러 분석: [▸ PHASE 1 season type vs PHASE 2 colors · ▸ top/bottom harmony with #HEX · ▸ best/avoid palette match · ▸ summary-based styling tip] "
            "\n상의 스타일 분석: [▸ material/pattern/fit · ▸ neckline/sleeve/trim details from PHASE 2 · ▸ color with #HEX · ▸ PHASE 1 body-type synergy · ▸ improvement note] "
            "\n하의 스타일 분석: [▸ silhouette/length/material from PHASE 2 · ▸ color with #HEX · ▸ leg-line effect vs PHASE 1 body · ▸ top-bottom proportion (PHASE 3 wearing) · ▸ improvement note] "
            "  (CRITICAL: this 하의 section is MANDATORY — do NOT skip, do NOT merge with other sections) "
            "\n토탈 스타일링 분석: [▸ overall color combo with #HEX judged by PHASE 1 · ▸ proportion verdict vs body type · ▸ TPO fit · ▸ improvement suggestion] "
            "\n핵심 키워드: [EXACTLY 5 keywords separated by commas, each 1-3 words, capturing outfit essence, e.g., 'Minimal Chic, Soft Spring, Structured Fit, Layered Tone, Daily Formal']"
            if _cs_en else
            "\nOUTPUT LINE 2+ — 분석 (한국어, 반드시 보고서 형식 ▸ 불릿 사용): "
            "아래 5개 섹션 모두 필수이며, 각 섹션의 판단은 PHASE 1 (퍼소나/체형/퍼스널컬러)을 근거로 해야 함. "
            "각 섹션은 라벨로 정확히 시작, ▸ 불릿 4~5개, 500자 이내. 모든 컬러는 '컬러명 #HEX' 형식. "
            "\n퍼스널컬러 분석: [▸ PHASE 1 시즌 타입 vs PHASE 2 컬러 · ▸ 상의/하의 조화(#HEX) · ▸ 추천/회피 팔레트 부합 · ▸ summary 기반 팁] "
            "\n상의 스타일 분석: [▸ 소재/패턴/핏 · ▸ PHASE 2의 넥라인/소매/트림 · ▸ 컬러(#HEX) · ▸ PHASE 1 체형 시너지 · ▸ 개선 포인트] "
            "\n하의 스타일 분석: [▸ PHASE 2의 실루엣/기장/소재 · ▸ 컬러(#HEX) · ▸ PHASE 1 체형 기준 다리라인 효과 · ▸ PHASE 3 착용방식 기반 상하 비율 · ▸ 개선 포인트] "
            "  (반드시 작성: 이 '하의' 섹션은 필수이며 생략 또는 다른 섹션과 병합 금지) "
            "\n토탈 스타일링 분석: [▸ PHASE 1 기준 전체 배색(#HEX) · ▸ 체형 대비 비율 평가 · ▸ TPO 적합성 · ▸ 개선 제안] "
            "\n핵심 키워드: [정확히 5개, 쉼표 구분, 각 2~6자. 예: '미니멀시크, 봄웜톤, 스트럭처드핏, 레이어드톤, 데일리포멀']"
        )

        # 다시요청
        + (" Retry note: vary pose slightly; maintain garment identity." if is_retry else "")
    )

    # ── Gemini API 호출 (신/구 SDK 분기) ──
    try:
        if _SDK == "new":
            # ★ google-genai (신규 공식 SDK) ★
            contents = [prompt]
            if face_bytes:
                contents.append(_gtypes.Part.from_bytes(data=face_bytes, mime_type=face_mime or "image/jpeg"))
            contents.append(_gtypes.Part.from_bytes(data=top_bytes,    mime_type=top_mime    or "image/jpeg"))
            contents.append(_gtypes.Part.from_bytes(data=bottom_bytes, mime_type=bottom_mime or "image/jpeg"))

            client = _genai.Client(api_key=_GEMINI_KEY)
            response = client.models.generate_content(
                model=_CODISTYLE_MODEL,
                contents=contents,
                config=_gtypes.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    temperature=0.7,
                ),
            )
        else:
            # ★ google-generativeai (구 SDK, 이미 설치됨) ★
            from PIL import Image as _PILImage
            _genai_old.configure(api_key=_GEMINI_KEY)
            model = _genai_old.GenerativeModel(_CODISTYLE_MODEL)

            # bytes → PIL Image 변환
            def _bytes_to_pil(raw):
                return _PILImage.open(io.BytesIO(raw))

            contents_old = [prompt]
            if face_bytes:
                contents_old.append(_bytes_to_pil(face_bytes))
            contents_old.append(_bytes_to_pil(top_bytes))
            contents_old.append(_bytes_to_pil(bottom_bytes))

            # 구 SDK에서 response_modalities 지원 여부 불확실
            # → dict 방식으로 전달 시도 → 실패하면 GenerationConfig 방식
            try:
                response = model.generate_content(
                    contents_old,
                    generation_config={
                        "response_modalities": ["IMAGE", "TEXT"],
                        "temperature": 0.7,
                    },
                )
            except TypeError:
                # dict 방식 실패 시 GenerationConfig 객체 사용
                response = model.generate_content(
                    contents_old,
                    generation_config=_genai_old.GenerationConfig(
                        temperature=0.7,
                    ),
                )
    except Exception as e:
        return jsonify(ok=False, error=f"Gemini 호출 실패 ({_SDK}): {str(e)[:300]}"), 500

    # ── 응답에서 이미지 추출 ──
    img_bytes = None
    comment   = ""
    try:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                img_bytes = part.inline_data.data
                # SDK는 이미 bytes로 반환 (base64 디코딩 불필요)
            elif part.text:
                comment = part.text.strip()[:2000]
    except (IndexError, AttributeError) as e:
        return jsonify(ok=False, error=f"응답 파싱 실패: {str(e)[:200]}"), 500

    # [2026-04-08] FinishReason.STOP 시 1회 자동 재시도
    if not img_bytes:
        try:
            finish = response.candidates[0].finish_reason
        except Exception:
            finish = "UNKNOWN"
        _safe_comment = comment[:100] if comment else ""
        print(f"[codistyle] 이미지 미생성(1차): finishReason={finish}, comment={_safe_comment[:80]}")
        
        # 재시도 (temperature를 약간 변경하여 다른 결과 유도)
        if str(finish) in ("STOP", "FinishReason.STOP", "1", "2") and not request.args.get("_retried"):
            print("[codistyle] 자동 재시도 중...")
            try:
                # ──── [2026-04-19 BUGFIX #1] 재시도 블록 변수 이름 오류 수정 ────
                # 원인: contents_new, config_new 변수가 정의되지 않음 → NameError
                #       → 재시도 자체가 작동하지 않고 에러 메시지에 'STOP'이 없어
                #         프론트 자동 재시도 로직도 발동 안 함
                # 해결: 실제 정의된 변수(contents 또는 contents_old) 사용 +
                #       신/구 SDK 모두 지원 + temperature 0.85로 상승
                # ────
                if _SDK == "new":
                    response = client.models.generate_content(
                        model=_CODISTYLE_MODEL,
                        contents=contents,
                        config=_gtypes.GenerateContentConfig(
                            response_modalities=["IMAGE", "TEXT"],
                            temperature=0.85,
                        ),
                    )
                else:
                    # 구 SDK 재시도
                    try:
                        response = model.generate_content(
                            contents_old,
                            generation_config={
                                "response_modalities": ["IMAGE", "TEXT"],
                                "temperature": 0.85,
                            },
                        )
                    except TypeError:
                        response = model.generate_content(
                            contents_old,
                            generation_config=_genai_old.GenerationConfig(temperature=0.85),
                        )
                # 재시도 응답에서 이미지 추출
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        img_bytes = part.inline_data.data
                    elif part.text:
                        comment = part.text.strip()[:2000]
                if img_bytes:
                    print("[codistyle] 재시도 성공!")
            except Exception as _retry_e:
                print(f"[codistyle] 재시도 실패: {_retry_e}")
        
        if not img_bytes:
            return jsonify(ok=False, error=f"착장 이미지 생성에 실패했습니다. 다시 시도해주세요. (reason={finish})"), 500

    # img_bytes가 bytes인지 확인 (혹시 base64 문자열이면 디코딩)
    if isinstance(img_bytes, str):
        img_bytes = base64.b64decode(img_bytes)

    rel  = _write_upload_bytes("codistyle", "jpg", img_bytes)
    base = _public_base()

    # ── 스타일링 스코어 파싱 (새 형식: STYLING_SCORE:82/100|...) ──
    styling_score = None
    score_breakdown = {}
    styling_advice = ""
    try:
        import re as _re2
        # 총점
        _m = _re2.search(r'STYLING_SCORE:(\d+)/100', comment)
        if _m: styling_score = int(_m.group(1))
        # 3개 세부 점수
        for _k in ['personal_color', 'body_shape', 'overall_styling', 'coordination']:
            _km = _re2.search(rf'{_k}:(\d+)', comment)
            if _km: score_breakdown[_k] = int(_km.group(1))
        # 점수 합산이 100이 아닌 경우 정규화
        _sb = score_breakdown
        # coordination → overall_styling 매핑
        if 'coordination' in _sb and 'overall_styling' not in _sb:
            _sb['overall_styling'] = _sb.pop('coordination')
        _sum = _sb.get('personal_color',0)+_sb.get('body_shape',0)+_sb.get('overall_styling',0)
        if styling_score and _sum > 0 and _sum != styling_score:
            _r = styling_score / _sum
            _sb['personal_color'] = round(_sb.get('personal_color',0)*_r)
            _sb['body_shape']     = round(_sb.get('body_shape',0)*_r)
            _sb['overall_styling']= styling_score - _sb['personal_color'] - _sb['body_shape']
        # 4개 섹션 분석 텍스트 추출
        _score_line_end = _re2.search(r'STYLING_SCORE:[^\n]+', comment)
        if _score_line_end:
            _advice_raw = comment[_score_line_end.end():].strip()
            styling_advice = _advice_raw[:600] if _advice_raw else ""
    except Exception:
        pass

    garment_summary = {
        "top": {"key": top_category_key, "ko": top_info.get("ko",""), "garment": top_info.get("garment","")},
        "bottom": {"key": bottom_category_key, "ko": bottom_info.get("ko",""), "garment": bottom_info.get("garment",""), "is_skirt": bottom_info.get("is_skirt",False)},
    }

    return jsonify(
        ok=True, path=rel,
        image=f"{base}{rel}", url=f"{base}{rel}",
        comment=comment or "AI 착장 이미지 생성 완료!",
        styling_score=styling_score,
        score_breakdown=score_breakdown,
        styling_advice=styling_advice,
        garment_summary=garment_summary,
        model=_CODISTYLE_MODEL,
        sdk=_SDK,
    )

# ── 관리자 인증 헬퍼 ──
# ════════════════════════════════════════════════════
# 멀티 어드민 시스템
# ════════════════════════════════════════════════════
import json as _json

# 어드민 계정 인메모리 DB
# 구조: { "email": { "role": "MASTER"|"SUB", "hash": sha256, "permissions": [...], "created_at": "" } }
_ADMIN_DB: dict = {}

def _admin_db_key() -> str:
    return "CB_ADMIN_ACCOUNTS_JSON"

def _init_admin_db():
    global _ADMIN_DB
    raw = os.environ.get(_admin_db_key(), "")
    if raw:
        try:
            _ADMIN_DB = _json.loads(raw)
            return
        except Exception:
            pass
    # 기본 마스터 계정: admin@codibank.kr / pass1234
    # ★ Render ADMIN_PW_HASH가 구버전(password 해시) 일 수 있으므로
    #   pass1234 해시를 코드 기본값으로 고정하고, 구버전 해시는 무시
    _PASS1234_HASH = "bd94dcda26fccb4e68d6a31f9b5aac0b571ae266d822620e901ef7ebe3a11d4f"
    _OLD_DEFAULT   = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    _env_hash = os.environ.get("ADMIN_PW_HASH", "")
    # 환경변수가 구버전(password)이거나 비어있으면 pass1234 해시 사용
    master_hash = _env_hash if (_env_hash and _env_hash != _OLD_DEFAULT) else _PASS1234_HASH
    _ADMIN_DB = {
        "admin@codibank.kr": {
            "role": "MASTER",
            "hash": master_hash,
            "permissions": ["all"],
            "created_at": "",
            "name": "마스터 관리자",
        }
    }

_init_admin_db()


def _auto_sync_master_to_supabase():
    """서버 시작 5초 후 MASTER 계정을 Supabase에 자동 동기화.
    CodiBank 앱(Supabase 로그인)에서도 admin@codibank.kr / pass1234 로 로그인 가능.
    """
    import threading as _th
    def _run():
        import time as _t2; _t2.sleep(5)
        try:
            import requests as _rq2
            _sb = supabase_url()
            _hdr = supabase_admin_headers()
            _PASS1234 = "bd94dcda26fccb4e68d6a31f9b5aac0b571ae266d822620e901ef7ebe3a11d4f"
            # 기존 Supabase 유저 uid 맵 가져오기
            lr = _rq2.get(f"{_sb}/auth/v1/admin/users?per_page=1000", headers=_hdr, timeout=15)
            uid_map = {}
            if lr.status_code == 200:
                ud = lr.json()
                ul = ud.get("users", ud) if isinstance(ud, dict) else ud
                for u in ul:
                    uid_map[u.get("email","").lower()] = u.get("id")
            # MASTER 계정만 동기화
            for em, info in list(_ADMIN_DB.items()):
                if info.get("role") != "MASTER":
                    continue
                pw = "pass1234"  # MASTER 기본 비밀번호
                sb_body = {
                    "email": em, "password": pw, "email_confirm": True,
                    "user_metadata": {"email": em, "nickname": info.get("name", em),
                                      "plan": "free", "role": "admin"},
                    "app_metadata":  {"provider": "email", "providers": ["email"]},
                }
                uid = uid_map.get(em.lower())
                if uid:
                    _rq2.put(f"{_sb}/auth/v1/admin/users/{uid}", headers=_hdr,
                             json={"password": pw, "email_confirm": True,
                                   "user_metadata": sb_body["user_metadata"]}, timeout=15)
                else:
                    _rq2.post(f"{_sb}/auth/v1/admin/users", headers=_hdr,
                              json=sb_body, timeout=15)
        except Exception:
            pass
    _th.Thread(target=_run, daemon=True).start()

_auto_sync_master_to_supabase()


def _save_admin_db():
    """변경사항을 환경변수(인메모리)에 저장 — 재시작 전까지 유효."""
    os.environ[_admin_db_key()] = _json.dumps(_ADMIN_DB, ensure_ascii=False)

def _get_admin_by_hash(hash_val: str):
    """해시로 어드민 정보 반환."""
    for email, info in _ADMIN_DB.items():
        if info.get("hash") == hash_val:
            return email, info
    return None, None

ALL_TABS = ["dash", "users", "pay", "closet", "codi", "items"]

# 기본 마스터 해시 상수 (pass1234) — 서버 재시작 후에도 항상 유효
_MASTER_FALLBACK_HASH = "bd94dcda26fccb4e68d6a31f9b5aac0b571ae266d822620e901ef7ebe3a11d4f"

def _get_provided_key(req) -> str:
    return (req.args.get("key") or req.headers.get("X-Admin-Key") or "").strip()

def verify_admin(req) -> bool:
    """어드민 인증 — _ADMIN_DB → ADMIN_PW_HASH → MASTER_FALLBACK 순서로 확인."""
    provided = _get_provided_key(req)
    if not provided:
        return False
    # 1) _ADMIN_DB 해시 일치
    _, info = _get_admin_by_hash(provided)
    if info:
        return True
    # 2) 환경변수 ADMIN_PW_HASH
    env_hash = os.environ.get("ADMIN_PW_HASH", "")
    if env_hash and provided == env_hash:
        return True
    # 3) pass1234 고정 해시 (서버 재시작 후 세션 유지 보장)
    return provided == _MASTER_FALLBACK_HASH

def verify_master(req) -> bool:
    """MASTER 권한 어드민만 True — _ADMIN_DB → ADMIN_PW_HASH → MASTER_FALLBACK."""
    provided = _get_provided_key(req)
    if not provided:
        return False
    # 1) _ADMIN_DB에서 MASTER 역할 확인
    _, info = _get_admin_by_hash(provided)
    if info and info.get("role") == "MASTER":
        return True
    # 2) 환경변수 ADMIN_PW_HASH (마스터 해시와 일치하면 MASTER)
    env_hash = os.environ.get("ADMIN_PW_HASH", "")
    if env_hash and provided == env_hash:
        return True
    # 3) pass1234 고정 해시 — 서버 재시작 후에도 마스터 접근 보장
    return provided == _MASTER_FALLBACK_HASH

def supabase_admin_headers():
    """Supabase Admin API용 헤더 (service_role 키 사용)"""
    key = os.environ.get('SUPABASE_SERVICE_KEY', '')
    return {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

def supabase_url():
    return os.environ.get('SUPABASE_URL', 'https://drgsayvlpzcacurcczjq.supabase.co')


# ══════════════════════════════════════
# Admin API 엔드포인트
# ══════════════════════════════════════

@app.get("/admin/users")
def admin_list_users():
    """유저 목록 조회"""
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        url = f"{supabase_url()}/auth/v1/admin/users?per_page=500"
        r = http_requests.get(url, headers=supabase_admin_headers(), timeout=10)
        if r.status_code != 200:
            return jsonify({"error": f"Supabase error: {r.status_code}", "detail": r.text}), r.status_code
        data = r.json()
        users = data.get('users', data) if isinstance(data, dict) else data
        return jsonify({"ok": True, "users": users, "total": len(users)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.delete("/admin/users/<uid>")
def admin_delete_user(uid):
    """유저 삭제"""
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        url = f"{supabase_url()}/auth/v1/admin/users/{uid}"
        r = http_requests.delete(url, headers=supabase_admin_headers(), timeout=10)
        if r.status_code not in (200, 204):
            return jsonify({"error": f"Supabase error: {r.status_code}", "detail": r.text}), r.status_code
        return jsonify({"ok": True, "deleted": uid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/admin/stats")
def admin_stats():
    """서비스 통계 (유저 수, 서버 상태 등)"""
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    stats = {"ok": True}
    # 유저 수
    try:
        url = f"{supabase_url()}/auth/v1/admin/users?per_page=1"
        r = http_requests.get(url, headers=supabase_admin_headers(), timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Supabase returns total in headers or body
            stats["total_users"] = len(data.get('users', []))
    except:
        stats["total_users"] = -1
    # R2 연결 상태
    try:
        import boto3
        s3 = boto3.client('s3',
            endpoint_url=os.environ.get('R2_ENDPOINT','') or (('https://'+os.environ.get('R2_ACCOUNT_ID','')+'.r2.cloudflarestorage.com') if os.environ.get('R2_ACCOUNT_ID','') else ''),
            aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID',''),
            aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY',''))
        bucket = os.environ.get('R2_BUCKET_NAME','codibank')
        resp = s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
        stats["r2_connected"] = True
        stats["r2_bucket"] = bucket
    except:
        stats["r2_connected"] = False
    # Gemini 키 상태
    stats["gemini_key_present"] = bool(os.environ.get('GEMINI_API_KEY',''))
    stats["gemini_model"] = os.environ.get('CODISTYLE_GEMINI_MODEL','not set')
    return jsonify(stats)

# ── Supabase DB 헬퍼 ──
def sb_query(method, table, params=None, body=None):
    """Supabase REST API로 DB 테이블 접근"""
    url = f"{supabase_url()}/rest/v1/{table}"
    if params:
        url += '?' + '&'.join(f'{k}={v}' for k, v in params.items())
    headers = supabase_admin_headers()
    headers['Prefer'] = 'return=representation'
    if method == 'GET':
        r = http_requests.get(url, headers=headers, timeout=10)
    elif method == 'POST':
        r = http_requests.post(url, headers=headers, json=body, timeout=10)
    elif method == 'DELETE':
        r = http_requests.delete(url, headers=headers, timeout=10)
    else:
        r = http_requests.request(method, url, headers=headers, json=body, timeout=10)
    return r


# ══════════════════════════════════════
# 사용자 데이터 동기화 API (Phase 1: 아이템 서버 동기화)
# ──── [2026-04-11 추가] ────
# 원인: 아이템/앨범 등이 localStorage에만 저장되어 기기 변경 시 소실
# 해결: R2에 사용자별 JSON 파일로 저장 → 로그인 시 복원
# 관련파일: codibank.js (syncItemsToServer, syncItemsFromServer)
# ════════════════════════════════════

@app.post("/api/user-data/save")
def user_data_save():
    """사용자 데이터를 R2에 JSON으로 저장"""
    try:
        payload = request.get_json(silent=True) or {}
        email = str(payload.get("email") or "").strip().lower()
        data_key = str(payload.get("key") or "").strip()
        data_value = payload.get("value")

        if not email or not data_key:
            return jsonify(ok=False, error="email과 key가 필요합니다."), 400
        if data_key not in ("items", "album", "profile_extra"):
            return jsonify(ok=False, error="허용되지 않는 키입니다."), 400

        import hashlib, json
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:16]
        fname = f"userdata_{email_hash}_{data_key}.json"
        json_bytes = json.dumps(data_value, ensure_ascii=False).encode("utf-8")

        # R2 저장
        r2_ok = False
        r2_result = _upload_to_r2(fname, json_bytes, "application/json")
        if r2_result:
            r2_ok = True

        # 로컬 폴백
        fpath = os.path.join(_UPLOAD_DIR, fname)
        with open(fpath, "wb") as f:
            f.write(json_bytes)

        print(f"[user-data] 저장 완료: {email} / {data_key} ({len(json_bytes)}B, R2={'✅' if r2_ok else '❌ 로컬만'})")
        return jsonify(ok=True, r2=r2_ok, size=len(json_bytes))
    except Exception as e:
        print(f"[user-data] 저장 실패: {e}")
        return jsonify(ok=False, error=str(e)), 500


@app.get("/api/user-data/load")
def user_data_load():
    """사용자 데이터를 R2/로컬에서 로드"""
    try:
        email = str(request.args.get("email") or "").strip().lower()
        data_key = str(request.args.get("key") or "").strip()

        if not email or not data_key:
            return jsonify(ok=False, error="email과 key가 필요합니다."), 400

        import hashlib, json
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:16]
        fname = f"userdata_{email_hash}_{data_key}.json"

        json_bytes = None

        # 1순위: 로컬 파일
        fpath = os.path.join(_UPLOAD_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                json_bytes = f.read()

        # 2순위: R2
        if not json_bytes and _R2_PUB_URL:
            try:
                import requests as _rq
                r = _rq.get(f"{_R2_PUB_URL}/uploads/{fname}", timeout=10)
                if r.status_code == 200:
                    json_bytes = r.content
            except Exception:
                pass

        if not json_bytes:
            return jsonify(ok=True, value=None, found=False)

        data = json.loads(json_bytes.decode("utf-8"))
        return jsonify(ok=True, value=data, found=True)
    except Exception as e:
        print(f"[user-data] 로드 실패: {e}")
        return jsonify(ok=False, error=str(e)), 500


# ══════════════════════════════════════
# A) 프론트엔드 추적 API (인증 불필요 - 이용자 호출용)
# ══════════════════════════════════════

@app.post("/api/track/payment")
def track_payment():
    """결제 완료 시 프론트에서 호출"""
    try:
        d = request.get_json(force=True)
        body = {
            'user_id': d.get('user_id') or None,
            'email': d.get('email', ''),
            'plan_id': d.get('plan_id', ''),
            'plan_name': d.get('plan_name', ''),
            'amount': d.get('amount', 0),
            'currency': d.get('currency', 'KRW'),
            'points_granted': d.get('points_granted', 0),
            'imp_uid': d.get('imp_uid', ''),
            'merchant_uid': d.get('merchant_uid', ''),
            'status': 'completed'
        }
        r = sb_query('POST', 'payments', body=body)
        if r.status_code in (200, 201):
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": r.text}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.post("/api/track/styling")
def track_styling():
    """스타일링 사용 시 프론트에서 호출"""
    try:
        d = request.get_json(force=True)
        body = {
            'user_id': d.get('user_id') or None,
            'email': d.get('email', ''),
            'type': d.get('type', 'codistyle'),
            'points_used': d.get('points_used', 100),
            'gender': d.get('gender', ''),
            'purpose': d.get('purpose', ''),
            'plan': d.get('plan', 'free')
        }
        r = sb_query('POST', 'styling_logs', body=body)
        if r.status_code in (200, 201):
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": r.text}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500



@app.post("/api/ai/analyze-item")
def ai_analyze_item():
    """
    의류 아이템 이미지를 Gemini Vision으로 분석:
    카테고리, 메인컬러(HEX), 패턴, 소재, 핏, 디자인 포인트, 스타일 키워드
    """
    if not _GEMINI_KEY:
        return jsonify(ok=False, error="GEMINI_API_KEY 미설정"), 400

    try:
        d = request.get_json(force=True) or {}
        image_data = d.get("image")          # base64 또는 URL
        image_url  = d.get("image_url", "")  # /uploads/ 경로

        if not image_data and not image_url:
            return jsonify(ok=False, error="이미지 없음"), 400

        # ── 이미지 데이터 준비 ──
        img_bytes = None
        img_mime  = "image/jpeg"

        if image_data:
            # base64 dataURL
            import base64
            if "," in image_data:
                header, b64 = image_data.split(",", 1)
                if "png" in header: img_mime = "image/png"
                elif "webp" in header: img_mime = "image/webp"
            else:
                b64 = image_data
            img_bytes = base64.b64decode(b64)

        elif image_url:
            # /uploads/ 경로 → R2 또는 로컬에서 로드
            import requests as _rq
            _backend = request.host_url.rstrip("/")
            full_url = image_url if image_url.startswith("http") else _backend + image_url
            resp = _rq.get(full_url, timeout=10)
            if resp.status_code == 200:
                img_bytes = resp.content
                ct = resp.headers.get("content-type", "image/jpeg")
                img_mime = ct.split(";")[0].strip()
            else:
                return jsonify(ok=False, error="이미지 로드 실패"), 400

        if not img_bytes:
            return jsonify(ok=False, error="이미지 데이터 없음"), 400

        # ── [STEP 1] rembg: 업로드 시 이미 처리됨 → 스킵 ──
        # (rembg를 여기서 다시 호출하면 HF Space 대기 누적으로 타임아웃 발생)

        # ── [STEP 2] Lykdat: 속성 태깅 ──
        lykdat_data = lykdat_tag_item(img_bytes)

        # ──── [2026-04-19 PERF] Marqo 임베딩 생성 — 코디하기 Phase1에서는 스킵 ────
        # 원인: Marqo FashionSigLIP 임베딩(512차원)은 모바일옷장 유사도 매칭 전용
        #       코디하기 Phase1에서는 is_skirt/sub_category/디자인 정보만 필요
        #       torch 로컬 연산으로 의류당 1~3초 소요 → 완전 낭비
        # 해결: skip_embedding=True 플래그로 이 STEP 3를 건너뛸 수 있게 함
        #       - 모바일옷장 등록(item.html): 플래그 없음 → 기존대로 임베딩 생성
        #       - 코디하기 Phase1(codistyle_analyze_garments): 플래그 True → 스킵
        # ────
        _skip_embedding = bool(d.get("skip_embedding", False))
        if _skip_embedding:
            fashion_embedding = None
            print("[analyze-item] skip_embedding=True → Marqo 임베딩 스킵 (코디하기 Phase1)")
        else:
            # ── [STEP 3] Marqo: 임베딩 생성 ──
            fashion_embedding = get_fashion_embedding(img_bytes)

        # ── img_bytes 최소 크기 검증 ──
        if not img_bytes or len(img_bytes) < 100:
            return jsonify(ok=False, error="이미지 데이터가 너무 작거나 없습니다"), 400

        # ── [STEP 4] Gemini 프롬프트에 Lykdat 컨텍스트 추가 ──
        _lykdat_ctx = ""
        if lykdat_data:
            _lykdat_ctx = f"""
[사전 분석 데이터 - 참고하여 더 정확하게 보완하세요]
카테고리: {lykdat_data.get('lykdat_category','미확인')}
주요 컬러: {lykdat_data.get('lykdat_color_name','미확인')} {lykdat_data.get('lykdat_color_hex','')}
패턴: {lykdat_data.get('lykdat_pattern','미확인')}
실루엣: {lykdat_data.get('lykdat_silhouette','미확인')}
"""

        # ── Gemini Vision 프롬프트 ──
        PROMPT = _lykdat_ctx + """
당신은 세계 최고의 패션 전문가 AI입니다.
이 의류 이미지를 분석하고 아래 JSON 형식으로만 응답하세요. JSON 외 다른 텍스트는 절대 포함하지 마세요.

⚠️ 배경 무시 규칙: 이미지에 바닥, 벽, 옷걸이, 손, 테이블 등 배경이 포함되어 있을 수 있습니다. 배경은 완전히 무시하고 의류 아이템 영역만 집중하여 분석하세요. 배경 색상을 의류 색상으로 착각하지 마세요.

⚠️ 치마/스커트 판별 CRITICAL RULE:
- 다리가 각각 분리된 통로(leg tube)가 있으면 → pants (바지류)
- 다리 분리 없이 한 장의 천이 아래로 퍼지면 → skirt (치마류) ← 착용샷이어도 동일하게 적용
- 폭이 넓어 바지처럼 보여도 leg separation 없으면 반드시 skirt
- 도트무늬/플리츠/티어드 등 디자인과 무관하게 구조로만 판별

{
  "category": "coat | jacket | top | pants | skirt | shoes | watch | scarf | socks | etc 중 하나 — ⚠️ 치마/스커트류는 반드시 skirt, 절대 pants에 포함하지 말 것",
  "sub_category": "아래 세부 품목 중 하나로 정확히 분류:\n코트류: 반코트/롱코트/패딩코트/트렌치코트/더플코트/케이프코트\n자켓류: 수트자켓/콤비자켓/일반자켓/레더자켓/사파리자켓/데님자켓/집업자켓/후드집업자켓/패딩자켓/다운자켓/가디건/볼레로\n상의: 티셔츠/반팔티/긴팔티/셔츠/블라우스/니트/스웨터/후드티/맨투맨\n바지류: 청바지/슬랙스/면바지/스키니/와이드팬츠/조거팬츠/반바지/레깅스\n치마류: 미니스커트/미디스커트/롱스커트/플리츠스커트/A라인스커트/랩스커트/티어드스커트/도트스커트",
  "is_skirt": "true if category=skirt, false otherwise — ⚠️ 이 필드가 착장이미지 생성에 직접 사용됩니다",
  "skirt_length": "mini(무릎위) | midi(무릎~종아리중간) | maxi(종아리~발목) | null(치마아닌경우)",
  "main_color": "#RRGGBB 형식의 주요 색상 HEX",
  "main_color_name": "색상 이름 (한국어)",
  "sub_color": "#RRGGBB 또는 null",
  "sub_color_name": "보조 색상 이름 (한국어) 또는 null",
  "pattern": "단색|스트라이프|체크|도트|플로럴|기하학|카무플라주|그래픽|레터링|애니멀|페이즐리|추상 중 하나",
  "material": "면|린넨|울|캐시미어|실크|폴리에스터|나일론|데님|가죽|니트|혼방|기타 중 하나 이상 (쉼표 구분)",
  "fit": "오버사이즈|루즈|레귤러|슬림|스키니 중 하나",
  "season": "봄여름|가을겨울|사계절|여름전용|겨울전용 중 하나",
  "style_keywords": ["캐주얼|포멀|스트릿|미니멀|빈티지|스포티|로맨틱|클래식 중 최대 3개"],
  "design_points": "이 아이템의 디자인 특징 1~2문장 (한국어) — 착용샷이면 의류 아이템만 묘사",
  "coordinate_hint": "이 아이템과 잘 어울리는 하의/상의/아우터 추천 (한국어 1문장)"
}

분석 기준:
- 착용샷(사람이 입은 사진)이어도 의류 아이템 자체만 분석
- 배경과 착용자 신체 무시, 의류 구조에만 집중
- 치마류(skirt)는 category를 반드시 skirt로, is_skirt를 true로 설정
- 반드시 유효한 JSON만 반환
"""

        # ── Gemini SDK 호출 (codistyle_generate와 동일 방식) ──
        _SDK = None
        try:
            from google import genai as _gmod
            from google.genai import types as _gtypes
            _SDK = "new"
        except ImportError:
            pass
        if not _SDK:
            try:
                import google.generativeai as _gmod
                _SDK = "old"
            except ImportError:
                pass
        if not _SDK:
            return jsonify(ok=False, error="Gemini SDK 없음"), 500

        result_text = None

        if _SDK == "new":
            _cli = _gmod.Client(api_key=_GEMINI_KEY)
            _img_part = _gtypes.Part.from_bytes(data=img_bytes, mime_type=img_mime)
            _resp = _cli.models.generate_content(
                model=_CODISTYLE_MODEL,
                contents=[_gtypes.Content(parts=[_img_part, _gtypes.Part.from_text(text=PROMPT)])],
            )
            result_text = _resp.text if hasattr(_resp, "text") else str(_resp)
        else:
            _gmod.configure(api_key=_GEMINI_KEY)
            import PIL.Image as _PILImage
            import io
            _pil = _PILImage.open(io.BytesIO(img_bytes))
            _model = _gmod.GenerativeModel("gemini-1.5-flash")
            _resp = _model.generate_content([PROMPT, _pil])
            result_text = _resp.text

        # ── JSON 파싱 ──
        import json, re as _re
        result_text = result_text.strip()
        # 마크다운 코드블록 제거
        result_text = _re.sub(r"```json\s*", "", result_text)
        result_text = _re.sub(r"```\s*", "", result_text)
        result_text = result_text.strip()

        try:
            analysis = json.loads(result_text)
        except json.JSONDecodeError:
            # 중괄호 사이만 추출
            m = _re.search(r"\{.*\}", result_text, _re.DOTALL)
            if m:
                analysis = json.loads(m.group())
            else:
                return jsonify(ok=False, error="JSON 파싱 실패", raw=result_text[:300]), 500

        # ── 결과 병합: Lykdat + 임베딩 추가 ──
        if lykdat_data:
            # Lykdat 데이터로 빈 필드 보완 (Gemini 결과 우선)
            if not analysis.get("main_color") and lykdat_data.get("lykdat_color_hex"):
                analysis["main_color"] = lykdat_data["lykdat_color_hex"]
            if not analysis.get("pattern") and lykdat_data.get("lykdat_pattern"):
                analysis["pattern"] = lykdat_data["lykdat_pattern"]
            analysis["_lykdat"] = lykdat_data  # 원본 Lykdat 데이터 보존

        if fashion_embedding:
            analysis["embedding"] = fashion_embedding  # 512차원 벡터

        # [2026-04-08] 퍼스널컬러 + 체형 호환성 평가
        pc_data = d.get("personalColor") or {}
        bt_key  = d.get("bodyType", "")
        bt_gender = d.get("gender", "")
        
        compatibility = {}
        
        item_color = analysis.get("main_color_name", "") or analysis.get("main_color", "")
        item_pattern = analysis.get("pattern", "")
        item_fit = analysis.get("fit", "")
        item_cat = analysis.get("category", "")
        item_sub = analysis.get("sub_category", "")
        
        # 퍼스널컬러 호환성
        if pc_data and pc_data.get("season"):
            pc_season = pc_data.get("season", "")
            pc_best = ", ".join((pc_data.get("best_color_names") or pc_data.get("best_colors") or [])[:4])
            pc_avoid = ", ".join((pc_data.get("avoid_color_names") or pc_data.get("avoid_colors") or [])[:3])
            compatibility["personal_color"] = {
                "season": pc_season,
                "best_colors": pc_best,
                "avoid_colors": pc_avoid,
                "item_color": item_color,
            }
        
        # 체형 호환성
        bt_info = _get_body_type_info(bt_gender, bt_key) if bt_key else None
        if bt_info:
            compatibility["body_type"] = {
                "type": bt_info["label"],
                "do_style": bt_info["do_style"],
                "dont_style": bt_info["dont_style"],
                "best_color": bt_info["best_color"],
                "worst_color": bt_info["worst_color"],
                "item_fit": item_fit,
                "item_category": item_sub or item_cat,
            }
        
        # GPT/Gemini로 종합 판단 (간단 텍스트)
        if compatibility:
            try:
                _compat_parts = []
                if compatibility.get("personal_color"):
                    pc = compatibility["personal_color"]
                    _compat_parts.append(
                        "퍼스널컬러(" + pc["season"] + "): "
                        "추천 컬러=" + pc["best_colors"] + ", "
                        "피해야 할 컬러=" + pc["avoid_colors"] + ". "
                        "이 아이템 컬러=" + pc["item_color"]
                    )
                if compatibility.get("body_type"):
                    bt = compatibility["body_type"]
                    _compat_parts.append(
                        "체형(" + bt["type"] + "): "
                        "추천=" + bt["do_style"] + ", "
                        "피해=" + bt["dont_style"] + ". "
                        "이 아이템=" + bt["item_fit"] + " " + bt["item_category"]
                    )
                
                _compat_prompt = (
                    "아래 사용자 정보와 아이템 정보를 보고, 이 아이템이 사용자에게 어울리는지 판단하세요.\n"
                    + "\n".join(_compat_parts)
                    + "\n\n아래 JSON으로만 응답:\n"
                    + '{"pc_score":0~100,"pc_comment":"퍼스널컬러 측면 한줄평(한국어)",'
                    + '"bt_score":0~100,"bt_comment":"체형 측면 한줄평(한국어)",'
                    + '"total_score":0~100,"total_comment":"종합 한줄평(한국어)"}'
                )
                
                if _SDK == "new":
                    _compat_resp = _cli.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[_compat_prompt],
                    )
                    _compat_text = _compat_resp.text.strip()
                else:
                    _compat_model = _gmod.GenerativeModel("gemini-2.0-flash")
                    _compat_resp = _compat_model.generate_content(_compat_prompt)
                    _compat_text = _compat_resp.text.strip()
                
                _compat_text = _re.sub(r"```json\s*", "", _compat_text)
                _compat_text = _re.sub(r"```\s*", "", _compat_text).strip()
                _compat_json = json.loads(_compat_text)
                compatibility["evaluation"] = _compat_json
            except Exception as _ce:
                print(f"[analyze-item] 호환성 평가 실패: {_ce}")
        
        if compatibility:
            analysis["compatibility"] = compatibility

        return jsonify(ok=True, analysis=analysis)

    except Exception as e:
        import traceback
        return jsonify(ok=False, error=str(e), trace=traceback.format_exc()[-500:]), 500




@app.post("/api/ai/match-wardrobe")
def ai_match_wardrobe():
    """
    내 옷장 아이템과 스타일링 이미지 유사도 매칭
    - 입력: styling_image(추천코디 이미지 URL), items(아이템 목록+임베딩)
    - 출력: 유사도 높은 순 아이템 최대 5개
    """
    try:
        d     = request.get_json(force=True) or {}
        style = d.get("styling_image", "")   # 추천코디 이미지 URL
        items = d.get("items", [])            # 임베딩 포함된 아이템 목록

        if not style:
            return jsonify(ok=False, error="스타일링 이미지 없음"), 400
        if not items:
            return jsonify(ok=False, error="아이템 목록 없음"), 400

        # 스타일링 이미지 → bytes
        if style.startswith("data:"):
            _, b64 = style.split(",", 1)
            style_bytes = base64.b64decode(b64)
        elif style.startswith("http"):
            resp = http_requests.get(style, timeout=10)
            style_bytes = resp.content
        else:
            # /uploads/ 상대 경로
            full_url = _public_base() + style
            resp = http_requests.get(full_url, timeout=10)
            style_bytes = resp.content

        # 스타일링 이미지 배경 제거 + 임베딩 생성
        style_clean = remove_clothing_bg(style_bytes)
        style_emb   = get_fashion_embedding(style_clean)

        if not style_emb:
            return jsonify(ok=False, error="스타일링 이미지 임베딩 실패"), 500

        # 각 아이템과 유사도 계산
        scored = []
        for item in items:
            emb = item.get("embedding")
            if not emb or len(emb) < 100:
                continue   # 임베딩 없는 아이템 스킵
            sim = cosine_similarity(style_emb, emb)
            scored.append({
                "id":         item.get("id", ""),
                "categoryKey":item.get("categoryKey", ""),
                "color":      item.get("color", ""),
                "note":       item.get("note", ""),
                "similarity": round(sim, 4),
                "match_pct":  round(sim * 100),
            })

        # 유사도 높은 순 정렬 → 상위 5개
        scored.sort(key=lambda x: -x["similarity"])
        top5 = scored[:5]

        return jsonify(ok=True, matches=top5, total_compared=len(scored))

    except Exception as e:
        import traceback
        return jsonify(ok=False, error=str(e),
                       trace=traceback.format_exc()[-400:]), 500


@app.post("/api/ai/personal-color")
def ai_personal_color():
    """[2026-04-08] Phase 2: 피부톤 수치 분석 + GPT-4o 12서브타입"""
    try:
        d = request.get_json(force=True) or {}
        image_data = d.get("image")
        if not image_data:
            return jsonify(ok=False, error="이미지 없음"), 400

        import base64 as _b64m
        if "," in image_data:
            header, b64 = image_data.split(",", 1)
            img_mime = "image/png" if "png" in header else "image/jpeg"
        else:
            b64 = image_data; img_mime = "image/jpeg"
        img_bytes = _b64m.b64decode(b64)

        # Phase 2: 피부톤 수치 분석
        skin_metrics = None
        enhanced_prompt = None
        if _HAS_SKIN_ANALYZER:
            try:
                skin_metrics = analyze_skin_tone(img_bytes)
                if skin_metrics.get("ok"):
                    enhanced_prompt = build_enhanced_prompt(skin_metrics)
                    print("[Phase2] skin: L*=" + str(skin_metrics["lab"]["L"]) + " ITA=" + str(skin_metrics["ita"]))
            except Exception as _e:
                print("[Phase2] error: " + str(_e))

        PROMPT = enhanced_prompt or _PC_FALLBACK_PROMPT

        _openai_key = os.environ.get("OPENAI_API_KEY", "")
        if not _openai_key:
            return _personal_color_gemini(img_bytes, img_mime, PROMPT)

        from openai import OpenAI as _OAI
        client = _OAI(api_key=_openai_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":[
                {"type":"image_url","image_url":{"url":"data:"+img_mime+";base64,"+b64,"detail":"high"}},
                {"type":"text","text":PROMPT}
            ]}],
            max_tokens=1200, temperature=0.1
        )
        result_text = resp.choices[0].message.content.strip()
        import json as _jm, re as _rem
        result_text = _rem.sub(r"```json\s*","",result_text)
        result_text = _rem.sub(r"```\s*","",result_text).strip()
        try: pc = _jm.loads(result_text)
        except _jm.JSONDecodeError:
            m = _rem.search(r"\{.*\}", result_text, _rem.DOTALL)
            pc = _jm.loads(m.group()) if m else {}

        resp_data = {"ok":True, "personal_color":pc, "phase": 2 if (skin_metrics and skin_metrics.get("ok")) else 1}
        if skin_metrics and skin_metrics.get("ok"):
            resp_data["skin_metrics"] = {"lab":skin_metrics["lab"],"ita":skin_metrics["ita"],"confidence":skin_metrics["confidence"]}
        return jsonify(resp_data)
    except Exception as e:
        import traceback
        return jsonify(ok=False, error=str(e), trace=traceback.format_exc()[-300:]), 500

_PC_FALLBACK_PROMPT = """당신은 전문 퍼스널컬러 컨설턴트입니다. 사진을 보고 퍼스널컬러를 분석하세요. JSON만 응답.
{"season":"봄웜|여름쿨|가을웜|겨울쿨","season_en":"영어","undertone":"웜톤|쿨톤","skin_tone":"밝은|중간|어두운","best_colors":["#HEX"x5],"best_color_names":["이름"x5],"avoid_colors":["#HEX"x3],"avoid_color_names":["이름"x3],"summary":"한줄요약","style_tip":"스타일팁 한국어"}
피부 언더톤, 밝기, 머리카락·눈동자 색상 종합 판단. 유효한 JSON만 반환."""


def _personal_color_gemini(img_bytes, img_mime, prompt):
    """퍼스널컬러 Gemini 폴백"""
    try:
        _SDK = None
        try:
            from google import genai as _gmod
            from google.genai import types as _gtypes
            _SDK = "new"
        except ImportError:
            try:
                import google.generativeai as _gmod
                _SDK = "old"
            except ImportError:
                pass
        if not _SDK:
            return jsonify(ok=False, error="AI SDK 없음"), 500

        if _SDK == "new":
            _cli = _gmod.Client(api_key=_GEMINI_KEY)
            _img_part = _gtypes.Part.from_bytes(data=img_bytes, mime_type=img_mime)
            _resp = _cli.models.generate_content(
                model=_CODISTYLE_MODEL,
                contents=[_gtypes.Content(parts=[_img_part, _gtypes.Part.from_text(text=prompt)])],
            )
            result_text = _resp.text if hasattr(_resp, "text") else str(_resp)
        else:
            _gmod.configure(api_key=_GEMINI_KEY)
            import PIL.Image as _PILImage, io
            _pil = _PILImage.open(io.BytesIO(img_bytes))
            _model = _gmod.GenerativeModel("gemini-1.5-flash")
            _resp = _model.generate_content([prompt, _pil])
            result_text = _resp.text

        import json, re as _re
        result_text = _re.sub(r"```json\s*", "", result_text.strip())
        result_text = _re.sub(r"```\s*", "", result_text).strip()
        try:
            pc = json.loads(result_text)
        except:
            m = _re.search(r"\{.*\}", result_text, _re.DOTALL)
            pc = json.loads(m.group()) if m else {}
        return jsonify(ok=True, personal_color=pc, model="gemini")
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.post("/api/track/item")
def track_item():
    """아이템 등록 시 프론트에서 호출"""
    try:
        d = request.get_json(force=True)
        body = {
            'user_id': d.get('user_id') or None,
            'email': d.get('email', ''),
            'category': d.get('category', ''),
            'image_url': d.get('image_url', ''),
            'item_name': d.get('item_name', '')
        }
        r = sb_query('POST', 'user_items', body=body)
        if r.status_code in (200, 201):
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": r.text}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ══════════════════════════════════════
# B) 관리자 조회 API (인증 필요)
# ══════════════════════════════════════

@app.get("/admin/payments")
def admin_payments():
    """결제 내역 조회"""
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        email = request.args.get('email', '')
        params = {'order': 'created_at.desc', 'limit': '100'}
        if email:
            params['email'] = f'eq.{email}'
        r = sb_query('GET', 'payments', params=params)
        if r.status_code != 200:
            return jsonify({"error": f"DB error: {r.status_code}"}), r.status_code
        data = r.json()
        total_revenue = sum(p.get('amount', 0) for p in data)
        return jsonify({"ok": True, "payments": data, "total": len(data), "total_revenue": total_revenue})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/admin/styling-logs")
def admin_styling_logs():
    """스타일링 이용 로그 조회"""
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        email = request.args.get('email', '')
        params = {'order': 'created_at.desc', 'limit': '200'}
        if email:
            params['email'] = f'eq.{email}'
        r = sb_query('GET', 'styling_logs', params=params)
        if r.status_code != 200:
            return jsonify({"error": f"DB error: {r.status_code}"}), r.status_code
        data = r.json()
        # 유저별 집계
        user_counts = {}
        for log in data:
            e = log.get('email', '')
            user_counts[e] = user_counts.get(e, 0) + 1
        return jsonify({"ok": True, "logs": data, "total": len(data), "by_user": user_counts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/admin/items")
def admin_items():
    """등록 아이템 조회"""
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        email = request.args.get('email', '')
        category = request.args.get('category', '')
        params = {'order': 'created_at.desc', 'limit': '200'}
        if email:
            params['email'] = f'eq.{email}'
        if category:
            params['category'] = f'eq.{category}'
        r = sb_query('GET', 'user_items', params=params)
        if r.status_code != 200:
            return jsonify({"error": f"DB error: {r.status_code}"}), r.status_code
        data = r.json()
        # 카테고리별 집계
        cat_counts = {}
        for item in data:
            c = item.get('category', 'other')
            cat_counts[c] = cat_counts.get(c, 0) + 1
        return jsonify({"ok": True, "items": data, "total": len(data), "by_category": cat_counts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/admin/dashboard")
def admin_dashboard_stats():
    """대시보드 통합 통계"""
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    stats = {"ok": True}
    try:
        # 결제 통계
        r = sb_query('GET', 'payments', params={'select': 'amount,created_at', 'limit': '1000'})
        if r.status_code == 200:
            payments = r.json()
            stats['total_payments'] = len(payments)
            stats['total_revenue'] = sum(p.get('amount', 0) for p in payments)
        # 스타일링 통계
        r = sb_query('GET', 'styling_logs', params={'select': 'id', 'limit': '10000'})
        if r.status_code == 200:
            stats['total_stylings'] = len(r.json())
        # 아이템 통계
        r = sb_query('GET', 'user_items', params={'select': 'category', 'limit': '10000'})
        if r.status_code == 200:
            items = r.json()
            stats['total_items'] = len(items)
            cat_counts = {}
            for item in items:
                c = item.get('category', 'other')
                cat_counts[c] = cat_counts.get(c, 0) + 1
            stats['items_by_category'] = cat_counts
    except Exception as e:
        stats['error'] = str(e)
    return jsonify(stats)


@app.post("/admin/login")
def admin_login():
    """이메일+비밀번호로 로그인 → 역할+권한 반환."""
    import hashlib as _hl
    data = request.get_json(silent=True) or {}
    email = str(data.get("email") or "").strip().lower()
    pw    = str(data.get("password") or "").strip()
    if not email or not pw:
        return jsonify({"ok": False, "error": "이메일과 비밀번호를 입력하세요."}), 400
    pw_hash = _hl.sha256(pw.encode()).hexdigest()
    info = _ADMIN_DB.get(email)
    if not info or info.get("hash") != pw_hash:
        return jsonify({"ok": False, "error": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401
    return jsonify({
        "ok": True,
        "email": email,
        "role": info.get("role", "SUB"),
        "name": info.get("name", email),
        "permissions": info.get("permissions", ALL_TABS),
        "hash": pw_hash,
    })


@app.get("/admin/admins")
def admin_list_admins():
    """어드민 목록 조회 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한이 필요합니다."}), 403
    result = []
    for email, info in _ADMIN_DB.items():
        result.append({
            "email": email,
            "name": info.get("name", email),
            "role": info.get("role", "SUB"),
            "permissions": info.get("permissions", ALL_TABS),
            "created_at": info.get("created_at", ""),
        })
    return jsonify({"ok": True, "admins": result})


@app.post("/admin/admins")
def admin_create_admin():
    """신규 어드민 생성 (MASTER 전용)."""
    import hashlib as _hl
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한이 필요합니다."}), 403
    data = request.get_json(silent=True) or {}
    email       = str(data.get("email") or "").strip().lower()
    pw          = str(data.get("password") or "").strip()
    name        = str(data.get("name") or email).strip()
    role        = "SUB"
    permissions = data.get("permissions") or ALL_TABS
    if not email or not pw:
        return jsonify({"ok": False, "error": "이메일과 비밀번호를 입력하세요."}), 400
    if email in _ADMIN_DB:
        return jsonify({"ok": False, "error": "이미 존재하는 어드민 계정입니다."}), 400
    if len(pw) < 4:
        return jsonify({"ok": False, "error": "비밀번호 4자 이상"}), 400
    from datetime import datetime
    import requests as _rq
    _ADMIN_DB[email] = {
        "role": role,
        "hash": _hl.sha256(pw.encode()).hexdigest(),
        "name": name,
        "permissions": permissions,
        "created_at": datetime.utcnow().isoformat(),
    }
    _save_admin_db()

    # ── Supabase에도 동일 계정 등록 (CodiBank 앱 로그인 가능하도록)
    sb_result = "skipped"
    try:
        _sb_url = supabase_url()
        _headers = supabase_admin_headers()
        sb_body = {
            "email":         email,
            "password":      pw,
            "email_confirm": True,
            "user_metadata": {
                "email":    email,
                "nickname": name,
                "plan":     "free",
                "role":     "admin",
            },
            "app_metadata": {
                "provider":  "email",
                "providers": ["email"],
                "role":      "admin",
            },
        }
        sb_r = _rq.post(f"{_sb_url}/auth/v1/admin/users",
                         headers=_headers, json=sb_body, timeout=15)
        if sb_r.status_code in (200, 201):
            sb_result = "created"
        elif sb_r.status_code == 422:
            # 이미 존재 → uid 찾아서 비밀번호 업데이트
            lr = _rq.get(f"{_sb_url}/auth/v1/admin/users?per_page=1000",
                          headers=_headers, timeout=15)
            if lr.status_code == 200:
                ud = lr.json()
                ul = ud.get("users", ud) if isinstance(ud, dict) else ud
                uid = next((u["id"] for u in ul if u.get("email","").lower()==email), None)
                if uid:
                    pu = _rq.put(f"{_sb_url}/auth/v1/admin/users/{uid}",
                                  headers=_headers,
                                  json={"password": pw, "email_confirm": True,
                                        "user_metadata": sb_body["user_metadata"]},
                                  timeout=15)
                    sb_result = "updated" if pu.status_code in (200,201) else f"put_failed:{pu.status_code}"
        else:
            sb_result = f"failed:{sb_r.status_code}"
    except Exception as _se:
        sb_result = f"error:{str(_se)[:80]}"

    return jsonify({"ok": True, "email": email, "supabase": sb_result})


@app.put("/admin/admins/<admin_email>")
def admin_update_admin(admin_email):
    """어드민 권한/비밀번호 수정 (MASTER 전용)."""
    import hashlib as _hl
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한이 필요합니다."}), 403
    email = admin_email.strip().lower()
    if email not in _ADMIN_DB:
        return jsonify({"ok": False, "error": "존재하지 않는 어드민입니다."}), 404
    data = request.get_json(silent=True) or {}
    # 비밀번호 변경
    new_pw = str(data.get("newPassword") or "").strip()
    if new_pw:
        if len(new_pw) < 4:
            return jsonify({"ok": False, "error": "비밀번호 4자 이상"}), 400
        _ADMIN_DB[email]["hash"] = _hl.sha256(new_pw.encode()).hexdigest()
        # 마스터 어드민이면 환경변수도 동기화
        if _ADMIN_DB[email].get("role") == "MASTER":
            os.environ["ADMIN_PW_HASH"] = _ADMIN_DB[email]["hash"]
    # 권한 변경
    if "permissions" in data:
        _ADMIN_DB[email]["permissions"] = data["permissions"]
    # 이름 변경
    if "name" in data:
        _ADMIN_DB[email]["name"] = data["name"]
    _save_admin_db()
    return jsonify({"ok": True})


@app.delete("/admin/admins/<admin_email>")
def admin_delete_admin(admin_email):
    """서브 어드민 삭제 (MASTER 전용, 마스터 본인 삭제 불가)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한이 필요합니다."}), 403
    email = admin_email.strip().lower()
    if email not in _ADMIN_DB:
        return jsonify({"ok": False, "error": "존재하지 않는 어드민입니다."}), 404
    if _ADMIN_DB[email].get("role") == "MASTER":
        return jsonify({"ok": False, "error": "마스터 어드민은 삭제할 수 없습니다."}), 400
    del _ADMIN_DB[email]
    _save_admin_db()
    return jsonify({"ok": True})


@app.post("/admin/change-password")
def admin_change_password():
    """어드민 비밀번호 변경 — 현재 비밀번호 검증 후 새 비밀번호로 교체.
    Render 환경변수 ADMIN_PW_HASH를 런타임에 갱신하고,
    서버 재시작 없이 즉시 적용되도록 os.environ을 직접 업데이트합니다.
    (영구 반영을 위해서는 Render 대시보드에서 환경변수도 변경해야 합니다.)
    """
    import hashlib as _hl
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    current_pw  = str(data.get("currentPassword") or "").strip()
    new_pw      = str(data.get("newPassword") or "").strip()
    confirm_pw  = str(data.get("confirmPassword") or "").strip()

    if not current_pw or not new_pw or not confirm_pw:
        return jsonify({"ok": False, "error": "모든 필드를 입력해주세요."}), 400

    # 현재 비밀번호 검증 — _ADMIN_DB 기준 (X-Admin-Key 헤더로 로그인한 어드민 찾기)
    provided_key  = (request.args.get("key") or request.headers.get("X-Admin-Key") or "").strip()
    current_hash  = _hl.sha256(current_pw.encode("utf-8")).hexdigest()

    # X-Admin-Key(로그인 시 발급된 해시)로 호출자 이메일 특정
    caller_email, caller_info = _get_admin_by_hash(provided_key)

    if not caller_info:
        return jsonify({"ok": False, "error": "세션이 만료되었습니다. 다시 로그인해주세요."}), 401

    # 입력한 현재 비밀번호가 _ADMIN_DB의 해시와 일치하는지 확인
    if current_hash != caller_info.get("hash", ""):
        return jsonify({"ok": False, "error": "현재 비밀번호가 올바르지 않습니다."}), 400

    # 새 비밀번호 유효성 검사
    if new_pw != confirm_pw:
        return jsonify({"ok": False, "error": "새 비밀번호와 확인 비밀번호가 일치하지 않습니다."}), 400
    if len(new_pw) < 4:
        return jsonify({"ok": False, "error": "새 비밀번호는 4자 이상이어야 합니다."}), 400
    if new_pw == current_pw:
        return jsonify({"ok": False, "error": "현재 비밀번호와 동일한 비밀번호는 사용할 수 없습니다."}), 400

    # 새 해시 생성 → _ADMIN_DB 즉시 갱신 (재시작 없이 반영)
    new_hash = _hl.sha256(new_pw.encode("utf-8")).hexdigest()
    _ADMIN_DB[caller_email]["hash"] = new_hash
    _save_admin_db()
    # 마스터 어드민이면 환경변수도 동기화
    if caller_info.get("role") == "MASTER":
        os.environ["ADMIN_PW_HASH"] = new_hash

    return jsonify({
        "ok": True,
        "message": "비밀번호가 즉시 변경되었습니다.",
        "new_hash": new_hash,
    })



# ══════════════════════════════════════════════════════════════
# 사용횟수 조정 API (MASTER 어드민 전용)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 설계:
#   - 사용횟수는 각 유저 브라우저 localStorage에 저장됨
#   - 어드민이 Supabase 'user_usage_bonus' 테이블에 보너스 값 저장
#   - 앱(코디쌤 closet.html / 코디하기 codistyle.html)이 로딩 시 /api/usage/bonus/<email>로 조회
#   - 조회된 bonus가 있으면 해당 월 한도에 더해 적용
# ══════════════════════════════════════════════════════════════

# ── Bonus 읽기 (앱에서 호출, 인증 불필요)
@app.get("/api/usage/bonus/<email>")
def get_usage_bonus(email):
    """특정 이메일의 사용횟수 보너스 조회."""
    try:
        email = email.strip().lower()
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        params = {
            "email": f"eq.{email}",
            "month": f"eq.{now_ym}",
            "select": "total_bonus",
            "limit": "1",
        }
        # 1) Supabase 테이블 조회
        try:
            r = sb_query("GET", "user_usage_bonus", params=params)
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    tb = int(rows[0].get("total_bonus", 0))
                    return jsonify({"ok": True, "total_bonus": tb, "month": now_ym})
        except Exception:
            pass
        # 2) Supabase 실패 시 서버 메모리 폴백 확인
        if hasattr(app, "_usage_bonus_cache"):
            key = f"{email}:{now_ym}"
            if key in app._usage_bonus_cache:
                tb = int(app._usage_bonus_cache[key].get("total_bonus", 0))
                return jsonify({"ok": True, "total_bonus": tb, "month": now_ym, "source": "memory"})
        return jsonify({"ok": True, "total_bonus": 0, "month": now_ym})
    except Exception as e:
        return jsonify({"ok": True, "total_bonus": 0, "error": str(e)})


# ── Bonus 설정 (MASTER 전용)
@app.post("/admin/usage/set-bonus")
def admin_set_usage_bonus():
    """유저의 사용횟수 보너스 설정 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        data = request.get_json(silent=True) or {}
        email       = str(data.get("email", "")).strip().lower()
        total_b     = max(0, int(data.get("total_bonus", data.get("closet_bonus", 0)) or 0))
        month       = str(data.get("month") or __import__('datetime').datetime.now().strftime("%Y-%m"))
        if not email:
            return jsonify({"ok": False, "error": "email 필수"}), 400
        if total_b < 0:
            return jsonify({"ok": False, "error": "보너스는 0 이상이어야 합니다"}), 400

        body = {"email": email, "month": month, "total_bonus": total_b,
                "updated_at": __import__('datetime').datetime.utcnow().isoformat() + "Z",
                "updated_by": (request.headers.get("X-Admin-Key") or "")[:16]}

        import requests as _rq
        url = f"{supabase_url()}/rest/v1/user_usage_bonus"
        headers = supabase_admin_headers()
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        r = _rq.post(url, headers=headers, json=body, timeout=10)
        if r.status_code in (200, 201):
            return jsonify({"ok": True, "email": email, "month": month, "total_bonus": total_b})
        if not hasattr(app, "_usage_bonus_cache"):
            app._usage_bonus_cache = {}
        app._usage_bonus_cache[f"{email}:{month}"] = {"total_bonus": total_b}
        return jsonify({"ok": True, "email": email, "month": month,
                        "total_bonus": total_b, "note": "memory_fallback"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── 보너스 현황 조회 (MASTER 전용)
@app.get("/admin/usage/bonus-list")
def admin_usage_bonus_list():
    """이달 보너스 지급 현황 전체 조회 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        params = {"month": f"eq.{now_ym}", "order": "updated_at.desc", "limit": "500",
                  "select": "email,month,total_bonus,updated_at"}
        r = sb_query("GET", "user_usage_bonus", params=params)
        if r.status_code == 200:
            return jsonify({"ok": True, "list": r.json(), "month": now_ym})
        # 메모리 폴백
        if hasattr(app, "_usage_bonus_cache"):
            rows = [{"email": k.split(":")[0], "month": k.split(":")[1], **v}
                    for k, v in app._usage_bonus_cache.items() if k.endswith(now_ym)]
            return jsonify({"ok": True, "list": rows, "month": now_ym, "note": "memory_fallback"})
        return jsonify({"ok": True, "list": [], "month": now_ym})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
# ──── [2026-04-09 추가] 사용량 서버 동기화 API ────
# 원인: localStorage만으로는 기기 변경 시 초기화, 관리자 페이지에서 조회 불가
# 해결: Supabase user_usage 테이블에 실시간 기록 + 조회
# 관련파일: closet.html, codistyle.html, admin.html
# ══════════════════════════════════════════════════════════════

@app.post("/api/usage/record")
def api_usage_record():
    """사용량 기록 (closet.html / codistyle.html에서 호출).
    body: { email, feature: 'closet'|'codistyle' }
    Supabase user_usage 테이블에 upsert.
    """
    try:
        data = request.get_json(silent=True) or {}
        email   = str(data.get("email", "")).strip().lower()
        feature = str(data.get("feature", "")).strip().lower()
        if not email:
            return jsonify({"ok": False, "error": "email 필수"}), 400
        if feature not in ("closet", "codistyle", "item"):
            return jsonify({"ok": False, "error": "feature must be closet, codistyle, or item"}), 400

        import datetime as _dt
        now      = _dt.datetime.now()
        month_k  = f"{now.year}-{now.month}"
        day_k    = now.strftime("%Y-%m-%d")

        # 1) 기존 행 조회
        params = {"email": f"eq.{email}", "select": "*", "limit": "1"}
        row = None
        try:
            r = sb_query("GET", "user_usage", params=params)
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    row = rows[0]
        except Exception:
            pass

        # 2) 월/일 리셋 로직
        if row:
            if row.get("month") != month_k:
                row["month"] = month_k
                row["closet_count"] = 0
                row["codistyle_count"] = 0
                row["total_count"] = 0
                row["item_count"] = 0
            if row.get("day") != day_k:
                row["day"] = day_k
                row["day_closet_count"] = 0
                row["day_codi_count"] = 0
                row["day_total"] = 0
                row["day_item_count"] = 0
        else:
            row = {
                "email": email, "month": month_k, "day": day_k,
                "closet_count": 0, "codistyle_count": 0, "total_count": 0,
                "item_count": 0,
                "day_closet_count": 0, "day_codi_count": 0, "day_total": 0,
                "day_item_count": 0,
            }

        # 3) 카운터 증가
        if feature == "closet":
            row["closet_count"]     = int(row.get("closet_count") or 0) + 1
            row["day_closet_count"] = int(row.get("day_closet_count") or 0) + 1
        elif feature == "codistyle":
            row["codistyle_count"]  = int(row.get("codistyle_count") or 0) + 1
            row["day_codi_count"]   = int(row.get("day_codi_count") or 0) + 1
        elif feature == "item":
            row["item_count"]       = int(row.get("item_count") or 0) + 1
            row["day_item_count"]   = int(row.get("day_item_count") or 0) + 1

        row["total_count"] = int(row.get("closet_count") or 0) + int(row.get("codistyle_count") or 0)
        row["day_total"]   = int(row.get("day_closet_count") or 0) + int(row.get("day_codi_count") or 0)
        row["updated_at"]  = _dt.datetime.utcnow().isoformat() + "Z"

        # 4) Upsert
        body = {
            "email": email, "month": row["month"], "day": row["day"],
            "closet_count": row["closet_count"], "codistyle_count": row["codistyle_count"],
            "total_count": row["total_count"], "item_count": int(row.get("item_count") or 0),
            "day_closet_count": row["day_closet_count"], "day_codi_count": row["day_codi_count"],
            "day_total": row["day_total"], "day_item_count": int(row.get("day_item_count") or 0),
            "updated_at": row["updated_at"],
        }
        import requests as _rq
        url = f"{supabase_url()}/rest/v1/user_usage"
        headers = supabase_admin_headers()
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        resp = _rq.post(url, headers=headers, json=body, timeout=10)

        # 메모리 폴백
        if not hasattr(app, "_usage_cache"):
            app._usage_cache = {}
        app._usage_cache[email] = body

        if resp.status_code in (200, 201):
            return jsonify({"ok": True, **body})
        return jsonify({"ok": True, **body, "note": "memory_fallback"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/api/usage/get/<email>")
def api_usage_get(email):
    """특정 유저의 현재 사용량 조회 (앱 로딩 시 호출)."""
    try:
        email = email.strip().lower()
        import datetime as _dt
        now     = _dt.datetime.now()
        month_k = f"{now.year}-{now.month}"
        day_k   = now.strftime("%Y-%m-%d")

        row = None
        try:
            params = {"email": f"eq.{email}", "select": "*", "limit": "1"}
            r = sb_query("GET", "user_usage", params=params)
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    row = rows[0]
        except Exception:
            pass

        # 메모리 폴백
        if not row and hasattr(app, "_usage_cache") and email in app._usage_cache:
            row = app._usage_cache[email]

        if not row:
            return jsonify({"ok": True, "month": month_k, "day": day_k,
                            "closetCount": 0, "codistyleCount": 0, "totalCount": 0,
                            "itemCount": 0,
                            "dayClosetCount": 0, "dayCodiCount": 0, "dayTotal": 0,
                            "dayItemCount": 0})

        # 월/일 리셋
        r_month = row.get("month", "")
        r_day   = row.get("day", "")
        cc = int(row.get("closet_count") or 0)
        cs = int(row.get("codistyle_count") or 0)
        tc = int(row.get("total_count") or 0)
        ic = int(row.get("item_count") or 0)
        dc = int(row.get("day_closet_count") or 0)
        dd = int(row.get("day_codi_count") or 0)
        dt_ = int(row.get("day_total") or 0)
        di = int(row.get("day_item_count") or 0)

        if r_month != month_k:
            cc = cs = tc = ic = 0
        if r_day != day_k:
            dc = dd = dt_ = di = 0

        return jsonify({
            "ok": True, "month": month_k, "day": day_k,
            "closetCount": cc, "codistyleCount": cs, "totalCount": tc,
            "itemCount": ic,
            "dayClosetCount": dc, "dayCodiCount": dd, "dayTotal": dt_,
            "dayItemCount": di,
        })
    except Exception as e:
        return jsonify({"ok": True, "month": "", "closetCount": 0, "codistyleCount": 0,
                        "totalCount": 0, "itemCount": 0,
                        "dayClosetCount": 0, "dayCodiCount": 0, "dayTotal": 0,
                        "dayItemCount": 0, "error": str(e)})


@app.get("/admin/usage/summary")
def admin_usage_summary():
    """전체 회원 사용량 집계 (MASTER 어드민 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        import datetime as _dt
        now_ym  = _dt.datetime.now().strftime("%Y-") + str(_dt.datetime.now().month)
        params  = {"month": f"eq.{now_ym}", "order": "total_count.desc", "limit": "500",
                    "select": "email,month,day,closet_count,codistyle_count,total_count,item_count,day_closet_count,day_codi_count,day_total,day_item_count,updated_at"}
        r = sb_query("GET", "user_usage", params=params)
        if r.status_code == 200:
            return jsonify({"ok": True, "list": r.json(), "month": now_ym})

        # 메모리 폴백
        if hasattr(app, "_usage_cache"):
            rows = [v for v in app._usage_cache.values() if v.get("month") == now_ym]
            return jsonify({"ok": True, "list": rows, "month": now_ym, "note": "memory_fallback"})
        return jsonify({"ok": True, "list": [], "month": now_ym})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
# 아이템 등록 보너스 API (이미지 생성 보너스와 동일 구조)
# ══════════════════════════════════════════════════════════════

@app.get("/api/usage/item-bonus/<email>")
def get_item_bonus(email: str):
    """유저 아이템 등록 보너스 조회 (앱에서 호출)."""
    try:
        email = email.strip().lower()
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        params = {"email": f"eq.{email}", "month": f"eq.{now_ym}", "select": "total_bonus", "limit": "1"}
        try:
            r = sb_query("GET", "user_item_bonus", params=params)
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    return jsonify({"ok": True, "total_bonus": int(rows[0].get("total_bonus", 0)), "month": now_ym})
        except Exception:
            pass
        if hasattr(app, "_item_bonus_cache"):
            key = f"{email}:{now_ym}"
            if key in app._item_bonus_cache:
                return jsonify({"ok": True, "total_bonus": int(app._item_bonus_cache[key].get("total_bonus", 0)), "month": now_ym, "source": "memory"})
        return jsonify({"ok": True, "total_bonus": 0, "month": now_ym})
    except Exception as e:
        return jsonify({"ok": True, "total_bonus": 0, "error": str(e)})


@app.post("/admin/item-bonus/set")
def admin_set_item_bonus():
    """아이템 등록 보너스 설정 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        data = request.get_json(silent=True) or {}
        email   = str(data.get("email", "")).strip().lower()
        total_b = max(0, int(data.get("total_bonus", 0) or 0))
        month   = str(data.get("month") or __import__('datetime').datetime.now().strftime("%Y-%m"))
        if not email:
            return jsonify({"ok": False, "error": "email 필수"}), 400
        body = {"email": email, "month": month, "total_bonus": total_b,
                "updated_at": __import__('datetime').datetime.utcnow().isoformat() + "Z",
                "updated_by": (request.headers.get("X-Admin-Key") or "")[:16]}
        import requests as _rq
        url = f"{supabase_url()}/rest/v1/user_item_bonus"
        headers = supabase_admin_headers()
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        r = _rq.post(url, headers=headers, json=body, timeout=10)
        if r.status_code in (200, 201):
            return jsonify({"ok": True, "email": email, "month": month, "total_bonus": total_b})
        if not hasattr(app, "_item_bonus_cache"):
            app._item_bonus_cache = {}
        app._item_bonus_cache[f"{email}:{month}"] = {"total_bonus": total_b}
        return jsonify({"ok": True, "email": email, "month": month, "total_bonus": total_b, "note": "memory_fallback"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/admin/item-bonus/list")
def admin_item_bonus_list():
    """아이템 보너스 현황 전체 조회 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        params = {"month": f"eq.{now_ym}", "order": "updated_at.desc", "limit": "500",
                  "select": "email,month,total_bonus,updated_at"}
        r = sb_query("GET", "user_item_bonus", params=params)
        if r.status_code == 200:
            return jsonify({"ok": True, "list": r.json(), "month": now_ym})
        if hasattr(app, "_item_bonus_cache"):
            rows = [{"email": k.split(":")[0], "month": k.split(":")[1], **v}
                    for k, v in app._item_bonus_cache.items() if k.endswith(now_ym)]
            return jsonify({"ok": True, "list": rows, "month": now_ym, "note": "memory_fallback"})
        return jsonify({"ok": True, "list": [], "month": now_ym})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
# 테스트 계정 생성 + 회원 사용횟수 지급 API
# ══════════════════════════════════════════════════════════════

@app.post("/admin/create-test-accounts")
def admin_create_test_accounts():
    """test01~test10@codibank.kr 테스트 계정 10개 이메일 인증 없이 생성 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403

    import requests as _rq
    results = []
    _sb_url = supabase_url()
    _headers = supabase_admin_headers()

    for i in range(1, 11):
        email = f"test{i:02d}@codibank.kr"
        pw    = f"Test{i:02d}!234"   # 기본 비밀번호 (Test01!234 ~ Test10!234)

        body = {
            "email":         email,
            "password":      pw,
            "email_confirm": True,      # 이메일 인증 완료 → 즉시 로그인 가능
            # Supabase Admin API: user_metadata는 JWT에 포함되어 앱에서 읽힘
            "user_metadata": {
                "plan":     "free",
                "gender":   "M" if i % 2 == 1 else "F",
                "ageGroup": "30s",
                "height":   str(170 + i),
                "weight":   str(65 + i),
                "nickname": f"테스트{i:02d}",
                "email":    email,
            },
            # app_metadata: 서버 측 메타데이터 (provider 정보 등)
            "app_metadata": {
                "provider":  "email",
                "providers": ["email"],
            },
        }
        url = f"{_sb_url}/auth/v1/admin/users"
        r = _rq.post(url, headers=_headers, json=body, timeout=15)
        if r.status_code in (200, 201):
            results.append({"email": email, "password": pw, "status": "created"})
        elif r.status_code == 422:
            # 이미 존재하는 계정 → uid 조회 후 PUT으로 비밀번호 + 인증 강제 업데이트
            try:
                # 유저 목록에서 email로 uid 찾기
                list_url = f"{_sb_url}/auth/v1/admin/users?page=1&per_page=1000"
                lr = _rq.get(list_url, headers=_headers, timeout=15)
                uid = None
                if lr.status_code == 200:
                    users_data = lr.json()
                    user_list = users_data.get("users", users_data) if isinstance(users_data, dict) else users_data
                    for u in user_list:
                        if u.get("email", "").lower() == email.lower():
                            uid = u.get("id")
                            break
                if uid:
                    # PUT으로 비밀번호 + email_confirm 강제 업데이트
                    patch_url = f"{_sb_url}/auth/v1/admin/users/{uid}"
                    patch_body = {
                        "password":      pw,
                        "email_confirm": True,
                        "user_metadata": body["user_metadata"],
                        "app_metadata":  body["app_metadata"],
                    }
                    pr = _rq.put(patch_url, headers=_headers, json=patch_body, timeout=15)
                    if pr.status_code in (200, 201):
                        results.append({"email": email, "password": pw, "status": "updated"})
                    else:
                        results.append({"email": email, "password": pw, "status": "update_failed",
                                         "detail": pr.text[:200]})
                else:
                    results.append({"email": email, "password": pw, "status": "uid_not_found"})
            except Exception as ex:
                results.append({"email": email, "password": pw, "status": "already_exists_error",
                                 "detail": str(ex)[:200]})
        else:
            results.append({"email": email, "password": pw, "status": "failed",
                             "detail": r.text[:200]})

    created = [r for r in results if r["status"] == "created"]
    updated = [r for r in results if r["status"] == "updated"]
    exists  = [r for r in results if r["status"] == "already_exists"]
    failed  = [r for r in results if r["status"] in ("failed", "update_failed", "uid_not_found", "already_exists_error")]

    # ── 성공한 테스트 계정을 _ADMIN_DB에도 등록 (관리자페이지 로그인 가능)
    import hashlib as _hlx
    from datetime import datetime as _dt
    for r_ in results:
        if r_["status"] in ("created", "updated"):
            em_ = r_["email"]
            pw_ = r_["password"]
            _ADMIN_DB[em_] = {
                "role":        "SUB",
                "hash":        _hlx.sha256(pw_.encode()).hexdigest(),
                "name":        em_.split("@")[0],
                "permissions": ["dash", "users", "closet", "codi"],
                "created_at":  _dt.utcnow().isoformat(),
            }
    _save_admin_db()

    return jsonify({
        "ok": True,
        "summary": f"신규생성:{len(created)} / 비밀번호업데이트:{len(updated)} / 실패:{len(failed)}",
        "results": results,
        "default_password_pattern": "Test01!234 ~ Test10!234",
        "note": "테스트 계정이 Supabase + 관리자페이지에 모두 등록됐습니다.",
    })


# ── 회원 사용횟수 지급 (MASTER 전용) — 특정 회원 email 기준
@app.post("/admin/member/set-bonus")
def admin_member_set_bonus():
    """회원(일반 유저)에게 이번달 이미지 생성 보너스 지급 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        import requests as _rq
        data        = request.get_json(silent=True) or {}
        email       = str(data.get("email", "")).strip().lower()
        total_b     = max(0, int(data.get("total_bonus", data.get("closet_bonus", 0)) or 0))
        month       = str(data.get("month") or __import__('datetime').datetime.now().strftime("%Y-%m"))

        if not email:
            return jsonify({"ok": False, "error": "email 필수"}), 400

        bonus_body = {
            "email": email, "month": month, "total_bonus": total_b,
            "updated_at": __import__('datetime').datetime.utcnow().isoformat() + "Z",
            "updated_by": (request.headers.get("X-Admin-Key") or "")[:16],
        }
        url     = f"{supabase_url()}/rest/v1/user_usage_bonus"
        headers = supabase_admin_headers()
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        r = _rq.post(url, headers=headers, json=bonus_body, timeout=10)

        if r.status_code not in (200, 201):
            if not hasattr(app, "_usage_bonus_cache"):
                app._usage_bonus_cache = {}
            app._usage_bonus_cache[f"{email}:{month}"] = {"total_bonus": total_b}

        return jsonify({
            "ok": True, "email": email, "month": month, "total_bonus": total_b,
            "note": "memory_fallback" if r.status_code not in (200, 201) else "saved_to_supabase",
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── 특정 회원 보너스 조회 (MASTER 전용)
@app.get("/admin/member/bonus/<email>")
def admin_member_get_bonus(email):
    """특정 회원의 이달 보너스 조회 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        email  = email.strip().lower()
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        params = {"email": f"eq.{email}", "month": f"eq.{now_ym}", "limit": "1"}
        r      = sb_query("GET", "user_usage_bonus", params=params)
        if r.status_code == 200:
            rows = r.json()
            if rows:
                return jsonify({"ok": True, **rows[0]})
        if hasattr(app, "_usage_bonus_cache"):
            key = f"{email}:{now_ym}"
            if key in app._usage_bonus_cache:
                return jsonify({"ok": True, "email": email, "month": now_ym,
                                **app._usage_bonus_cache[key]})
        return jsonify({"ok": True, "email": email, "month": now_ym, "total_bonus": 0})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500



@app.post("/admin/sync-to-supabase")
def admin_sync_to_supabase():
    """_ADMIN_DB의 모든 어드민 계정을 Supabase에 동기화 (MASTER 전용).
    어드민이 CodiBank 앱에도 로그인 가능하도록 Supabase 계정을 생성/업데이트합니다.
    비밀번호는 요청 body의 password_map {email: pw} 또는 기본값 'pass1234'를 사용합니다.
    """
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    import requests as _rq
    data = request.get_json(silent=True) or {}
    password_map = data.get("password_map") or {}   # {email: password}
    default_pw   = str(data.get("default_password") or "pass1234")

    _sb_url = supabase_url()
    _headers = supabase_admin_headers()
    results = []

    # 기존 Supabase 유저 목록 미리 가져오기 (uid 검색용)
    existing_uid_map = {}
    try:
        lr = _rq.get(f"{_sb_url}/auth/v1/admin/users?per_page=1000",
                      headers=_headers, timeout=15)
        if lr.status_code == 200:
            ud = lr.json()
            ul = ud.get("users", ud) if isinstance(ud, dict) else ud
            for u in ul:
                existing_uid_map[u.get("email","").lower()] = u.get("id")
    except Exception:
        pass

    _P1234_HASH = "bd94dcda26fccb4e68d6a31f9b5aac0b571ae266d822620e901ef7ebe3a11d4f"
    for email, info in _ADMIN_DB.items():
        if email in password_map:
            pw = password_map[email]
        elif info.get("hash") == _P1234_HASH:
            pw = "pass1234"
        else:
            pw = default_pw
        name = info.get("name", email)
        sb_body = {
            "email":         email,
            "password":      pw,
            "email_confirm": True,
            "user_metadata": {
                "email":    email,
                "nickname": name,
                "plan":     "free",
                "role":     "admin",
            },
            "app_metadata": {
                "provider":  "email",
                "providers": ["email"],
                "role":      "admin",
            },
        }
        try:
            uid = existing_uid_map.get(email.lower())
            if uid:
                # 이미 존재 → 비밀번호 업데이트
                pr = _rq.put(f"{_sb_url}/auth/v1/admin/users/{uid}",
                              headers=_headers,
                              json={"password": pw, "email_confirm": True,
                                    "user_metadata": sb_body["user_metadata"]},
                              timeout=15)
                status = "updated" if pr.status_code in (200,201) else f"put_failed:{pr.status_code}"
            else:
                # 신규 생성
                cr = _rq.post(f"{_sb_url}/auth/v1/admin/users",
                               headers=_headers, json=sb_body, timeout=15)
                status = "created" if cr.status_code in (200,201) else f"post_failed:{cr.status_code}"
        except Exception as e:
            status = f"error:{str(e)[:60]}"
        results.append({"email": email, "password": pw, "status": status})

    return jsonify({
        "ok":     True,
        "synced": len(results),
        "results": results,
        "note": "어드민 계정이 Supabase에 동기화됐습니다. CodiBank 앱에서 동일한 이메일/비밀번호로 로그인하세요.",
    })


@app.get("/admin/debug/supabase-status")
def admin_debug_supabase():
    """Supabase 연결 상태 + admin 계정 존재 여부 진단 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    import requests as _rq
    _sb  = supabase_url()
    _hdr = supabase_admin_headers()
    result = {
        "supabase_url": _sb,
        "service_key_set": bool(os.environ.get("SUPABASE_SERVICE_KEY", "")),
        "service_key_prefix": (os.environ.get("SUPABASE_SERVICE_KEY", "")[:20] + "...") if os.environ.get("SUPABASE_SERVICE_KEY") else "NOT SET",
    }
    # Supabase Admin API 테스트 — 유저 목록 1명만 가져오기
    try:
        tr = _rq.get(f"{_sb}/auth/v1/admin/users?per_page=1", headers=_hdr, timeout=10)
        result["api_status_code"] = tr.status_code
        result["api_ok"] = tr.status_code == 200
        if tr.status_code == 200:
            ud = tr.json()
            ul = ud.get("users", ud) if isinstance(ud, dict) else ud
            result["total_users_sample"] = len(ul)
        else:
            result["api_error"] = tr.text[:300]
    except Exception as e:
        result["api_exception"] = str(e)[:200]
        result["api_ok"] = False

    # admin@codibank.kr Supabase 존재 여부
    admin_exists = False
    test_exists  = {}
    try:
        lr = _rq.get(f"{_sb}/auth/v1/admin/users?per_page=1000", headers=_hdr, timeout=15)
        if lr.status_code == 200:
            ud = lr.json()
            ul = ud.get("users", ud) if isinstance(ud, dict) else ud
            emails_confirmed = {}
            for u in ul:
                em_l = u.get("email","").lower()
                emails_confirmed[em_l] = {
                    "exists": True,
                    "confirmed": bool(u.get("email_confirmed_at")),
                    "confirmed_at": u.get("email_confirmed_at",""),
                }
            admin_exists = "admin@codibank.kr" in emails_confirmed
            result["admin_confirmed"] = emails_confirmed.get("admin@codibank.kr",{}).get("confirmed", False)
            for i in range(1, 11):
                em = f"test{i:02d}@codibank.kr"
                info = emails_confirmed.get(em, {"exists": False, "confirmed": False})
                test_exists[em] = info
            result["total_supabase_users"] = len(ul)
    except Exception as e:
        result["list_exception"] = str(e)[:200]

    result["admin_in_supabase"]  = admin_exists
    result["test_accounts"] = test_exists
    result["_admin_db_accounts"] = list(_ADMIN_DB.keys())

    return jsonify(result)


@app.post("/admin/debug/force-create-admin")
def admin_debug_force_create():
    """admin@codibank.kr를 Supabase에 강제 생성/업데이트 (MASTER 전용).
    진단 후 직접 호출로 즉시 해결.
    """
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    import requests as _rq
    data = request.get_json(silent=True) or {}
    target_email = str(data.get("email") or "admin@codibank.kr").strip().lower()
    password     = str(data.get("password") or "pass1234").strip()

    _sb  = supabase_url()
    _hdr = supabase_admin_headers()
    steps = []

    # 1단계: 서비스 키 확인
    svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not svc_key:
        return jsonify({
            "ok": False,
            "error": "SUPABASE_SERVICE_KEY 환경변수가 설정되지 않았습니다.",
            "action": "Render 대시보드 → Environment → SUPABASE_SERVICE_KEY에 Supabase service_role 키를 추가하세요.",
            "where_to_find": f"https://supabase.com/dashboard/project/drgsayvlpzcacurcczjq/settings/api → service_role 키",
        })
    steps.append({"step": "service_key_check", "ok": True})

    # 2단계: 기존 유저 uid 조회
    uid = None
    try:
        lr = _rq.get(f"{_sb}/auth/v1/admin/users?per_page=1000", headers=_hdr, timeout=15)
        steps.append({"step": "list_users", "status": lr.status_code})
        if lr.status_code == 200:
            ud = lr.json()
            ul = ud.get("users", ud) if isinstance(ud, dict) else ud
            for u in ul:
                if u.get("email","").lower() == target_email:
                    uid = u.get("id")
                    break
    except Exception as e:
        steps.append({"step": "list_users", "error": str(e)[:100]})

    sb_body = {
        "email": target_email, "password": password, "email_confirm": True,
        "user_metadata": {
            "email": target_email, "nickname": "마스터 관리자",
            "plan": "free", "role": "admin",
        },
        "app_metadata": {"provider": "email", "providers": ["email"]},
    }

    # 3단계: 생성 또는 업데이트
    if uid:
        pr = _rq.put(f"{_sb}/auth/v1/admin/users/{uid}", headers=_hdr,
                     json={"password": password, "email_confirm": True,
                           "user_metadata": sb_body["user_metadata"]}, timeout=15)
        steps.append({"step": "put_update", "status": pr.status_code,
                      "ok": pr.status_code in (200, 201),
                      "response": pr.text[:200] if pr.status_code not in (200,201) else "ok"})
        action = "updated"
    else:
        cr = _rq.post(f"{_sb}/auth/v1/admin/users", headers=_hdr, json=sb_body, timeout=15)
        steps.append({"step": "post_create", "status": cr.status_code,
                      "ok": cr.status_code in (200, 201),
                      "response": cr.text[:300] if cr.status_code not in (200,201) else "ok"})
        action = "created" if cr.status_code in (200,201) else "failed"

    final_ok = any(s.get("ok") for s in steps if s.get("step") in ("put_update","post_create"))
    return jsonify({
        "ok": final_ok,
        "email": target_email,
        "password_used": password,
        "action": action,
        "steps": steps,
        "next_step": (
            f"성공! CodiBank 앱에서 {target_email} / {password} 로 로그인하세요."
            if final_ok else
            "실패. steps 확인 후 SUPABASE_SERVICE_KEY가 service_role 키인지 확인하세요."
        ),
    })



@app.post("/admin/debug/confirm-all-emails")
def admin_confirm_all_emails():
    """Supabase의 admin + test01~10 계정 email_confirmed_at을 지금 시각으로 일괄 설정.
    이메일 미인증으로 로그인 안 되는 문제를 직접 해결합니다 (MASTER 전용).
    """
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    import requests as _rq
    _sb  = supabase_url()
    _hdr = supabase_admin_headers()

    svc_key = os.environ.get("SUPABASE_SERVICE_KEY","")
    if not svc_key:
        return jsonify({"ok": False,
                        "error": "SUPABASE_SERVICE_KEY 환경변수 없음",
                        "action": "Render 환경변수에 SUPABASE_SERVICE_KEY(service_role 키) 추가 후 재배포"})

    # 대상 이메일 목록
    targets = ["admin@codibank.kr"] + [f"test{i:02d}@codibank.kr" for i in range(1, 11)]
    data = request.get_json(silent=True) or {}
    extra = data.get("extra_emails") or []
    targets += [e.strip().lower() for e in extra if e.strip()]

    # Supabase 유저 목록에서 uid 조회
    try:
        lr = _rq.get(f"{_sb}/auth/v1/admin/users?per_page=1000", headers=_hdr, timeout=15)
        if lr.status_code != 200:
            return jsonify({"ok": False, "error": f"유저 목록 조회 실패: {lr.status_code}", "body": lr.text[:300]})
        ud  = lr.json()
        ul  = ud.get("users", ud) if isinstance(ud, dict) else ud
        uid_map = {u.get("email","").lower(): u for u in ul}
    except Exception as e:
        return jsonify({"ok": False, "error": f"유저 목록 조회 예외: {str(e)}"})

    results = []
    for email in targets:
        u = uid_map.get(email)
        if not u:
            results.append({"email": email, "status": "not_found"})
            continue
        uid = u.get("id")
        already = bool(u.get("email_confirmed_at"))
        # PUT으로 email_confirm: True 강제 설정
        try:
            pr = _rq.put(
                f"{_sb}/auth/v1/admin/users/{uid}",
                headers=_hdr,
                json={"email_confirm": True},
                timeout=15
            )
            if pr.status_code in (200, 201):
                results.append({"email": email, "status": "confirmed", "was_already": already})
            else:
                results.append({"email": email, "status": f"failed_{pr.status_code}",
                                 "detail": pr.text[:200]})
        except Exception as e:
            results.append({"email": email, "status": f"error: {str(e)[:80]}"})

    ok_count   = sum(1 for r in results if r["status"] == "confirmed")
    fail_count = sum(1 for r in results if "fail" in r["status"] or "error" in r["status"])
    return jsonify({
        "ok":         fail_count == 0,
        "confirmed":  ok_count,
        "failed":     fail_count,
        "results":    results,
        "next_step":  f"✅ {ok_count}개 인증 완료. 이제 CodiBank 앱에서 로그인하세요." if ok_count > 0 else "실패. SUPABASE_SERVICE_KEY를 확인하세요.",
    })



@app.post("/admin/debug/test-login")
def admin_debug_test_login():
    """CodiBank 앱과 동일한 방식으로 Supabase signInWithPassword를 서버에서 직접 테스트.
    프론트 config.js 없이도 Supabase 인증 동작을 검증합니다 (MASTER 전용).
    """
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403

    import requests as _rq
    data     = request.get_json(silent=True) or {}
    email    = str(data.get("email")    or "admin@codibank.kr").strip().lower()
    password = str(data.get("password") or "pass1234").strip()

    _sb      = supabase_url()
    svc_key  = os.environ.get("SUPABASE_SERVICE_KEY", "")
    anon_key = os.environ.get("SUPABASE_ANON_KEY", "")

    result = {
        "email":            email,
        "supabase_url":     _sb,
        "service_key_set":  bool(svc_key),
        "anon_key_set":     bool(anon_key),
        "anon_key_format":  ("JWT(eyJ...)" if anon_key.startswith("eyJ") else
                             ("sb_publishable(신형-미지원)" if anon_key.startswith("sb_") else
                              ("미설정" if not anon_key else "알수없는형식"))),
    }

    # ── 테스트 1: service_role 키로 해당 유저 정보 조회 (계정 상태 재확인)
    try:
        lr = _rq.get(f"{_sb}/auth/v1/admin/users?per_page=1000",
                      headers={"apikey": svc_key, "Authorization": f"Bearer {svc_key}",
                               "Content-Type": "application/json"}, timeout=10)
        if lr.status_code == 200:
            ud  = lr.json()
            ul  = ud.get("users", ud) if isinstance(ud, dict) else ud
            usr = next((u for u in ul if u.get("email","").lower() == email), None)
            if usr:
                result["user_exists"]         = True
                result["email_confirmed_at"]  = usr.get("email_confirmed_at") or "NULL"
                result["confirmed"]           = bool(usr.get("email_confirmed_at"))
                result["last_sign_in"]        = usr.get("last_sign_in_at") or "없음"
                result["uid"]                 = usr.get("id","")
            else:
                result["user_exists"] = False
                result["user_exists_note"] = "Supabase에 해당 이메일 없음"
    except Exception as e:
        result["user_lookup_error"] = str(e)[:100]

    # ── 테스트 2: anon key로 실제 signInWithPassword 호출 (앱과 동일)
    if anon_key:
        try:
            tr = _rq.post(
                f"{_sb}/auth/v1/token?grant_type=password",
                headers={"apikey": anon_key, "Content-Type": "application/json"},
                json={"email": email, "password": password},
                timeout=10
            )
            result["signin_status"]   = tr.status_code
            result["signin_ok"]       = tr.status_code == 200
            if tr.status_code == 200:
                rd = tr.json()
                result["signin_result"] = "✅ 로그인 성공"
                result["token_type"]    = rd.get("token_type", "")
                result["access_token"]  = (rd.get("access_token") or "")[:30] + "..."
            else:
                rd = tr.json()
                result["signin_result"] = "❌ 로그인 실패"
                result["signin_error"]  = rd.get("error_description") or rd.get("msg") or tr.text[:200]
                result["signin_code"]   = rd.get("error", "")
        except Exception as e:
            result["signin_exception"] = str(e)[:100]
    else:
        result["signin_result"] = "⚠ SUPABASE_ANON_KEY 미설정 — anon key 없이는 앱 로그인 불가"
        result["signin_ok"]     = False

    # ── 테스트 3: service_role 키로 임시 비밀번호 강제 리셋 (테스트 목적)
    if data.get("reset_password") and svc_key and result.get("uid"):
        try:
            rr = _rq.put(
                f"{_sb}/auth/v1/admin/users/{result['uid']}",
                headers={"apikey": svc_key, "Authorization": f"Bearer {svc_key}",
                         "Content-Type": "application/json"},
                json={"password": password, "email_confirm": True},
                timeout=10
            )
            result["password_reset_status"] = rr.status_code
            result["password_reset_ok"]     = rr.status_code in (200, 201)
        except Exception as e:
            result["password_reset_error"] = str(e)[:100]

    # ── 진단 요약
    if not anon_key:
        result["diagnosis"] = "🔴 SUPABASE_ANON_KEY 환경변수 없음 → 앱 로그인 불가 (config.js의 키도 확인 필요)"
    elif not anon_key.startswith("eyJ"):
        result["diagnosis"] = "🔴 ANON_KEY가 JWT 형식(eyJ...)이 아님 → Supabase JS SDK v2는 JWT anon key 필요"
    elif not result.get("user_exists"):
        result["diagnosis"] = "🔴 Supabase에 계정 없음"
    elif not result.get("confirmed"):
        result["diagnosis"] = "🔴 이메일 미인증 (email_confirmed_at = NULL)"
    elif result.get("signin_ok"):
        result["diagnosis"] = "✅ 서버 로그인 성공. 앱 config.js의 SUPABASE_ANON_KEY 또는 URL 확인 필요"
    else:
        err = result.get("signin_error", "")
        if "Invalid login credentials" in err:
            result["diagnosis"] = "🔴 비밀번호 불일치 → reset_password:true 로 재호출하여 비밀번호 리셋"
        elif "Email not confirmed" in err:
            result["diagnosis"] = "🔴 이메일 미인증 (API는 confirmed 표시지만 실제 불일치)"
        else:
            result["diagnosis"] = f"🔴 로그인 실패: {err}"

    return jsonify(result)



@app.post("/admin/debug/create-bonus-table")
def admin_create_bonus_table():
    """user_usage_bonus 테이블이 없으면 생성 시도 (MASTER 전용).
    Supabase에서 SQL Editor로 직접 실행하는 DDL도 반환합니다.
    """
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403

    ddl = """
CREATE TABLE IF NOT EXISTS public.user_usage_bonus (
  email       TEXT NOT NULL,
  month       TEXT NOT NULL,
  total_bonus INTEGER DEFAULT 0,
  updated_at  TIMESTAMPTZ DEFAULT now(),
  updated_by  TEXT,
  PRIMARY KEY (email, month)
);
ALTER TABLE public.user_usage_bonus ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON public.user_usage_bonus
  FOR ALL USING (true) WITH CHECK (true);
"""
    import requests as _rq
    _sb  = supabase_url()
    _hdr = supabase_admin_headers()

    # Supabase REST API로 테이블 존재 확인
    try:
        test = _rq.get(f"{_sb}/rest/v1/user_usage_bonus?limit=1",
                        headers=_hdr, timeout=10)
        if test.status_code == 200:
            return jsonify({
                "ok": True,
                "table_exists": True,
                "message": "테이블이 이미 존재합니다. 보너스 지급이 정상 작동합니다.",
            })
        elif test.status_code == 404 or '42P01' in test.text:
            return jsonify({
                "ok": False,
                "table_exists": False,
                "message": "테이블 없음 — Supabase SQL Editor에서 아래 SQL을 실행하세요.",
                "sql": ddl.strip(),
                "sql_editor_url": f"https://supabase.com/dashboard/project/drgsayvlpzcacurcczjq/sql/new",
            })
        else:
            return jsonify({
                "ok": False,
                "table_exists": False,
                "status": test.status_code,
                "detail": test.text[:300],
                "sql": ddl.strip(),
            })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "sql": ddl.strip()})


@app.post("/admin/debug/create-items-table")
def admin_create_items_table():
    """user_items + user_item_bonus 테이블 DDL 반환 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403

    ddl = """
-- 아이템 등록 추적 테이블
CREATE TABLE IF NOT EXISTS public.user_items (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email       TEXT NOT NULL,
  category    TEXT,
  item_name   TEXT,
  image_url   TEXT,
  user_id     TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE public.user_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON public.user_items
  FOR ALL USING (true) WITH CHECK (true);
CREATE INDEX IF NOT EXISTS idx_user_items_email ON public.user_items(email);

-- 아이템 등록 보너스 테이블
CREATE TABLE IF NOT EXISTS public.user_item_bonus (
  email       TEXT NOT NULL,
  month       TEXT NOT NULL,
  total_bonus INTEGER DEFAULT 0,
  updated_at  TIMESTAMPTZ DEFAULT now(),
  updated_by  TEXT,
  PRIMARY KEY (email, month)
);
ALTER TABLE public.user_item_bonus ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON public.user_item_bonus
  FOR ALL USING (true) WITH CHECK (true);

-- [2026-04-09] 사용량 서버 동기화 테이블
CREATE TABLE IF NOT EXISTS public.user_usage (
  email              TEXT PRIMARY KEY,
  month              TEXT,
  day                TEXT,
  closet_count       INTEGER DEFAULT 0,
  codistyle_count    INTEGER DEFAULT 0,
  total_count        INTEGER DEFAULT 0,
  item_count         INTEGER DEFAULT 0,
  day_closet_count   INTEGER DEFAULT 0,
  day_codi_count     INTEGER DEFAULT 0,
  day_total          INTEGER DEFAULT 0,
  day_item_count     INTEGER DEFAULT 0,
  updated_at         TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE public.user_usage ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON public.user_usage
  FOR ALL USING (true) WITH CHECK (true);
"""
    import requests as _rq
    _sb  = supabase_url()
    _hdr = supabase_admin_headers()
    results = {}
    for tbl in ["user_items", "user_item_bonus", "user_usage"]:
        try:
            test = _rq.get(f"{_sb}/rest/v1/{tbl}?limit=1", headers=_hdr, timeout=10)
            results[tbl] = "exists" if test.status_code == 200 else "missing"
        except Exception as e:
            results[tbl] = f"error:{str(e)[:40]}"
    all_exist = all(v == "exists" for v in results.values())
    return jsonify({
        "ok": True,
        "tables": results,
        "all_exist": all_exist,
        "message": "모든 테이블 정상" if all_exist else "Supabase SQL Editor에서 아래 SQL을 실행하세요.",
        "sql": ddl.strip(),
        "sql_editor_url": "https://supabase.com/dashboard/project/drgsayvlpzcacurcczjq/sql/new",
    })



# [2026-04-15] 서버 시작 시 R2 상태 즉시 확인 (gunicorn에서도 작동)
_r2_startup = _get_r2()
if _r2_startup:
    print(f"[STARTUP] ✅ R2 연결 OK — bucket={_R2_BUCKET}, pub={_R2_PUB_URL or '(없음)'}")
else:
    print("[STARTUP] ⚠️  R2 미연결 — 이미지가 로컬에만 저장됩니다 (Render 재시작 시 삭제됨)")
    print("[STARTUP]    Render Environment에 R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_PUBLIC_URL 설정 필요")


# ══════════════════════════════════════════════════════════════
# [2026-04-15] R2 Storage 진단
# ══════════════════════════════════════════════════════════════
@app.get("/admin/debug/r2-status")
def debug_r2_status():
    """R2 스토리지 연결 상태 + 환경변수 진단"""
    env_check = {
        "R2_ENDPOINT": bool(os.getenv("R2_ENDPOINT", "")),
        "R2_ACCOUNT_ID": bool(os.getenv("R2_ACCOUNT_ID", "")),
        "R2_ACCESS_KEY_ID": bool(os.getenv("R2_ACCESS_KEY_ID", "")),
        "R2_SECRET_ACCESS_KEY": bool(os.getenv("R2_SECRET_ACCESS_KEY", "")),
        "R2_BUCKET_NAME": os.getenv("R2_BUCKET_NAME", "codibank"),
        "R2_PUBLIC_URL": os.getenv("R2_PUBLIC_URL", "(미설정)"),
    }
    r2 = _get_r2()
    r2_connected = r2 is not None
    r2_file_count = 0
    r2_sample_files = []
    if r2_connected:
        try:
            resp = r2.list_objects_v2(Bucket=_R2_BUCKET, Prefix="uploads/", MaxKeys=20)
            contents = resp.get("Contents", [])
            r2_file_count = resp.get("KeyCount", len(contents))
            r2_sample_files = [c["Key"] for c in contents[:10]]
        except Exception as e:
            r2_file_count = -1
            r2_sample_files = [f"list error: {str(e)[:60]}"]
    local_files = []
    try:
        local_files = os.listdir(_UPLOAD_DIR)[:10]
    except:
        pass
    return jsonify({
        "ok": True,
        "r2_connected": r2_connected,
        "r2_file_count": r2_file_count,
        "r2_sample_files": r2_sample_files,
        "local_upload_dir": _UPLOAD_DIR,
        "local_file_count": len(os.listdir(_UPLOAD_DIR)) if os.path.isdir(_UPLOAD_DIR) else 0,
        "local_sample_files": local_files,
        "env_vars": env_check,
        "guide": "R2 미연결 시 Render Environment에 R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL 설정 필요" if not r2_connected else "R2 정상 연결됨",
    })


# ═══════════════════════════════════════════════════════════════════════
#  /api/proxy-image  — 쇼핑몰 이미지 URL CORS/Hotlink 우회 프록시
#  [2026-04-17] 쇼핑몰 이미지 URL로 코디하기 불가 문제 해결
# ═══════════════════════════════════════════════════════════════════════

# ── 설정 ──
_PROXY_MAX_IMAGE_BYTES = 15 * 1024 * 1024   # 15MB
_PROXY_REQUEST_TIMEOUT = 12                  # 초
_PROXY_MAX_REDIRECTS = 5

# 쇼핑몰 도메인 → Referer 위조 맵 (Hotlink 방지 우회)
_PROXY_REFERER_MAP = {
    # 무신사
    "image.msscdn.net":              "https://www.musinsa.com/",
    "msscdn.net":                    "https://www.musinsa.com/",
    "static.msscdn.net":             "https://www.musinsa.com/",
    "www.musinsa.com":               "https://www.musinsa.com/",
    "musinsa.com":                   "https://www.musinsa.com/",
    # 29CM
    "img.29cm.co.kr":                "https://www.29cm.co.kr/",
    "product.29cm.co.kr":            "https://www.29cm.co.kr/",
    "static.29cm.co.kr":             "https://www.29cm.co.kr/",
    "www.29cm.co.kr":                "https://www.29cm.co.kr/",
    # W컨셉
    "img.wconcept.co.kr":            "https://www.wconcept.co.kr/",
    "product.wconcept.co.kr":        "https://www.wconcept.co.kr/",
    "www.wconcept.co.kr":            "https://www.wconcept.co.kr/",
    # SSF Shop
    "image.ssfshop.com":             "https://www.ssfshop.com/",
    "img.ssfshop.com":               "https://www.ssfshop.com/",
    "www.ssfshop.com":               "https://www.ssfshop.com/",
    # 지그재그
    "cf.product-image.s.zigzag.kr":  "https://zigzag.kr/",
    "image.zigzag.kr":               "https://zigzag.kr/",
    "zigzag.kr":                     "https://zigzag.kr/",
    # 에이블리
    "img.a-bly.com":                 "https://m.a-bly.com/",
    "a-bly.com":                     "https://m.a-bly.com/",
    "m.a-bly.com":                   "https://m.a-bly.com/",
    # 쿠팡
    "image10.coupangcdn.com":        "https://www.coupang.com/",
    "image6.coupangcdn.com":         "https://www.coupang.com/",
    "image7.coupangcdn.com":         "https://www.coupang.com/",
    "image8.coupangcdn.com":         "https://www.coupang.com/",
    "image9.coupangcdn.com":         "https://www.coupang.com/",
    "thumbnail6.coupangcdn.com":     "https://www.coupang.com/",
    "thumbnail7.coupangcdn.com":     "https://www.coupang.com/",
    "thumbnail8.coupangcdn.com":     "https://www.coupang.com/",
    "thumbnail9.coupangcdn.com":     "https://www.coupang.com/",
    "thumbnail10.coupangcdn.com":    "https://www.coupang.com/",
    "static.coupangcdn.com":         "https://www.coupang.com/",
    "coupangcdn.com":                "https://www.coupang.com/",
    "www.coupang.com":               "https://www.coupang.com/",
    "coupang.com":                   "https://www.coupang.com/",
    # 네이버 스마트스토어
    "shop-phinf.pstatic.net":        "https://smartstore.naver.com/",
    "shopping-phinf.pstatic.net":    "https://smartstore.naver.com/",
    "smartstore.naver.com":          "https://smartstore.naver.com/",
    "brand.naver.com":               "https://brand.naver.com/",
    # 룩핀
    "img.lookpin.co.kr":             "https://lookpin.co.kr/",
    "lookpin.co.kr":                 "https://lookpin.co.kr/",
    # 브랜디
    "d2emtenuzntcob.cloudfront.net": "https://www.brandi.co.kr/",
    "www.brandi.co.kr":              "https://www.brandi.co.kr/",
    "brandi.co.kr":                  "https://www.brandi.co.kr/",
}

# 차단이 강한 사이트 목록 (사용자에게 친절하게 안내)
_PROXY_HARD_BLOCK_HINTS = {
    "coupang.com":        "쿠팡",
    "coupangcdn.com":     "쿠팡",
    "smartstore.naver.com": "네이버 스마트스토어",
    "brand.naver.com":    "네이버 브랜드스토어",
}

_PROXY_ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/webp",
    "image/gif", "image/avif", "image/bmp",
}


def _proxy_is_private_ip(hostname: str) -> bool:
    """SSRF 방지: DNS resolve 후 private/loopback/link-local IP 검사."""
    if not hostname:
        return True
    try:
        infos = socket.getaddrinfo(hostname, None)
    except Exception:
        return True  # DNS 실패 시 안전 차단
    for info in infos:
        ip_str = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if (ip.is_private or ip.is_loopback or ip.is_link_local or
                ip.is_multicast or ip.is_reserved or ip.is_unspecified):
            return True
    return False


def _proxy_pick_referer(host: str):
    """쇼핑몰 Referer 자동 감지 (서브도메인 포함)."""
    if not host:
        return None
    host = host.lower()
    if host in _PROXY_REFERER_MAP:
        return _PROXY_REFERER_MAP[host]
    parts = host.split(".")
    for i in range(len(parts)):
        candidate = ".".join(parts[i:])
        if candidate in _PROXY_REFERER_MAP:
            return _PROXY_REFERER_MAP[candidate]
    return None


@app.route("/api/proxy-image", methods=["POST"])
def api_proxy_image():
    """쇼핑몰 이미지 URL → 서버가 대신 받아 base64 dataURL로 전달.

    Body:  { "url": "<image url>" }
    200:   { ok: True, dataUrl: "data:image/...;base64,...", contentType, bytes }
    4xx:   { ok: False, error: "..." }
    """
    try:
        data = request.get_json(silent=True) or {}
    except Exception:
        data = {}
    img_url = str(data.get("url", "")).strip()

    # ── [1] URL 기본 검증 ──
    if not img_url:
        return jsonify({"ok": False, "error": "URL is required"}), 400
    if len(img_url) > 2048:
        return jsonify({"ok": False, "error": "URL too long"}), 400

    parsed = urllib.parse.urlparse(img_url)
    if parsed.scheme not in ("http", "https"):
        return jsonify({"ok": False, "error": "Only http/https URLs allowed"}), 400
    if not parsed.hostname:
        return jsonify({"ok": False, "error": "Invalid hostname"}), 400

    # ── [2] SSRF 방지 ──
    if _proxy_is_private_ip(parsed.hostname):
        return jsonify({"ok": False, "error": "Blocked: internal/private network"}), 400

    _lower_host = parsed.hostname.lower()
    if _lower_host in ("localhost", "localhost.localdomain", "ip6-localhost"):
        return jsonify({"ok": False, "error": "Blocked: localhost"}), 400
    if parsed.port is not None and parsed.port not in (80, 443, 8080, 8443):
        return jsonify({"ok": False, "error": "Blocked: non-standard port"}), 400

    # ── [3] 요청 헤더 (Hotlink 우회 + 모바일 UA) ──
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/16.6 Mobile/15E148 Safari/604.1"
        ),
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    referer = _proxy_pick_referer(parsed.hostname)
    if referer:
        headers["Referer"] = referer
    else:
        headers["Referer"] = f"{parsed.scheme}://{parsed.hostname}/"

    # ── [4] 이미지 다운로드 ──
    try:
        resp = http_requests.get(
            img_url,
            headers=headers,
            timeout=_PROXY_REQUEST_TIMEOUT,
            stream=True,
            allow_redirects=True,
        )
    except http_requests.exceptions.Timeout:
        return jsonify({"ok": False, "error": "Remote server timed out"}), 504
    except http_requests.exceptions.ConnectionError:
        return jsonify({"ok": False, "error": "Could not connect to remote server"}), 502
    except http_requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "error": f"Fetch failed: {str(e)[:100]}"}), 502

    # 리다이렉트 재검증 (공개 URL → 사설 IP 우회 공격 방어)
    if len(resp.history) > _PROXY_MAX_REDIRECTS:
        resp.close()
        return jsonify({"ok": False, "error": "Too many redirects"}), 502
    if resp.history:
        final_parsed = urllib.parse.urlparse(resp.url)
        if final_parsed.hostname and _proxy_is_private_ip(final_parsed.hostname):
            resp.close()
            return jsonify({"ok": False, "error": "Blocked: redirect to internal network"}), 400

    # ── [5] 응답 상태 ──
    if resp.status_code != 200:
        resp.close()
        return jsonify({"ok": False, "error": f"Remote returned HTTP {resp.status_code}"}), 502

    # ── [6] Content-Type 검증 ──
    ct = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    if not ct.startswith("image/"):
        resp.close()
        return jsonify({"ok": False, "error": f'Not an image (Content-Type: {ct or "unknown"})'}), 400

    # ── [7] 스트리밍 다운로드 + 사이즈 제한 ──
    chunks = []
    total = 0
    try:
        for chunk in resp.iter_content(chunk_size=65536):
            if not chunk:
                continue
            total += len(chunk)
            if total > _PROXY_MAX_IMAGE_BYTES:
                resp.close()
                return jsonify({
                    "ok": False,
                    "error": f"Image too large (>{_PROXY_MAX_IMAGE_BYTES // (1024 * 1024)}MB)"
                }), 413
            chunks.append(chunk)
    except Exception as e:
        resp.close()
        return jsonify({"ok": False, "error": f"Download interrupted: {str(e)[:100]}"}), 502
    finally:
        resp.close()

    content = b"".join(chunks)
    if not content:
        return jsonify({"ok": False, "error": "Empty image response"}), 502

    # ── [8] 매직바이트 검증 (Content-Type 위장 방지) ──
    if not (
        content.startswith(b"\xff\xd8\xff") or           # JPEG
        content.startswith(b"\x89PNG\r\n\x1a\n") or      # PNG
        content.startswith(b"GIF8") or                    # GIF
        content.startswith(b"RIFF") or                    # WebP (RIFF....WEBP)
        content.startswith(b"BM") or                      # BMP
        (len(content) >= 12 and content[4:12] == b"ftypavif")  # AVIF
    ):
        return jsonify({"ok": False, "error": "File signature does not match an image"}), 400

    # ── [9] base64 dataURL 반환 ──
    b64 = base64.b64encode(content).decode("ascii")
    return jsonify({
        "ok": True,
        "dataUrl": f"data:{ct};base64,{b64}",
        "contentType": ct,
        "bytes": len(content),
    }), 200


# ═══════════════════════════════════════════════════════════════════════
#  /api/extract-product-images  — 쇼핑몰 상품 페이지 URL에서 이미지 자동 추출
#  [2026-04-17] 사용자가 상품 페이지 URL을 붙여넣으면 이미지 후보를 뽑아줌
# ═══════════════════════════════════════════════════════════════════════

_EXTRACT_MAX_HTML_BYTES = 3 * 1024 * 1024   # HTML 3MB 제한
_EXTRACT_TIMEOUT = 10
_EXTRACT_MAX_IMAGES = 12

# 이미지 확장자 패턴
_IMG_EXT_RE = re.compile(r"\.(jpe?g|png|webp|avif|gif)(\?|$|#)", re.IGNORECASE)
# URL에서 크기 힌트 패턴 (_500, 500x600, size=500 등)
_SIZE_HINT_RE = re.compile(r"[_/=-]((\d{3,4})(?:x(\d{3,4}))?)[_./-]", re.IGNORECASE)

# 제외할 이미지 패턴 (아이콘, 로고, 버튼 등)
_IMG_SKIP_PATTERNS = (
    "icon", "logo", "favicon", "button", "btn_", "arrow", "badge",
    "sprite", "bg_", "banner_", "/nav/", "/header/", "/footer/",
    "placeholder", "loading", "empty", "blank", "default",
    "pixel.gif", "blank.gif", "spacer", "transparent",
    "facebook", "twitter", "instagram", "kakao", "naver_",
    "qr_", "barcode", "share_",
)


def _resolve_url(base_url: str, img_url: str) -> str:
    """상대 경로 → 절대 경로."""
    if not img_url:
        return ""
    img_url = img_url.strip().strip('"\'')
    if img_url.startswith(("http://", "https://")):
        return img_url
    if img_url.startswith("//"):
        base_scheme = urllib.parse.urlparse(base_url).scheme or "https"
        return f"{base_scheme}:{img_url}"
    if img_url.startswith("/"):
        p = urllib.parse.urlparse(base_url)
        return f"{p.scheme}://{p.netloc}{img_url}"
    # 상대 경로
    return urllib.parse.urljoin(base_url, img_url)


def _extract_meta_image(html: str, prop_names) -> list:
    """OG 태그 / Twitter 카드 등 메타 이미지 추출."""
    results = []
    for prop in prop_names:
        # <meta property="og:image" content="..."> 또는 name="..."
        for m in re.finditer(
            r'<meta\s+[^>]*(?:property|name)\s*=\s*["\']' + re.escape(prop) + r'["\'][^>]*>',
            html, re.IGNORECASE
        ):
            tag = m.group(0)
            cm = re.search(r'content\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
            if cm:
                results.append(cm.group(1))
    return results


def _extract_img_src(html: str) -> list:
    """<img> 태그의 src/data-src/data-original/srcset에서 URL 추출."""
    results = []
    # <img ... src="..." data-src="..." data-original="...">
    for m in re.finditer(r'<img\s+[^>]+>', html, re.IGNORECASE):
        tag = m.group(0)
        # 우선순위: data-src > data-original > src
        for attr in ("data-src", "data-original", "data-lazy", "data-lazy-src", "data-zoom-image", "src"):
            am = re.search(r'\b' + re.escape(attr) + r'\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
            if am:
                url = am.group(1).strip()
                if url and not url.startswith("data:"):
                    results.append(url)
                break
        # srcset: 여러 URL 중 가장 큰 것
        sm = re.search(r'\bsrcset\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if sm:
            # "url1 1x, url2 2x" 또는 "url1 500w, url2 1000w"
            best_url, best_w = None, 0
            for part in sm.group(1).split(","):
                part = part.strip()
                if not part:
                    continue
                bits = part.split()
                url = bits[0]
                w = 0
                if len(bits) > 1:
                    try:
                        w_str = bits[1].rstrip("wx")
                        w = int(float(w_str) * (1000 if bits[1].endswith("x") else 1))
                    except (ValueError, TypeError):
                        pass
                if w > best_w:
                    best_w, best_url = w, url
            if best_url:
                results.append(best_url)
    return results


def _score_image(url: str) -> int:
    """이미지 URL에 품질 점수 부여 (높을수록 상품 이미지 가능성 높음)."""
    score = 0
    url_lower = url.lower()

    # 제외 패턴 포함 시 대폭 감점
    for bad in _IMG_SKIP_PATTERNS:
        if bad in url_lower:
            score -= 50

    # 확장자 확인
    if _IMG_EXT_RE.search(url):
        score += 10

    # 상품 이미지 힌트
    if any(k in url_lower for k in ("product", "goods", "item", "상품", "detail", "main")):
        score += 20

    # 크기 힌트 (크면 높은 점수)
    sm = _SIZE_HINT_RE.search(url)
    if sm:
        try:
            size = int(sm.group(2))
            if size >= 500:
                score += 15
            elif size >= 300:
                score += 8
            elif size >= 100:
                score += 2
            else:
                score -= 10  # 너무 작음 (썸네일/아이콘)
        except (ValueError, TypeError):
            pass

    # 쇼핑몰 CDN 도메인 보너스 (기존 _PROXY_REFERER_MAP)
    for shop_domain in _PROXY_REFERER_MAP.keys():
        if shop_domain in url_lower:
            score += 25
            break

    return score


@app.route("/api/extract-product-images", methods=["POST"])
def api_extract_product_images():
    """쇼핑몰 상품 페이지 URL → 이미지 후보 URL 리스트 반환.

    Body:  { "url": "<product page url>" }
    200:   { ok: True, images: [url1, url2, ...], pageTitle: "...", sourceUrl: "..." }
    4xx:   { ok: False, error: "..." }
    """
    try:
        data = request.get_json(silent=True) or {}
    except Exception:
        data = {}
    page_url = str(data.get("url", "")).strip()

    # ── URL 검증 (proxy-image와 동일 로직) ──
    if not page_url:
        return jsonify({"ok": False, "error": "URL is required"}), 400
    if len(page_url) > 2048:
        return jsonify({"ok": False, "error": "URL too long"}), 400

    parsed = urllib.parse.urlparse(page_url)
    if parsed.scheme not in ("http", "https"):
        return jsonify({"ok": False, "error": "Only http/https URLs allowed"}), 400
    if not parsed.hostname:
        return jsonify({"ok": False, "error": "Invalid hostname"}), 400

    # SSRF 방지
    if _proxy_is_private_ip(parsed.hostname):
        return jsonify({"ok": False, "error": "Blocked: internal/private network"}), 400
    if parsed.hostname.lower() in ("localhost", "localhost.localdomain", "ip6-localhost"):
        return jsonify({"ok": False, "error": "Blocked: localhost"}), 400
    if parsed.port is not None and parsed.port not in (80, 443, 8080, 8443):
        return jsonify({"ok": False, "error": "Blocked: non-standard port"}), 400

    # ── HTML 페이지 fetch ──
    # [2026-04-17] 헤더 강화: 실제 Chrome 브라우저처럼 위장 + 사이트별 Referer
    # 데스크톱 Chrome UA가 모바일 Safari보다 차단 덜 당함 (봇 탐지 우회)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        # Chrome Client Hints (실제 Chrome이 항상 보냄 — 없으면 봇 판정)
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        # Fetch 메타 (네비게이션 요청처럼 보이게)
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    # 쇼핑몰 도메인이면 해당 사이트를 Referer로 (구글에서 검색해 온 것처럼)
    _page_referer = _proxy_pick_referer(parsed.hostname)
    if _page_referer:
        headers["Referer"] = _page_referer
    else:
        # 일반 사이트는 구글 검색에서 왔다고 위장
        headers["Referer"] = "https://www.google.com/"
    try:
        resp = http_requests.get(
            page_url,
            headers=headers,
            timeout=_EXTRACT_TIMEOUT,
            stream=True,
            allow_redirects=True,
        )
    except http_requests.exceptions.Timeout:
        return jsonify({"ok": False, "error": "Page loading timed out"}), 504
    except http_requests.exceptions.ConnectionError:
        return jsonify({"ok": False, "error": "Could not connect to page"}), 502
    except http_requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "error": f"Fetch failed: {str(e)[:100]}"}), 502

    # 리다이렉트 후 재검증
    final_url = resp.url
    if resp.history:
        fp = urllib.parse.urlparse(final_url)
        if fp.hostname and _proxy_is_private_ip(fp.hostname):
            resp.close()
            return jsonify({"ok": False, "error": "Blocked: redirect to internal network"}), 400

    if resp.status_code != 200:
        resp.close()
        # 강한 차단 사이트 친절 안내
        _hint = None
        _host_lower = parsed.hostname.lower()
        for _bad_host, _shop_name in _PROXY_HARD_BLOCK_HINTS.items():
            if _bad_host in _host_lower:
                _hint = _shop_name
                break
        if _hint:
            err_msg = f"{_hint} is actively blocking automated access. Please save the image and upload directly."
            print(f"[extract-product-images] ⚠️ {_hint} blocked: HTTP {resp.status_code} for {page_url[:100]}")
            return jsonify({
                "ok": False,
                "error": err_msg,
                "hardBlocked": True,
                "shopName": _hint,
            }), 502
        print(f"[extract-product-images] HTTP {resp.status_code} for {page_url[:100]}")
        return jsonify({"ok": False, "error": f"Page returned HTTP {resp.status_code}"}), 502

    ct = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    if ct and "html" not in ct and "xml" not in ct:
        resp.close()
        return jsonify({"ok": False, "error": f"Not an HTML page (Content-Type: {ct})"}), 400

    # HTML 스트리밍 with 사이즈 제한
    html_bytes = []
    total = 0
    try:
        for chunk in resp.iter_content(chunk_size=65536):
            if not chunk:
                continue
            total += len(chunk)
            if total > _EXTRACT_MAX_HTML_BYTES:
                break   # 초과해도 지금까지 받은 부분으로 파싱 시도
            html_bytes.append(chunk)
    except Exception as e:
        resp.close()
        return jsonify({"ok": False, "error": f"Download interrupted: {str(e)[:100]}"}), 502
    finally:
        resp.close()

    raw = b"".join(html_bytes)
    # 인코딩 감지
    try:
        # HTML meta charset 우선
        cm = re.search(rb'<meta\s+[^>]*charset\s*=\s*["\']?([^"\'\s>]+)', raw[:2048], re.IGNORECASE)
        encoding = cm.group(1).decode("ascii", errors="ignore") if cm else (resp.encoding or "utf-8")
        html = raw.decode(encoding, errors="replace")
    except Exception:
        html = raw.decode("utf-8", errors="replace")

    # ── 페이지 타이틀 추출 ──
    page_title = ""
    tm = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if tm:
        page_title = re.sub(r"\s+", " ", tm.group(1)).strip()[:200]

    # ── 이미지 후보 수집 ──
    candidates = []

    # 1) OG/Twitter 메타 이미지 (최상위 신뢰)
    for url in _extract_meta_image(html, [
        "og:image", "og:image:secure_url", "og:image:url",
        "twitter:image", "twitter:image:src",
        "product:image", "image",
    ]):
        candidates.append((url, 100))  # 메타는 고정 100점

    # 2) JSON-LD Product.image 파싱 (일부 쇼핑몰 지원)
    for m in re.finditer(
        r'<script\s+[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.IGNORECASE | re.DOTALL
    ):
        block = m.group(1)
        for im in re.finditer(r'"image"\s*:\s*("([^"]+)"|\[([^\]]+)\])', block):
            if im.group(2):
                candidates.append((im.group(2), 90))
            elif im.group(3):
                for url_m in re.finditer(r'"([^"]+)"', im.group(3)):
                    candidates.append((url_m.group(1), 85))

    # 3) <img> 태그 전체
    for url in _extract_img_src(html):
        candidates.append((url, _score_image(url)))

    # ── 정규화 + 중복 제거 + 필터 + 정렬 ──
    seen = set()
    dedup = []
    for url, base_score in candidates:
        if not url:
            continue
        abs_url = _resolve_url(final_url, url)
        if not abs_url or not abs_url.startswith(("http://", "https://")):
            continue
        # 크기 매우 작은 이미지 제거 (?w=50, /50x50/ 등)
        small_m = _SIZE_HINT_RE.search(abs_url.lower())
        if small_m:
            try:
                if int(small_m.group(2)) < 150:
                    continue
            except (ValueError, TypeError):
                pass
        # data:, javascript: 등 제외
        if abs_url.lower().startswith(("data:", "javascript:", "about:")):
            continue
        # 확장자 없고 알려진 CDN도 아니면 제외
        if not _IMG_EXT_RE.search(abs_url):
            is_cdn = any(shop in abs_url.lower() for shop in _PROXY_REFERER_MAP.keys())
            if not is_cdn and "image" not in abs_url.lower() and "img" not in abs_url.lower():
                continue
        if abs_url in seen:
            continue
        seen.add(abs_url)
        # 최종 점수 (기본 점수 + 스코어링)
        final_score = base_score + (_score_image(abs_url) if base_score < 90 else 0)
        if final_score < -20:
            continue
        dedup.append((abs_url, final_score))

    # 점수 내림차순 정렬 후 상위 N개
    dedup.sort(key=lambda x: x[1], reverse=True)
    images = [url for url, _ in dedup[:_EXTRACT_MAX_IMAGES]]

    if not images:
        return jsonify({
            "ok": False,
            "error": "No product images found on this page",
            "pageTitle": page_title,
        }), 404

    return jsonify({
        "ok": True,
        "images": images,
        "pageTitle": page_title,
        "sourceUrl": final_url,
        "count": len(images),
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8787"))
    # ✅ 안정성 기본값: debug OFF
    # - debug=True(리로더)일 때는 프로세스가 2개 떠서(port가 2개 LISTEN으로 보임)
    #   사용자가 "포트가 점유"되었다고 오해하기 쉽습니다.
    # - 투자자 데모/외부 공유 목적이면 debug=False가 훨씬 안전합니다.
    debug = str(os.getenv("CODIBANK_DEBUG", "0")).strip().lower() in ("1", "true", "yes", "on")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
