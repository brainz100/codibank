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
import json
import os
import platform
import re
import sys
import time
from typing import Any, Dict, Tuple

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

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

app = Flask(__name__)
CORS(app)

# 얼굴/아이템 사진(DataURL)까지 포함되면 요청 바디가 커질 수 있습니다.
# - 모바일 원본 사진은 base64로 변환되면 1.3배 이상 커지기도 해서,
#   데모 안정성을 위해 넉넉히 허용합니다.
# - 프론트에서도 리사이즈/압축을 하지만(속도/요금/안정성), 서버도 여유를 둡니다.
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # 60MB

# ==============================
# Upload storage (매우 중요)
# ==============================
#
# 반복적으로 발생했던 문제:
# - zip을 새로 받아서 폴더를 교체하거나(또는 폴더명을 바꾸거나) server 폴더를 덮어쓰면
#   server/uploads 안에 저장된 이미지가 같이 사라져 코디앨범/옷장/추천 코디 이미지가
#   "잠깐 보였다가 사라지는" 것처럼 보이는 현상이 생깁니다.
#
# 해결:
# - 업로드/생성된 이미지 저장 위치를 "코드 폴더"와 분리하여,
#   버전업/폴더 변경에도 유지되는 데이터 폴더(기본: ~/.codibank/uploads)에 저장합니다.
# - 필요 시 환경변수로 변경 가능:
#   - CODIBANK_DATA_DIR=/absolute/path/to/data   (uploads 하위 폴더 사용)
#   - CODIBANK_UPLOAD_DIR=/absolute/path/to/uploads

_DEFAULT_DATA_DIR = os.path.join(os.path.expanduser("~"), ".codibank")
_DATA_DIR = (os.getenv("CODIBANK_DATA_DIR") or "").strip() or _DEFAULT_DATA_DIR
_DATA_DIR = os.path.abspath(os.path.expanduser(_DATA_DIR))

_UPLOAD_DIR = (os.getenv("CODIBANK_UPLOAD_DIR") or "").strip() or os.path.join(_DATA_DIR, "uploads")
_UPLOAD_DIR = os.path.abspath(os.path.expanduser(_UPLOAD_DIR))
os.makedirs(_UPLOAD_DIR, exist_ok=True)

# (레거시 호환) 예전 버전은 server/uploads에 저장했습니다.
# 새 저장소로 옮기지 않아도 기존 앨범/아이템이 깨지지 않도록
# /uploads/<file> 서빙 시 레거시 폴더도 폴백으로 확인합니다.
_LEGACY_UPLOAD_DIR = os.path.join(_HERE, "uploads")
try:
    os.makedirs(_LEGACY_UPLOAD_DIR, exist_ok=True)
except Exception:
    pass

# 브라우저에서 저장된 경로를 그대로 쓰기 위해 고정 prefix 사용
_UPLOAD_PREFIX = "/uploads/"


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_upload_bytes(slot: str, ext: str, data: bytes, *, fixed_name: str | None = None) -> str:
    """uploads 폴더에 바이너리를 저장하고 상대 경로(/uploads/..)를 반환"""

    slot = re.sub(r"[^a-z0-9_-]+", "", str(slot or "img").lower())[:16] or "img"
    ext = re.sub(r"[^a-z0-9]+", "", str(ext or "jpg").lower()) or "jpg"

    if fixed_name:
        fname = fixed_name
    else:
        fname = f"{slot}_{_now_ms()}_{os.urandom(3).hex()}.{ext}"

    fpath = os.path.join(_UPLOAD_DIR, fname)
    # ✅ 원자적(atomic) 저장
    # - 모바일에서 저장 직후 /uploads/... 를 바로 요청하는 경우가 많아,
    #   부분적으로 쓰인 파일을 읽는 레이스를 피합니다.
    tmp = fpath + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
        try:
            f.flush()
            os.fsync(f.fileno())
        except Exception:
            pass
    os.replace(tmp, fpath)
    return f"{_UPLOAD_PREFIX}{fname}"


