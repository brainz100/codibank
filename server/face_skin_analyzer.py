"""
face_skin_analyzer.py — 코디뱅크 퍼스널컬러 Phase 2 피부톤 분석 모듈

[2026-04-08] 최초 작성
- 셀카 이미지에서 피부 영역 추출 → CIELab 수치 분석
- face-parsing 대체: HSV + YCbCr 듀얼 마스크 기반 피부 감지
- numpy + PIL만 사용 (추가 ML 라이브러리 불필요, Render 호환)

파이프라인:
  1) 이미지 로드 → 중앙 얼굴 영역 크롭
  2) HSV + YCbCr 듀얼 마스크로 피부 픽셀 감지
  3) 이마/볼/턱 영역 가중 평균으로 메이크업 영향 최소화
  4) RGB → CIELab 변환
  5) ITA(Individual Typology Angle) 계산
  6) 12서브타입 사전 추정 (GPT 보조 힌트)
  
의존성: numpy, PIL (Pillow)
"""

from __future__ import annotations
import io
import math
from typing import Dict, Any, Optional, Tuple, List

import numpy as np
from PIL import Image


# ═══════════════════════════════════════════════════════
# 1. RGB → CIELab 변환 (D65 조명 기준)
# ═══════════════════════════════════════════════════════

def _srgb_to_linear(c: float) -> float:
    """sRGB [0,1] → linear RGB"""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb_to_lab(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """RGB (0-255) → CIELab (L*, a*, b*)"""
    rl = _srgb_to_linear(r / 255.0)
    gl = _srgb_to_linear(g / 255.0)
    bl = _srgb_to_linear(b / 255.0)
    
    # linear RGB → XYZ (D65 reference)
    x = rl * 0.4124564 + gl * 0.3575761 + bl * 0.1804375
    y = rl * 0.2126729 + gl * 0.7151522 + bl * 0.0721750
    z = rl * 0.0193339 + gl * 0.1191920 + bl * 0.9503041
    
    # D65 백색점
    xn, yn, zn = 0.95047, 1.0, 1.08883
    
    def f(t):
        return t ** (1 / 3) if t > 0.008856 else (903.3 * t + 16) / 116
    
    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return L, a, b_val


def rgb_array_to_lab(pixels: np.ndarray) -> Tuple[float, float, float]:
    """RGB 픽셀 배열 (N, 3) → 평균 CIELab"""
    if len(pixels) == 0:
        return 0.0, 0.0, 0.0
    
    labs = np.array([rgb_to_lab(int(p[0]), int(p[1]), int(p[2])) for p in pixels])
    return float(np.median(labs[:, 0])), float(np.median(labs[:, 1])), float(np.median(labs[:, 2]))


# ═══════════════════════════════════════════════════════
# 2. ITA (Individual Typology Angle) 계산
# ═══════════════════════════════════════════════════════

def calculate_ita(L: float, b: float) -> float:
    """ITA = arctan((L* - 50) / b*) × (180/π)
    높을수록 밝은 피부, 낮을수록 어두운 피부
    """
    if abs(b) < 0.001:
        return 90.0 if L > 50 else -90.0
    return math.degrees(math.atan2(L - 50, b))


def ita_to_skin_category(ita: float) -> str:
    """ITA → 피부 밝기 카테고리 (Chardon et al. 1991 기준)"""
    if ita > 55:
        return "매우 밝은"
    elif ita > 41:
        return "밝은"
    elif ita > 28:
        return "중간"
    elif ita > 10:
        return "어두운"
    else:
        return "매우 어두운"


# ═══════════════════════════════════════════════════════
# 3. 피부 픽셀 감지 (HSV + YCbCr 듀얼 마스크)
# ═══════════════════════════════════════════════════════

def _detect_skin_pixels(img_array: np.ndarray) -> np.ndarray:
    """
    RGB 이미지 배열에서 피부 픽셀만 추출.
    HSV + YCbCr 듀얼 마스크 방식 — 조명 변화에 강건.
    
    Returns: (N, 3) RGB 피부 픽셀 배열
    """
    h, w, _ = img_array.shape
    r, g, b = img_array[:, :, 0].astype(float), img_array[:, :, 1].astype(float), img_array[:, :, 2].astype(float)
    
    # ── HSV 변환 (피부 Hue 범위 필터) ──
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin + 1e-10
    
    # Hue 계산 (0-360)
    hue = np.zeros_like(r)
    mask_r = (cmax == r)
    mask_g = (cmax == g) & ~mask_r
    mask_b = ~mask_r & ~mask_g
    hue[mask_r] = 60 * (((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6)
    hue[mask_g] = 60 * (((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2)
    hue[mask_b] = 60 * (((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4)
    
    sat = delta / (cmax + 1e-10)
    val = cmax / 255.0
    
    # HSV 피부 범위: H(0~50°), S(0.1~0.8), V(0.2~0.95)
    hsv_mask = (
        ((hue >= 0) & (hue <= 50)) &
        (sat >= 0.10) & (sat <= 0.80) &
        (val >= 0.20) & (val <= 0.95)
    )
    
    # ── YCbCr 변환 (피부색 크로마 범위 필터) ──
    y_val = 0.299 * r + 0.587 * g + 0.114 * b
    cb = 128 - 0.169 * r - 0.331 * g + 0.500 * b
    cr = 128 + 0.500 * r - 0.419 * g - 0.081 * b
    
    # YCbCr 피부 범위 (Chai & Ngan 논문 기준, 아시안 스킨톤 확장)
    ycbcr_mask = (
        (y_val > 60) &
        (cb >= 77) & (cb <= 135) &
        (cr >= 130) & (cr <= 180)
    )
    
    # ── RGB 기본 규칙 (피부는 R > G > B 경향) ──
    rgb_rule = (r > 60) & (g > 40) & (b > 20) & (r > g) & (r > b) & (abs(r - g) > 10)
    
    # 듀얼 마스크: HSV와 YCbCr 중 하나라도 + RGB 규칙
    combined_mask = ((hsv_mask | ycbcr_mask) & rgb_rule)
    
    skin_pixels = img_array[combined_mask]
    return skin_pixels


# ═══════════════════════════════════════════════════════
# 4. 얼굴 영역 크롭 + 가중 영역 분석
# ═══════════════════════════════════════════════════════

def _crop_face_region(img: Image.Image) -> Image.Image:
    """셀카 이미지에서 중앙 얼굴 영역 크롭 (상위 20~70%, 좌우 20~80%)"""
    w, h = img.size
    # 셀카 기준: 얼굴은 대략 중앙 상단에 위치
    top = int(h * 0.15)
    bottom = int(h * 0.70)
    left = int(w * 0.15)
    right = int(w * 0.85)
    return img.crop((left, top, right, bottom))


def _analyze_face_zones(img_array: np.ndarray) -> Dict[str, Any]:
    """
    얼굴을 3영역(이마/볼/턱)으로 나누어 분석.
    이마(메이크업 적은 곳)에 높은 가중치 부여.
    """
    h, w, _ = img_array.shape
    
    zones = {
        "forehead": img_array[0:int(h * 0.3), int(w * 0.25):int(w * 0.75)],     # 상단 30% 중앙
        "cheeks": img_array[int(h * 0.3):int(h * 0.65), :],                       # 중간 35%
        "chin": img_array[int(h * 0.65):, int(w * 0.25):int(w * 0.75)],           # 하단 35% 중앙
    }
    
    zone_results = {}
    zone_weights = {"forehead": 0.45, "cheeks": 0.35, "chin": 0.20}  # 이마 가중치 높음
    
    weighted_L = 0.0
    weighted_a = 0.0
    weighted_b = 0.0
    total_weight = 0.0
    
    for zone_name, zone_img in zones.items():
        skin = _detect_skin_pixels(zone_img)
        if len(skin) < 20:  # 피부 픽셀이 너무 적으면 스킵
            continue
        
        L, a, b = rgb_array_to_lab(skin)
        avg_rgb = np.median(skin, axis=0).astype(int)
        
        w_val = zone_weights.get(zone_name, 0.33)
        weighted_L += L * w_val
        weighted_a += a * w_val
        weighted_b += b * w_val
        total_weight += w_val
        
        zone_results[zone_name] = {
            "L": round(L, 1),
            "a": round(a, 1),
            "b": round(b, 1),
            "avg_rgb": [int(avg_rgb[0]), int(avg_rgb[1]), int(avg_rgb[2])],
            "pixel_count": len(skin),
        }
    
    if total_weight > 0:
        weighted_L /= total_weight
        weighted_a /= total_weight
        weighted_b /= total_weight
    
    return {
        "zones": zone_results,
        "weighted_lab": {
            "L": round(weighted_L, 1),
            "a": round(weighted_a, 1),
            "b": round(weighted_b, 1),
        },
    }


# ═══════════════════════════════════════════════════════
# 5. 언더톤 사전 추정 (Lab 기반 규칙)
# ═══════════════════════════════════════════════════════

def _estimate_undertone(a: float, b: float) -> str:
    """
    CIELab a*, b* 기반 언더톤 추정.
    a* (redness): 높을수록 따뜻한(웜) 경향
    b* (yellowness): 높을수록 황색(웜) 경향
    
    웜톤: a* > 10 또는 b* > 18
    쿨톤: a* < 8 그리고 b* < 15
    """
    warmth_score = (a * 0.6) + (b * 0.4)
    
    if warmth_score > 12:
        return "웜톤"
    elif warmth_score < 8:
        return "쿨톤"
    else:
        return "뉴트럴"


def _estimate_season_hint(L: float, a: float, b: float, ita: float) -> Dict[str, Any]:
    """
    Lab 수치 기반 12서브타입 사전 추정 (GPT에 힌트로 전달).
    최종 결정은 GPT-4o가 이미지+수치 종합 판단.
    """
    undertone = _estimate_undertone(a, b)
    skin_brightness = ita_to_skin_category(ita)
    
    # 대분류 추정
    if undertone == "웜톤":
        if ita > 41:  # 밝은 피부
            season_hint = "봄웜 계열 (라이트/브라이트)"
            candidates = ["봄 라이트웜", "봄 브라이트웜", "봄 트루웜"]
        else:  # 중간~어두운 피부
            season_hint = "가을웜 계열 (뮤트/딥)"
            candidates = ["가을 뮤트웜", "가을 트루웜", "가을 딥웜"]
    elif undertone == "쿨톤":
        if ita > 41:  # 밝은 피부
            season_hint = "여름쿨 계열 (라이트/뮤트)"
            candidates = ["여름 라이트쿨", "여름 트루쿨", "여름 뮤트쿨"]
        else:  # 중간~어두운 피부
            season_hint = "겨울쿨 계열 (브라이트/딥)"
            candidates = ["겨울 브라이트쿨", "겨울 트루쿨", "겨울 딥쿨"]
    else:  # 뉴트럴
        if ita > 41:
            season_hint = "봄/여름 경계 (뉴트럴)"
            candidates = ["봄 라이트웜", "여름 라이트쿨"]
        else:
            season_hint = "가을/겨울 경계 (뉴트럴)"
            candidates = ["가을 뮤트웜", "겨울 트루쿨"]
    
    # 채도(Chroma) 기반 세분화
    chroma = math.sqrt(a ** 2 + b ** 2)
    clarity = "높은 채도 (선명한 컬러)" if chroma > 18 else "낮은 채도 (뮤트한 컬러)"
    
    return {
        "undertone": undertone,
        "skin_brightness": skin_brightness,
        "season_hint": season_hint,
        "candidates": candidates,
        "chroma": round(chroma, 1),
        "clarity": clarity,
    }


# ═══════════════════════════════════════════════════════
# 6. 메인 분석 함수
# ═══════════════════════════════════════════════════════

def analyze_skin_tone(image_bytes: bytes) -> Dict[str, Any]:
    """
    셀카 이미지 바이트 → 피부톤 종합 분석 결과.
    
    Returns:
        {
            "lab": {"L": 72.1, "a": 8.3, "b": 16.5},
            "ita": 51.2,
            "ita_category": "밝은",
            "undertone": "쿨톤",
            "season_hint": "여름쿨 계열",
            "candidates": ["여름 라이트쿨", ...],
            "chroma": 18.5,
            "clarity": "높은 채도",
            "zones": {...},
            "skin_pixel_count": 12345,
            "confidence": "high"
        }
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # 이미지가 너무 크면 리사이즈 (분석 속도 + 메모리)
        max_dim = 640
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.LANCZOS)
        
        # 얼굴 영역 크롭
        face_img = _crop_face_region(img)
        face_array = np.array(face_img)
        
        # 전체 피부 픽셀 감지
        all_skin = _detect_skin_pixels(face_array)
        
        if len(all_skin) < 50:
            return {
                "ok": False,
                "error": "피부 영역을 충분히 감지하지 못했습니다. 밝은 조명에서 정면 셀카를 촬영해주세요.",
                "skin_pixel_count": len(all_skin),
            }
        
        # 전체 평균 Lab
        L, a, b = rgb_array_to_lab(all_skin)
        
        # 영역별 분석 (이마/볼/턱 가중)
        zone_analysis = _analyze_face_zones(face_array)
        
        # 가중 평균 Lab 사용 (영역별 가중 > 전체 평균)
        wl = zone_analysis["weighted_lab"]
        final_L = wl["L"] if wl["L"] > 0 else L
        final_a = wl["a"] if wl["L"] > 0 else a
        final_b = wl["b"] if wl["L"] > 0 else b
        
        # ITA
        ita = calculate_ita(final_L, final_b)
        ita_cat = ita_to_skin_category(ita)
        
        # 시즌 추정
        season = _estimate_season_hint(final_L, final_a, final_b, ita)
        
        # 신뢰도 (피부 픽셀 수 기반)
        confidence = "high" if len(all_skin) > 3000 else ("medium" if len(all_skin) > 500 else "low")
        
        return {
            "ok": True,
            "lab": {"L": round(final_L, 1), "a": round(final_a, 1), "b": round(final_b, 1)},
            "ita": round(ita, 1),
            "ita_category": ita_cat,
            "undertone": season["undertone"],
            "skin_brightness": season["skin_brightness"],
            "season_hint": season["season_hint"],
            "candidates": season["candidates"],
            "chroma": season["chroma"],
            "clarity": season["clarity"],
            "zones": zone_analysis["zones"],
            "skin_pixel_count": len(all_skin),
            "confidence": confidence,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════
# 7. GPT 프롬프트 생성 (수치 데이터 포함)
# ═══════════════════════════════════════════════════════

def build_enhanced_prompt(skin_data: Dict[str, Any]) -> str:
    """
    피부톤 분석 결과를 포함한 강화 프롬프트 생성.
    GPT-4o에 이미지와 함께 전달하면 정확도가 크게 향상됨.
    """
    if not skin_data.get("ok"):
        # 분석 실패 시 기본 프롬프트
        return _BASE_PROMPT
    
    lab = skin_data["lab"]
    
    metrics_section = f"""
[피부톤 객관적 측정 데이터 — 이 수치를 반드시 참고하세요]
- CIELab: L*={lab['L']}, a*={lab['a']}, b*={lab['b']}
- ITA(Individual Typology Angle): {skin_data['ita']}° → 피부 밝기: {skin_data['ita_category']}
- Chroma(채도): {skin_data['chroma']} → {skin_data['clarity']}
- 사전 언더톤 추정: {skin_data['undertone']}
- 사전 시즌 추정: {skin_data['season_hint']}
- 후보 서브타입: {', '.join(skin_data['candidates'])}
- 분석 신뢰도: {skin_data['confidence']} (피부 픽셀 {skin_data['skin_pixel_count']}개)

[중요 지침]
- 위 CIELab 수치는 이미지에서 피부 영역만 추출하여 계산한 객관적 값입니다.
- a* 값이 높을수록(>10) 웜톤, 낮을수록(<8) 쿨톤 경향입니다.
- b* 값이 높을수록(>18) 황색(웜), 낮을수록(<15) 청색(쿨) 경향입니다.
- ITA가 높을수록(>41°) 밝은 피부, 낮을수록(<28°) 어두운 피부입니다.
- 사전 추정과 이미지를 종합하여 최종 12서브타입을 결정하세요.
- 사전 추정이 맞지 않다고 판단되면 이미지 기반으로 수정해도 됩니다.
"""
    
    return _BASE_PROMPT_12TYPE + metrics_section


# 기본 프롬프트 (Phase 1 호환)
_BASE_PROMPT = """당신은 전문 퍼스널컬러 컨설턴트입니다.
이 사람의 사진을 보고 퍼스널컬러를 분석하세요.
아래 JSON 형식으로만 응답하세요. JSON 외 다른 텍스트는 절대 포함하지 마세요.

{
  "season": "봄웜 | 여름쿨 | 가을웜 | 겨울쿨 중 하나",
  "season_en": "Spring Warm | Summer Cool | Autumn Warm | Winter Cool 중 하나",
  "undertone": "웜톤 | 쿨톤 중 하나",
  "skin_tone": "밝은 | 중간 | 어두운 중 하나",
  "best_colors": ["#HEX1", "#HEX2", "#HEX3", "#HEX4", "#HEX5"],
  "best_color_names": ["색상명1(한국어)", "색상명2", "색상명3", "색상명4", "색상명5"],
  "avoid_colors": ["#HEX1", "#HEX2", "#HEX3"],
  "avoid_color_names": ["피할색1(한국어)", "피할색2", "피할색3"],
  "summary": "퍼스널컬러 한줄 요약",
  "style_tip": "이 계절 타입에게 어울리는 패션 스타일 팁 1~2문장 (한국어)"
}"""


# 12서브타입 강화 프롬프트
_BASE_PROMPT_12TYPE = """당신은 10년 경력의 전문 퍼스널컬러 컨설턴트입니다.
이 사람의 사진과 함께 제공된 피부톤 측정 데이터를 종합 분석하여 퍼스널컬러를 진단하세요.

12서브타입 중 하나를 선택하세요:
- 봄 라이트웜, 봄 트루웜, 봄 브라이트웜
- 여름 라이트쿨, 여름 트루쿨, 여름 뮤트쿨
- 가을 뮤트웜, 가을 트루웜, 가을 딥웜
- 겨울 브라이트쿨, 겨울 트루쿨, 겨울 딥쿨

아래 JSON 형식으로만 응답하세요. JSON 외 다른 텍스트는 절대 포함하지 마세요.

{
  "season": "위 12서브타입 중 하나 (한국어)",
  "season_en": "영어 버전 (예: Summer Light Cool)",
  "season_group": "봄웜 | 여름쿨 | 가을웜 | 겨울쿨 중 대분류",
  "undertone": "웜톤 | 쿨톤 | 뉴트럴 중 하나",
  "skin_tone": "밝은 | 중간 | 어두운 중 하나",
  "best_colors": ["#HEX1", "#HEX2", "#HEX3", "#HEX4", "#HEX5"],
  "best_color_names": ["색상명1(한국어)", "색상명2", "색상명3", "색상명4", "색상명5"],
  "avoid_colors": ["#HEX1", "#HEX2", "#HEX3"],
  "avoid_color_names": ["피할색1(한국어)", "피할색2", "피할색3"],
  "summary": "퍼스널컬러 한줄 요약 (예: 여름 라이트쿨 - 투명하고 밝은 파스텔 컬러가 잘 어울려요)",
  "style_tip": "이 서브타입에게 어울리는 패션 스타일 팁 2~3문장 (한국어)",
  "style_tip_en": "Style tip in English",
  "makeup_tip": "이 서브타입에 맞는 메이크업 팁 2문장 (한국어)",
  "confidence": 분석 신뢰도 0~100 정수,
  "analysis_note": "CIELab 수치와 시각적 판단의 근거를 2문장으로 설명"
}

분석 기준:
- 제공된 CIELab L*a*b* 수치와 ITA를 최우선 참고
- 피부 언더톤(웜/쿨), 피부 밝기, 머리카락·눈동자 색상 종합 판단
- 사진 조명 편향이 의심되면 CIELab 수치를 더 신뢰
- 반드시 유효한 JSON만 반환"""
