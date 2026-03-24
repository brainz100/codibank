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
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, Tuple
import requests as http_requests

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

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
    with open(fpath, "wb") as f:
        f.write(data)
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
        if not prompt:
            prompt = (
                "Create a photorealistic full-body fashion styling image. "
                f"The subject should look like the user: {gender}, age {age}, {height or ''}cm, {weight or ''}kg. "
                "Use the provided reference images for the outfit: one upper-body garment and one lower-body garment. "
                "Preserve the clothing category, color, silhouette and major design details from the references. "
                "If a face reference is provided, preserve the same facial identity. "
                "Show the whole body from head to toe. "
                f"Weather: {bucket}. Condition: {cond or 'clear'}. Purpose: {purpose_desc}. "
                f"Location culture hint: {str(weather.get('location') or '').strip() or 'Seoul'}. "
                "Natural proportions, realistic try-on, clean fashion editorial background. "
                "No text, no watermark, no logo."
            )
        else:
            prompt = prompt + " Keep the upper and lower garments faithful to the provided reference images, preserve category, color and silhouette. If face reference exists, preserve facial identity. No text, no watermark."
        return prompt, short

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
        "Photorealistic full-body fashion lookbook photo. "
        f"A {profile_str} wearing a {purpose_desc}. "
        f"Weather: {bucket}. Condition: {cond or 'clear'}. "
        f"Style theme: {purpose_tag}. "
        f"Keywords: {kw_str}. "
        f"{weather_rule} "
        "Clean studio background, soft natural lighting, sharp focus. "
        "No text, no watermark, no logo, no brand marks. "
        "High quality outfit details, realistic proportions."
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
    return jsonify(
        ok=True,
        ts=_now_ms(),
        python=sys.version.split(" ")[0],
        platform=platform.platform(),
        openai_sdk=_sdk_version(),
        has_openai_key=_safe_bool(os.getenv("OPENAI_API_KEY")),
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
    f1 = os.path.join(_UPLOAD_DIR, filename)
    if os.path.exists(f1):
        return send_from_directory(_UPLOAD_DIR, filename)
    f2 = os.path.join(_LEGACY_UPLOAD_DIR, filename)
    if os.path.exists(f2):
        return send_from_directory(_LEGACY_UPLOAD_DIR, filename)
    return jsonify(ok=False, error="upload not found", filename=filename), 404


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
        data_url = str(payload.get("dataUrl") or "").strip()
        if not data_url:
            return jsonify(ok=False, error="dataUrl 또는 file이 필요합니다."), 400
        try:
            mime, img_bytes = _data_url_to_bytes(data_url)
        except Exception:
            return jsonify(ok=False, error="이미지 형식이 올바르지 않습니다(dataUrl)."), 400
        ext = _mime_to_ext(mime)
        slot = re.sub(r"[^a-z0-9_-]+", "", str(payload.get("slot") or "img").lower())[:16] or "img"

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
):
    """얼굴 사진이 포함된 /api/ai/styling 요청을 Gemini로 처리합니다.

    DALL-E는 텍스트→이미지 전용이라 참조 얼굴을 반영할 수 없지만,
    Gemini는 이미지+텍스트 멀티모달이므로 얼굴 특징을 보존할 수 있습니다.
    /api/codistyle/generate와 동일한 Gemini SDK 호출 로직을 재사용합니다.
    """

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
    gender = str(user_info.get("gender", "M")).strip().upper()
    gender_en = "woman" if gender == "F" else "man"
    gender_ko = "여성" if gender == "F" else "남성"
    age = str(user_info.get("ageGroup", "30대")).strip()
    height = str(user_info.get("height", "")).strip()
    weight = str(user_info.get("weight", "")).strip()
    hw_ko = f"키 {height}cm, 몸무게 {weight}kg" if height and weight else ""

    # ── 얼굴 강조 프롬프트 보강 ──
    gemini_prompt = (
        prompt + " "
        "CRITICALLY IMPORTANT: The FIRST image is the face reference photo. "
        "You MUST preserve the EXACT facial features, skin tone, hair style and color of this person. "
        "Generate the image as if THIS EXACT PERSON is wearing the recommended outfit. "
        f"Subject: Korean {gender_en}, {age}"
        + (f", {hw_ko}" if hw_ko else "") + ". "
        "Full body head to toe visible. Photorealistic fashion editorial."
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
        return jsonify(ok=False, error=f"Gemini 호출 실패 ({_SDK}): {str(e)[:300]}"), 500

    # ── 응답에서 이미지 추출 ──
    img_bytes = None
    comment = ""
    try:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                img_bytes = part.inline_data.data
            elif part.text:
                comment = part.text.strip()[:200]
    except (IndexError, AttributeError) as e:
        return jsonify(ok=False, error=f"응답 파싱 실패: {str(e)[:200]}"), 500

    if not img_bytes:
        try:
            finish = response.candidates[0].finish_reason
        except Exception:
            finish = "UNKNOWN"
        return jsonify(ok=False, error=f"이미지 미생성 finishReason={finish} {comment[:100]}"), 500

    if isinstance(img_bytes, str):
        img_bytes = base64.b64decode(img_bytes)

    rel = _write_upload_bytes("ai", ext, img_bytes, fixed_name=cache_fname)
    base = _public_base()
    return jsonify(
        ok=True,
        image=f"{base}{rel}",
        path=rel,
        url=f"{base}{rel}",
        explanation=short or comment or "AI 코디 이미지 생성 완료!",
        model=f"gemini:{model_name}",
        cached=False,
        prompt=gemini_prompt if os.getenv("CODIBANK_DEBUG_PROMPT") == "1" else None,
    )


@app.post("/api/ai/styling")
def ai_styling():
    # API Key 체크: OpenAI 또는 Gemini 중 하나라도 있으면 진행
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_gemini = bool(_GEMINI_KEY)
    if not has_openai and not has_gemini:
        return jsonify(
            ok=False,
            error="OPENAI_API_KEY 또는 GEMINI_API_KEY가 설정되지 않았습니다. 서버 환경변수에 API Key를 설정해주세요.",
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
    # - 같은 조건(날씨/목적/프로필/seed/얼굴/참조의상)로 재요청하면 OpenAI 호출 없이 바로 반환합니다.
    ref_images, face_bytes_for_key = _collect_ref_images(payload)
    cache_key = _make_ai_cache_key(payload, face_bytes_for_key, ref_images)
    ext = "jpg" if output_format.lower() in ("jpeg", "jpg") else output_format.lower()
    cache_fname = f"ai_{cache_key}.{ext}"
    cache_fpath = os.path.join(_UPLOAD_DIR, cache_fname)
    if os.path.exists(cache_fpath):
        rel = f"{_UPLOAD_PREFIX}{cache_fname}"
        base = _public_base()
        return jsonify(
            ok=True,
            image=f"{base}{rel}",  # 프론트 호환: img src로 바로 사용
            path=rel,
            url=f"{base}{rel}",
            explanation=short,
            model="cache",
            cached=True,
        )

    # ── ★ 얼굴 사진이 있으면 Gemini 우선 사용 ──
    # DALL-E(OpenAI)는 텍스트→이미지 모델이라 참조 얼굴 사진을 반영 못합니다.
    # Gemini는 이미지+텍스트 멀티모달이므로 얼굴 특징을 그대로 보존합니다.
    has_face = any(r[0] == "face" for r in ref_images)

    if has_face and _GEMINI_KEY:
        return _ai_styling_via_gemini(payload, prompt, short, ref_images, cache_fname, ext)

    # ── 얼굴 없음 또는 GEMINI_KEY 미설정 → 기존 OpenAI 경로 ──
    if not has_openai:
        return jsonify(
            ok=False,
            error="얼굴 사진 없이 코디 생성하려면 OPENAI_API_KEY가 필요합니다.",
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

@app.post("/api/codistyle/generate")
def codistyle_generate():
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
    user_info = payload.get("user") or {}
    gender    = str(user_info.get("gender", "M")).strip().upper()
    gender_en = "woman" if gender == "F" else "man"
    gender_ko = "여성" if gender == "F" else "남성"
    age       = str(user_info.get("ageGroup", "30대")).strip()
    height    = str(user_info.get("height", "")).strip()
    weight    = str(user_info.get("weight", "")).strip()
    hw_ko     = f"키 {height}cm, 몸무게 {weight}kg" if height and weight else ""
    hw_en     = f"height {height}cm, weight {weight}kg" if height and weight else ""

    # ── 이미지 로드 → bytes ──
    def _to_bytes(data_url_val, path_val=None):
        """dataUrl 또는 로컬파일 → (mime, raw_bytes)"""
        src = str(data_url_val or "").strip()
        if src.startswith("data:"):
            header, b64 = src.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
            return mime, base64.b64decode(b64)
        path = str(path_val or "").strip()
        if path.startswith("/uploads/"):
            fpath = os.path.join(_UPLOAD_DIR, os.path.basename(path))
            if os.path.exists(fpath):
                with open(fpath, "rb") as fh:
                    return "image/jpeg", fh.read()
        return None, None

    top_mime,    top_bytes    = _to_bytes(payload.get("topDataUrl"),    payload.get("topPath"))
    bottom_mime, bottom_bytes = _to_bytes(payload.get("bottomDataUrl"), payload.get("bottomPath"))
    face_mime,   face_bytes   = _to_bytes(payload.get("faceImage"),     None)

    if not top_bytes or not bottom_bytes:
        return jsonify(ok=False, error="상의/하의 이미지가 필요합니다"), 400

    # ── 프롬프트 구성 ──
    if face_bytes:
        face_line = (
            f"The FIRST image is the face reference of the actual person ({gender_ko}"
            + (f", {hw_ko}" if hw_ko else "") + "). "
            "CRITICALLY preserve exact facial features, skin tone, hair style and color. "
            "Generate the image as if THIS EXACT PERSON is wearing the clothes. "
        )
        img_desc = "FIRST image=face reference, SECOND image=upper garment, THIRD image=lower garment."
    else:
        face_line = (
            f"Subject: Korean {gender_en}, {age}"
            + (f", {hw_en}" if hw_en else "") + ". "
        )
        img_desc = "FIRST image=upper garment, SECOND image=lower garment."

    # 한국어 보조 지시 (얼굴 유무에 따라 다르게)
    if face_bytes:
        ko_instruction = "첨부한 얼굴 이미지의 인물이 상의와 하의를 입고 있는 전신 모습을 생성해주세요. "
    else:
        ko_instruction = "첨부한 상의와 하의를 입고 있는 전신 모습을 생성해주세요. "

    prompt = (
        "Create a photorealistic full-body Korean fashion editorial photo. "
        + face_line
        + img_desc + " "
        + ko_instruction
        + "Reproduce the EXACT color, fabric, silhouette, logo of each garment from the reference images. "
        "Full body head to toe visible. Clean Korean urban or studio background. "
        "Professional fashion editorial lighting. Photorealistic. No text. No watermarks."
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
                comment = part.text.strip()[:200]
    except (IndexError, AttributeError) as e:
        return jsonify(ok=False, error=f"응답 파싱 실패: {str(e)[:200]}"), 500

    if not img_bytes:
        try:
            finish = response.candidates[0].finish_reason
        except Exception:
            finish = "UNKNOWN"
        return jsonify(ok=False, error=f"이미지 미생성 finishReason={finish} {comment[:100]}"), 500

    # img_bytes가 bytes인지 확인 (혹시 base64 문자열이면 디코딩)
    if isinstance(img_bytes, str):
        img_bytes = base64.b64decode(img_bytes)

    rel  = _write_upload_bytes("codistyle", "jpg", img_bytes)
    base = _public_base()
    return jsonify(
        ok=True, path=rel,
        image=f"{base}{rel}", url=f"{base}{rel}",
        comment=comment or "AI 착장 이미지 생성 완료!",
        model=_CODISTYLE_MODEL,
        sdk=_SDK,
    )

# ── 관리자 인증 헬퍼 ──
def verify_admin(req):
    """X-Admin-Key 헤더의 sha256 해시가 ADMIN_PW_HASH와 일치하는지 확인"""
    expected = os.environ.get('ADMIN_PW_HASH', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8')
    provided = (req.args.get('key') or req.headers.get('X-Admin-Key') or '').strip()
    if not provided or provided != expected:
        return False
    return True

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
            endpoint_url=os.environ.get('R2_ENDPOINT',''),
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
# A) 프론트엔드 추적 API (인증 불필요 - 이용자 호출용)
# ══════════════════════════════════════

@app.post("/api/track/payment")
def track_payment():
    """결제 완료 시 프론트에서 호출"""
    try:
        d = request.get_json(force=True)
        body = {
            'user_id': d.get('user_id'),
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
            'user_id': d.get('user_id'),
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


@app.post("/api/track/item")
def track_item():
    """아이템 등록 시 프론트에서 호출"""
    try:
        d = request.get_json(force=True)
        body = {
            'user_id': d.get('user_id'),
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8787"))
    # ✅ 안정성 기본값: debug OFF
    # - debug=True(리로더)일 때는 프로세스가 2개 떠서(port가 2개 LISTEN으로 보임)
    #   사용자가 "포트가 점유"되었다고 오해하기 쉽습니다.
    # - 투자자 데모/외부 공유 목적이면 debug=False가 훨씬 안전합니다.
    debug = str(os.getenv("CODIBANK_DEBUG", "0")).strip().lower() in ("1", "true", "yes", "on")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