def _make_ai_cache_key(payload: Dict[str, Any], face_bytes: bytes | None) -> str:
    """요청 입력을 기반으로 안정적인 캐시 키를 생성합니다.

    - OpenAI 호출이 실패하거나 느릴 때, 이전에 생성해 둔 이미지를 즉시 반환하기 위함
    - seed가 포함되어야 '다시 코디'가 다른 결과로 저장됩니다.
    """

    user = payload.get("user") or {}
    weather = payload.get("weather") or {}

    body = {
        "purposeKey": payload.get("purposeKey") or "",
        "purposeLabel": payload.get("purposeLabel") or "",
        "seed": payload.get("seed") or 0,
        "forDateKey": payload.get("forDateKey") or payload.get("dateKey") or "",
        "size": payload.get("size") or "",
        "quality": payload.get("quality") or "",
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
        "styleTitle": payload.get("styleTitle") or "",
        "keywords": payload.get("keywords") or [],
        "stylist": payload.get("stylist") or {},
        "matchPairs": payload.get("matchPairs") or [],
    }

    if face_bytes:
        # 얼굴 바이너리 전체를 저장하지 않고, 해시만 포함
        body["faceHash"] = _sha256_hex(face_bytes)[:16]

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


def _safe_float(x: Any) -> float | None:
    try:
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        s = str(x).strip()
        if not s:
            return None
        return float(s)
    except Exception:
        return None


def _body_shape_desc(user: Dict[str, Any]) -> str:
    """키/몸무게 숫자만 넣으면 모델이 체형 차이를 약하게 반영하는 경우가 있어,
    BMI 기반의 간단한 '체형 설명'을 함께 제공합니다."""

    h = _safe_float(user.get("height"))
    w = _safe_float(user.get("weight"))
    gender = (user.get("gender") or "").upper()
    if not h or not w:
        return ""
    if h <= 0:
        return ""
    m = h / 100.0
    if m <= 0:
        return ""
    bmi = w / (m * m)

    # (참고) 아시아권 BMI 기준은 더 보수적이지만, 여기서는 이미지 체형 가이드를 위해 단순화합니다.
    if bmi < 18.5:
        build = "slim"
    elif bmi < 23:
        build = "average"
    elif bmi < 27:
        build = "athletic"
    elif bmi < 32:
        build = "stocky"
    else:
        build = "plus-size"

    extra = []
    if gender == "M":
        extra.append("masculine proportions")
    elif gender == "F":
        extra.append("feminine proportions")

    return f"body build: {build} (BMI≈{bmi:.1f}); proportions must reflect {int(h)}cm & {int(w)}kg" + (
        f"; {', '.join(extra)}" if extra else ""
    )


def _culture_hint(location: str) -> str:
    s = (location or "").strip().lower()
    if not s:
        return "Keep the styling culturally appropriate for the user's location."
    # KR
    if any(k in s for k in ["seoul", "korea", "kr", "busan", "incheon", "daejeon", "daegu", "gwangju"]):
        return "Base the look on contemporary Korean city fashion sensibilities: clean silhouette, neat layering, subtle trend accents."
    # JP
    if any(k in s for k in ["tokyo", "osaka", "japan", "jp"]):
        return "Base the look on Japanese urban sensibilities: minimal, tidy layering, restrained palette."
    # FR
    if any(k in s for k in ["paris", "france", "fr"]):
        return "Base the look on Parisian/French chic: understated elegance with one subtle statement."
    # US
    if any(k in s for k in ["new york", "los angeles", "usa", "united states", "us"]):
        return "Base the look on US urban casual: relaxed, practical, wearable." 
    return f"Keep the styling culturally appropriate for: {location}."


def _stylist_hint(stylist: Any) -> str:
    """프론트에서 생성한 스타일리스트 페르소나를 프롬프트에 반영."""

    if not stylist:
        return ""
    if isinstance(stylist, dict):
        sid = stylist.get("id")
        tag = (stylist.get("tag") or "").lower().strip()
        sub_tag = (stylist.get("subTag") or "").lower().strip()
        voice = (stylist.get("voice") or "").strip()
        desc = (stylist.get("desc") or "").strip()

        # 세분화된 21개 스타일리스트 → 영문 스타일 지시어 매핑
        sub_tag_map = {
            # 미니멀 계열
            "scandi":       "Scandinavian minimal: white/gray/beige palette, clean silhouette, texture over color",
            "monochrome":   "Monochrome edge: single-color tonal dressing, black or off-white, fit-focused",
            "genderless":   "Genderless basic: oversized neutral basics, texture contrast without color blocks",
            # 스트릿 계열
            "k-layered":    "K-street layered: hoodie under jacket, wide pants, statement shoes",
            "utility":      "Workwear utility: cargo details, earth tones, functional pockets, durable fabrics",
            "y2k":          "Y2K casual: crop silhouettes, one colorful accent piece, low-rise proportions",
            # 시크/포멀 계열
            "french":       "French chic: understated base with one elegant accent, effortless refinement",
            "italian":      "Italian luxe: tailored fit, rich textures, neutral plus deep wine or olive accent",
            "modern-biz":   "Modern business: slim-fit suiting, white shirt base, no tie, polished and clean",
            # 스포티 계열
            "premium-ath":  "Premium athleisure: logo-free technical fabrics, neutral sporty palette, bold jacket",
            "outdoor":      "Outdoor adventure: functional outerwear, layered base, boots or trail shoes",
            "tech":         "Techwear: water-resistant lightweight fabrics, zip layers, dark palette with one neon accent",
            # 데이트/소셜 계열
            "romantic":     "Romantic daily: one floral or pastel accent, feminine silhouette, soft fabrics",
            "clean":        "Clean casual: solid tee and slacks, color pairing as the only statement",
            "semi-formal":  "Smart semi-formal: blazer with casual pants, sneakers as accent, office-to-outing",
            # 계절 특화
            "layered-cool": "Layered cool-weather: coat plus knit plus inner 3-layer, earth tones, long boots",
            "summer":       "Summer resort: linen or cotton, bright palette, sandals or espadrilles",
            "transition":   "Transition season: trench coat or cardigan as key piece, light layering",
            # 문화권 특화
            "tokyo":        "Tokyo minimal street: tidy wide silhouette, white/black/khaki palette",
            "nyc":          "NYC power casual: oversized outer, slim inner, bold black-white contrast",
            "seoul":        "Seoul trendsetter: K-fashion mix-match, layered accent, unique shoes as focal point",
        }

        # subTag가 있으면 세부 지시어 사용, 없으면 일반 tag 매핑
        if sub_tag and sub_tag in sub_tag_map:
            style_directive = sub_tag_map[sub_tag]
        else:
            tag_map = {
                "minimal":     "minimal classic: neutral palette, clean silhouette",
                "street":      "K-street casual: layered, trendy, statement pieces",
                "chic":        "French chic: simple base with one elegant accent",
                "athleisure":  "sporty athleisure: functional, active-ready",
                "business":    "smart business: tonal, well-fitted, polished",
                "workwear":    "workwear mood: sturdy fabrics, outerwear-focused",
                "smartcasual": "smart casual: balanced, versatile office-to-outing",
            }
            style_directive = tag_map.get(tag, tag)

        bits = []
        if sid is not None:
            bits.append(f"stylist #{sid}")
        if voice:
            bits.append(voice)
        if style_directive:
            bits.append(style_directive)
        if desc and desc != style_directive:
            bits.append(desc)
        if not bits:
            return ""
        return "Stylist persona: " + "; ".join(bits) + "."
    return ""


def _matchpairs_hint(match_pairs: Any) -> str:
    """프론트에서 뽑아낸 카테고리-컬러 키워드를 프롬프트에 반영(색감 일관성 강화)."""

    if not match_pairs or not isinstance(match_pairs, list):
        return ""
    color_map = {
        "블랙": "black",
        "화이트": "white",
        "그레이": "gray",
        "라이트그레이": "light gray",
        "네이비": "navy",
        "블루": "blue",
        "스카이블루": "sky blue",
        "그린": "green",
        "베이지": "beige",
        "브라운": "brown",
        "레드": "red",
        "핑크": "pink",
        "퍼플": "purple",
        "옐로": "yellow",
        "오렌지": "orange",
    }
    cat_map = {
        "coat": "coat",
        "jacket": "jacket",
        "top": "top",
        "pants": "bottoms",
        "shoes": "shoes",
        "scarf": "scarf",
    }
    parts = []
    for p in match_pairs:
        if not isinstance(p, dict):
            continue
        k = str(p.get("key") or "").strip()
        c = str(p.get("color") or "").strip()
        if not k or not c:
            continue
        c_en = color_map.get(c, c)
        k_en = cat_map.get(k, k)
        parts.append(f"{k_en}: {c_en}")
    if not parts:
        return ""
    return "Outfit color targets: " + ", ".join(parts) + "."


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


def _gender_en(g: str) -> str:
    g = (g or "").upper().strip()
    if g == "M":
        return "male"
    if g == "F":
        return "female"
    return "person"


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
    # 프론트 키: commute/meet/exercise/weekendTrip/overseasTrip/presentation/date/other
    if k == "commute":
        return (
            "smart casual commute",
            "clean minimal smart-casual outfit suitable for commuting",
        )
    if k == "meet":
        return (
            "social meetup",
            "polished casual outfit for meeting friends",
        )
    if k == "exercise":
        return (
            "athleisure workout",
            "functional athleisure outfit for exercise",
        )
    if k == "weekendTrip":
        return (
            "weekend trip",
            "comfortable layered travel outfit for a weekend trip",
        )
    if k == "overseasTrip":
        return (
            "overseas travel",
            "versatile travel outfit with practical layering for overseas trip",
        )
    if k == "presentation":
        return (
            "presentation",
            "sharp professional outfit suitable for giving a presentation",
        )
    if k == "date":
        return (
            "date",
            "stylish casual outfit for a date",
        )
    # fallback
    pl = (purpose_label or "").strip() or "everyday"
    return (pl, "well-balanced everyday outfit")


def build_prompt(payload: Dict[str, Any]) -> Tuple[str, str]:
    """(prompt, short_explanation)"""
    user = payload.get("user") or {}
    weather = payload.get("weather") or {}

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

    # ✅ 체형(키/몸무게) + 문화권 + 스타일리스트 + (카테고리-컬러) 타겟
    body_rule = _body_shape_desc(user)
    location = str(weather.get("location", "")).strip()
    culture_rule = _culture_hint(location) if location else ""
    stylist_rule = _stylist_hint(payload.get("stylist"))
    match_rule = _matchpairs_hint(payload.get("matchPairs"))

    kw_str = ", ".join([str(k) for k in keywords if str(k).strip()][:6])

    # 온도 버킷에 따른 레이어링 가이드
    if bucket in ("very cold", "cool"):
        weather_rule = "Layer appropriately for cold weather (coat/jacket, warm inner, scarf optional)."
    elif bucket == "hot":
        weather_rule = "Choose breathable lightweight fabrics suitable for hot weather."
    else:
        weather_rule = "Use balanced layering suitable for mild weather."

    # ══════════════════════════════════════════════════════
    # ⛔ 절대 금지 규칙 (HARD RULES - 반드시 지켜야 함)
    # ══════════════════════════════════════════════════════
    hard_rules = (
        "ABSOLUTE OUTFIT RULES — NEVER VIOLATE: "
        "(1) EXACTLY ONE outer layer: either one coat OR one jacket, NEVER both, NEVER two jackets, NEVER two coats. "
        "(2) EXACTLY ONE scarf OR muffler OR necktie total — never two or more neckwear items simultaneously. "
        "(3) EXACTLY ONE bag OR backpack OR tote — never two bags at once. "
        "(4) EXACTLY ONE hat OR cap — never two headwear items. "
        "(5) EXACTLY ONE pair of shoes — never two pairs visible. "
        "(6) Each clothing category appears EXACTLY ONCE in the outfit. "
        "(7) The complete outfit must be a single coherent look — no mismatched duplicate layers. "
        "Violating any of these rules is strictly forbidden."
    )

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
        "Photorealistic full-body fashion lookbook photo. "
        f"A {profile_str} wearing a {purpose_desc}. "
        + (f"Body guidance: {body_rule}. " if body_rule else "")
        + (f"Location: {location}. " if location else "")
        + (f"{culture_rule} " if culture_rule else "")
        + (f"{stylist_rule} " if stylist_rule else "")
        + (f"{match_rule} " if match_rule else "")
        + f"Weather: {bucket}. Condition: {cond or 'clear'}. "
        + f"Style theme: {purpose_tag}. "
        + f"Keywords: {kw_str}. "
        + f"{weather_rule} "
        + f"{hard_rules} "
        + "Clean studio background, soft natural lighting, sharp focus. "
        + "No text, no watermark, no logo, no brand marks. "
        + "High quality outfit details, realistic body shape and proportions."
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


@app.get("/health")
def health():
    # uploads 폴더 점검(파일 개수)
    try:
        upload_count = len([n for n in os.listdir(_UPLOAD_DIR) if not str(n).endswith('.tmp')])
    except Exception:
        upload_count = None
    return jsonify(
        ok=True,
        ts=_now_ms(),
        python=sys.version.split(" ")[0],
        platform=platform.platform(),
        openai_sdk=_sdk_version(),
        has_openai_key=_safe_bool(os.getenv("OPENAI_API_KEY")),
        upload_dir=_UPLOAD_DIR,
        legacy_upload_dir=_LEGACY_UPLOAD_DIR,
        upload_count=upload_count,
        models={
            "no_face": os.getenv("CODIBANK_OPENAI_IMAGE_MODEL", "gpt-image-1.5"),
            "with_face": os.getenv("CODIBANK_OPENAI_IMAGE_MODEL_FACE", "gpt-image-1.5"),
        },
    )


@app.get("/uploads/<path:filename>")
def serve_upload(filename: str):
    """업로드된 이미지를 서빙합니다.

    - 프로토타입/로컬 테스트용
    - 모바일(같은 Wi-Fi)에서 이미지 URL로 접근 가능
    - ✅ [버그1·2 수정] CORS + Cache-Control 헤더 추가
      · crossOrigin=anonymous 설정된 canvas가 taint 없이 이미지를 그릴 수 있도록 CORS 허용
      · immutable 캐싱으로 재접근 시 빠른 로딩 보장
    """
    from flask import after_this_request
    @after_this_request
    def add_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        response.headers["Cache-Control"] = "public, max-age=86400, immutable"
        return response
    # 1) 신규 저장소(~/.codibank/uploads 등)
    try:
        f0 = os.path.join(_UPLOAD_DIR, filename)
        if os.path.isfile(f0):
            return send_from_directory(_UPLOAD_DIR, filename)
    except Exception:
        pass

    # 2) 레거시 저장소(server/uploads)
    try:
        f1 = os.path.join(_LEGACY_UPLOAD_DIR, filename)
        if os.path.isfile(f1):
            return send_from_directory(_LEGACY_UPLOAD_DIR, filename)
    except Exception:
        pass

    # 3) not found
    return (jsonify(ok=False, error="file not found"), 404)


@app.post("/api/storage/upload")
def storage_upload():
    """브라우저에서 촬영/선택한 이미지를 서버에 저장합니다.

    ✅ 권장 입력(multipart/form-data):
      - file: (binary)
      - slot: front|back|brand|img (옵션)

    호환 입력(JSON):
      { dataUrl: "data:image/...;base64,...", slot?: "front|back|brand", email?: "..." }

    출력:
      { ok:true, path:"/uploads/xxx.jpg", url:"http://host:8787/uploads/xxx.jpg" }

    왜 필요한가?
    - 일부 모바일 브라우저에서 로컬(IndexedDB/Blob URL) 이미지가
      매우 짧게 보였다가 사라지는 현상이 있어, 데모 안정성을 위해
      서버 파일로 저장해 참조하도록 합니다.
    - base64(DataURL)는 커질 수 있으므로, multipart 업로드를 우선 지원합니다.
    """

    # 1) multipart/form-data 우선 처리 (용량/안정성 ↑)
    try:
        if request.files and "file" in request.files:
            f = request.files["file"]
            data = b""
            try:
                data = f.read() or b""
            except Exception:
                data = b""

            if not data:
                return jsonify(ok=False, error="업로드된 파일이 비어있습니다."), 400

            slot = str(request.form.get("slot") or request.args.get("slot") or "img")

            filename = str(getattr(f, "filename", "") or "")
            mime = str(getattr(f, "mimetype", "") or "")
            ext = "jpg"

            # ✅ 확장자 결정(안정성)
            # - 일부 클라이언트가 filename을 .jpg로 고정하거나, mime과 확장자가 불일치할 수 있습니다.
            # - 가능하면 mimetype을 우선하고, 없으면 filename을 사용합니다.
            m = (mime or "").lower()
            ext_by_mime = ""
            if "png" in m:
                ext_by_mime = "png"
            elif "webp" in m:
                ext_by_mime = "webp"
            elif "jpeg" in m or "jpg" in m:
                ext_by_mime = "jpg"
            elif "heic" in m or "heif" in m:
                ext_by_mime = "jpg"

            ext_by_name = ""
            if "." in filename:
                ext_by_name = filename.rsplit(".", 1)[1].lower()

            ext = ext_by_mime or ext_by_name or "jpg"

            try:
                rel = _write_upload_bytes(slot=slot, ext=ext, data=data)
                try:
                    print(f"[storage_upload] slot={slot} bytes={len(data)} ext={ext} -> {rel}", flush=True)
                except Exception:
                    pass
            except Exception as e:
                return jsonify(ok=False, error=f"서버 저장 실패: {e}"), 500

            base = request.host_url.rstrip("/")
            return jsonify(ok=True, path=rel, url=f"{base}{rel}")
    except Exception:
        # multipart 파싱 실패 시 JSON 경로로 계속 진행
        pass

    # 2) JSON dataUrl (레거시/호환)
    payload = request.get_json(silent=True) or {}
    data_url = str(payload.get("dataUrl") or "").strip()
    if not data_url:
        return jsonify(ok=False, error="dataUrl 또는 multipart file이 필요합니다."), 400

    try:
        mime, img_bytes = _data_url_to_bytes(data_url)
    except Exception:
        return jsonify(ok=False, error="이미지 형식이 올바르지 않습니다(dataUrl)."), 400

    # 확장자 결정
    ext = "jpg"
    m = (mime or "").lower()
    if "png" in m:
        ext = "png"
    elif "webp" in m:
        ext = "webp"
    elif "jpeg" in m or "jpg" in m:
        ext = "jpg"

    # 파일명(슬롯/시간/난수)
    slot = str(payload.get("slot") or "img")
    try:
        rel = _write_upload_bytes(slot=slot, ext=ext, data=img_bytes)
    except Exception as e:
        return jsonify(ok=False, error=f"서버 저장 실패: {e}"), 500

    base = request.host_url.rstrip("/")
    return jsonify(ok=True, path=rel, url=f"{base}{rel}")


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


@app.post("/api/ai/styling")
def ai_styling():
    # API Key 체크
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify(
            ok=False,
            error="OPENAI_API_KEY가 설정되지 않았습니다. 서버 환경변수에 API Key를 설정해주세요.",
        ), 400

    payload = request.get_json(silent=True) or {}

    prompt, short = build_prompt(payload)

    face_data_url = payload.get("faceImage")
    size = str(payload.get("size") or "1024x1536")
    quality = str(payload.get("quality") or "low")

    # 출력 포맷(모바일 로딩 최적화)
    output_format = str(payload.get("output_format") or "jpeg")
    output_compression = int(payload.get("output_compression") or 80)

    # --- 서버 캐시(파일) ---
    # - 같은 조건(날씨/목적/프로필/seed/얼굴)로 재요청하면
    #   OpenAI 호출 없이 바로 이미지 파일을 반환합니다.
    face_bytes_for_key: bytes | None = None
    if face_data_url:
        try:
            _mime0, face_bytes_for_key = _data_url_to_bytes(str(face_data_url))
        except Exception:
            face_bytes_for_key = None

    cache_key = _make_ai_cache_key(payload, face_bytes_for_key)
    ext = "jpg" if output_format.lower() in ("jpeg", "jpg") else output_format.lower()
    cache_fname = f"ai_{cache_key}.{ext}"
    cache_fpath = os.path.join(_UPLOAD_DIR, cache_fname)
    legacy_cache_fpath = os.path.join(_LEGACY_UPLOAD_DIR, cache_fname)
    if os.path.exists(cache_fpath) or os.path.exists(legacy_cache_fpath):
        rel = f"{_UPLOAD_PREFIX}{cache_fname}"
        base = request.host_url.rstrip("/")
        return jsonify(
            ok=True,
            image=f"{base}{rel}",  # 프론트 호환: img src로 바로 사용
            path=rel,
            url=f"{base}{rel}",
            explanation=short,
            model="cache",
            cached=True,
        )

    # 모델 선택
    # - 기본은 gpt-image-1.5
    # - 계정/조직에 따라 특정 모델 접근이 막혀있을 수 있어 후보군을 두고 순차 시도합니다.
    model_no_face = os.getenv("CODIBANK_OPENAI_IMAGE_MODEL", "gpt-image-1.5")
    model_with_face = os.getenv("CODIBANK_OPENAI_IMAGE_MODEL_FACE", "gpt-image-1.5")

    client = get_client()

    try:
        model_used = ""

        if face_data_url:
            mime, img_bytes = _data_url_to_bytes(str(face_data_url))
            face_ext = "jpg" if (mime.endswith("jpeg") or mime.endswith("jpg")) else "png"

            # 이미지 편집(참조 이미지 기반)
            # - 주의: file-like 객체는 1회 읽으면 포인터가 끝으로 가므로,
            #         재시도/모델 폴백 시 반드시 새 BytesIO를 생성해야 합니다.
            last_err: Exception | None = None
            for m in _candidate_image_models(model_with_face):
                try:
                    bio = io.BytesIO(img_bytes)
                    bio.name = f"face.{face_ext}"
                    resp = _images_edit_compat(
                        client,
                        model=m,
                        image_files=[bio],
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
                    # 접근 불가 모델이면 다음 후보로
                    if _is_model_access_error(str(e)):
                        continue
                    raise
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

        # 파일 저장(코디앨범 안정성)
        rel = _write_upload_bytes("ai", ext, img_bytes, fixed_name=cache_fname)
        base = request.host_url.rstrip("/")

        # 프론트 호환을 위해 image 필드는 path로 제공(가벼움)
        # 필요하면 프론트에서 url을 써도 됩니다.
        return jsonify(
            ok=True,
            image=f"{base}{rel}",
            path=rel,
            url=f"{base}{rel}",
            explanation=short,
            model=model_used,
            cached=False,
            prompt=prompt if os.getenv("CODIBANK_DEBUG_PROMPT") == "1" else None,
        )

    except Exception as e:
        return (
            jsonify(
                ok=False,
                error=str(e),
                openai_sdk=_sdk_version(),
                has_openai_key=_safe_bool(os.getenv("OPENAI_API_KEY")),
            ),
            500,
        )


@app.post("/api/ai/classify-item")
def classify_item():
    """
    Claude Vision API를 이용한 패션 아이템 카테고리/컬러/스타일 분류
    - MobileNet(브라우저)보다 훨씬 정확한 분류 가능
    - 코트/자켓/탑 등 기장 구분, 색상, 브랜드 힌트까지 추출
    """
    import anthropic as _anthropic_sdk

    if not os.getenv("ANTHROPIC_API_KEY"):
        return jsonify(
            ok=False,
            error="ANTHROPIC_API_KEY가 설정되지 않았습니다.",
        ), 400

    try:
        data = request.get_json(force=True) or {}
        image_b64 = data.get("image_b64", "")
        media_type = data.get("media_type", "image/jpeg")
        hint_category = str(data.get("hint_category") or "").strip()

        if not image_b64:
            return jsonify(ok=False, error="image_b64가 없습니다."), 400

        client = _anthropic_sdk.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        category_hint = f"사용자가 선택한 힌트 카테고리: {hint_category}. 이것을 참고하되, 이미지 분석 결과가 더 정확하면 우선합니다." if hint_category else ""

        prompt = f"""당신은 패션 전문가입니다. 이미지를 보고 의류/패션 아이템을 정확하게 분류하세요.

{category_hint}

다음 카테고리 중 하나를 선택하세요:
- coat: 코트 (롱코트, 트렌치코트, 패딩, 다운재킷, 파카 등 허리 아래로 내려오는 아우터)
- jacket: 자켓 (블레이저, 야구점퍼, 청자켓, 가죽자켓, 수트자켓, 바람막이 등 허리선 아우터)
- top: 탑/셔츠/블라우스 (티셔츠, 셔츠, 블라우스, 니트, 후디, 가디건, 조끼 등 상의)
- pants: 바지/스커트 (청바지, 슬랙스, 치마, 레깅스, 반바지 등 하의)
- shoes: 구두/운동화 (운동화, 구두, 부츠, 샌들, 로퍼 등 신발류)
- socks: 양말
- watch: 시계
- scarf: 스카프/목도리/머플러
- etc: 기타 (가방, 모자, 벨트 등)

JSON만 반환하세요 (다른 텍스트 없이):
{{
  "category": "카테고리키",
  "color": "주요 컬러(한국어, 예: 블랙, 네이비, 화이트, 베이지, 그레이, 브라운, 블루, 그린, 레드, 핑크)",
  "sub_color": "보조 컬러(없으면 빈 문자열)",
  "style_tag": "스타일 태그(예: 캐주얼, 포멀, 스포티, 미니멀, 스트릿, 빈티지)",
  "length": "기장(coat/jacket/top만: 롱/미들/숏, 나머지는 빈 문자열)",
  "brand_hint": "브랜드 힌트(보이면 브랜드명, 없으면 빈 문자열)",
  "confidence": "high/medium/low",
  "note": "간단한 아이템 설명(20자 이내, 한국어)"
}}"""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        raw = (response.content[0].text or "").strip()
        # JSON 파싱
        import json as _json
        try:
            # 마크다운 코드블록 제거
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = _json.loads(clean)
        except Exception:
            # 파싱 실패시 기본값
            result = {
                "category": hint_category or "etc",
                "color": "",
                "sub_color": "",
                "style_tag": "",
                "length": "",
                "brand_hint": "",
                "confidence": "low",
                "note": "",
            }

        return jsonify(ok=True, **result)

    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8787"))
    # ✅ 안정성 기본값: debug OFF
    # - debug=True(리로더)일 때는 프로세스가 2개 떠서(port가 2개 LISTEN으로 보임)
    #   사용자가 "포트가 점유"되었다고 오해하기 쉽습니다.
    # - 투자자 데모/외부 공유 목적이면 debug=False가 훨씬 안전합니다.
    debug = str(os.getenv("CODIBANK_DEBUG", "0")).strip().lower() in ("1", "true", "yes", "on")
    # ⚠️ 리로더(use_reloader=True)는 uploads 폴더에 파일이 저장될 때마다
    #    "파일 변경"으로 인식해 서버가 재시작되는 경우가 있어,
    #    이미지가 잠깐 보였다가 깨지는 현상을 유발할 수 있습니다.
    #    데모/테스트 안정성을 위해 리로더는 항상 끕니다.
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False, threaded=True)
