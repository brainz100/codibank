# -*- coding: utf-8 -*-
"""
─── 2026-07-04 KST · TJ 지시 ─── CodiBank 장문 번역 파이프라인 v1 ──────────────
스타일리스트 스토리·분석 보고서 같은 '긴 문장'을 다국어로 번역한다.

구조 (하이브리드 2단):
  ① 용어 마스킹  : 패션 도메인 고유어(꾸안꾸·백꾸 등)와 서비스 고유명사를
                   번역 전에 ⟦T00⟧ 토큰으로 치환 → 오역 원천 차단.
                   번역 후 '언어별 고정 번역'으로 복원.
  ② Gemini Flash : 마스킹된 본문만 LLM 번역 (신 SDK google-genai →
                   구 google-generativeai 폴백 — v53 mock_backend 패턴 동일).
  ③ Supabase 캐시: 같은 문장+언어는 1회만 번역 (PostgREST REST, requests 기반).
                   캐시/번역 실패 시 원문 반환 — 서비스는 절대 죽지 않는다.

mock_backend.py 통합 (딱 2줄):
    from translate_pipeline import translate_bp
    app.register_blueprint(translate_bp)

필요 환경변수 (없으면 해당 단계 자동 생략):
    GEMINI_API_KEY            (기존 키 재사용)
    SUPABASE_URL              예: https://drgsayvlpzcacurcczjq.supabase.co
    SUPABASE_SERVICE_KEY      service_role 키 (서버 전용)

Supabase 테이블: translation_cache.sql 참고 (동봉).

엔드포인트:
    POST /api/translate
      body: { "text": "...", "targetLang": "en" }            → { ok, translated }
      body: { "texts": ["...","..."], "targetLang": "ja" }   → { ok, translations: [...] }
    지원 targetLang: en · ja · zh   (그 외/ko → 원문 그대로)

내부 사용 (분석/스토리 생성 직후 호출 권장 — 조회 시가 아니라 생성 시 1회):
    from translate_pipeline import translate_text
    story_en = translate_text(story_ko, "en")
"""

import os
import json
import hashlib
import logging
import re

log = logging.getLogger("codibank.translate")

# ═══════════════════════════════════════════════════════════════════════════
# ① 용어 보호 사전 — 패션 고유어 · 서비스 고유명사 (언어별 고정 번역)
#    ※ 여기 없는 단어만 LLM이 번역한다. 키는 '긴 것 우선' 매칭.
# ═══════════════════════════════════════════════════════════════════════════
PROTECTED_TERMS = {
    # ── 서비스 고유명사 ──
    "코디뱅크":   {"en": "CodiBank",        "ja": "CodiBank",          "zh": "CodiBank", "es": "CodiBank"},
    "코디핏":     {"en": "CodiFit",         "ja": "CodiFit",           "zh": "CodiFit", "es": "CodiFit"},
    "트라이온":   {"en": "Try-On",          "ja": "Try-On",            "zh": "Try-On", "es": "Try-On"},
    "런웨이":     {"en": "Runway",          "ja": "Runway",            "zh": "Runway", "es": "Runway"},
    "스타일몬스터": {"en": "Style Monster", "ja": "Style Monster",     "zh": "Style Monster", "es": "Style Monster"},
    # ── 한국 패션 신조어 (직역 사고 다발 구간) ──
    "꾸안꾸":     {"en": "effortless-chic", "ja": "抜け感スタイル",     "zh": "慵懒高级感", "es": "estilo effortless-chic"},
    "꾸안꾸룩":   {"en": "effortless-chic look", "ja": "抜け感ルック", "zh": "慵懒高级感造型", "es": "look effortless-chic"},
    "남친룩":     {"en": "boyfriend look",  "ja": "彼氏ルック",        "zh": "男友风", "es": "look boyfriend"},
    "여친룩":     {"en": "girlfriend look", "ja": "彼女ルック",        "zh": "女友风", "es": "look girlfriend"},
    "백꾸":       {"en": "bag charm styling", "ja": "バッグチャーム",   "zh": "包包挂饰装扮", "es": "decoración de bolso"},
    "신꾸":       {"en": "shoe charm styling", "ja": "シューデコ",      "zh": "鞋子装饰", "es": "decoración de zapatillas"},
    "올드머니룩": {"en": "old-money look",  "ja": "オールドマネールック", "zh": "老钱风", "es": "look old money"},
    "하객룩":     {"en": "wedding-guest look", "ja": "結婚式お呼ばれコーデ", "zh": "婚礼宾客穿搭", "es": "look de invitada a boda"},
    "소개팅룩":   {"en": "blind-date look", "ja": "お見合いデートルック", "zh": "相亲穿搭", "es": "look de cita a ciegas"},
    "데이트룩":   {"en": "date look",       "ja": "デートルック",       "zh": "约会穿搭", "es": "look de cita"},
    "공항패션":   {"en": "airport fashion", "ja": "空港ファッション",   "zh": "机场穿搭", "es": "moda de aeropuerto"},
    "미니멀룩":   {"en": "minimal look",    "ja": "ミニマルルック",     "zh": "极简风", "es": "look minimalista"},
    "스트릿패션": {"en": "street fashion",  "ja": "ストリートファッション", "zh": "街头风", "es": "moda urbana"},
    "프레피룩":   {"en": "preppy look",     "ja": "プレッピールック",   "zh": "学院风", "es": "look preppy"},
    "빈티지 레트로": {"en": "vintage retro", "ja": "ヴィンテージレトロ", "zh": "复古风", "es": "vintage retro"},
    # ── 스타일 용어 (오역 잦음) ──
    "핏감":       {"en": "fit",             "ja": "フィット感",         "zh": "版型", "es": "ajuste"},
    "레이어드":   {"en": "layering",        "ja": "レイヤード",         "zh": "叠穿", "es": "capas"},
    "톤온톤":     {"en": "tone-on-tone",    "ja": "トーンオントーン",   "zh": "同色系搭配", "es": "tono sobre tono"},
    "포인트 컬러": {"en": "accent color",   "ja": "ポイントカラー",     "zh": "点缀色", "es": "color de acento"},
    "드레이프감": {"en": "drape",           "ja": "ドレープ感",         "zh": "垂坠感", "es": "caída"},
}

_SENTINEL = "\u27e6T{}\u27e7"          # ⟦T0⟧ ⟦T1⟧ … LLM이 건드리지 않는 특수 괄호
_SENTINEL_RE = re.compile(r"\u27e6T(\d+)\u27e7")
_TERM_KEYS = sorted(PROTECTED_TERMS.keys(), key=len, reverse=True)  # 긴 키 우선

SUPPORTED_LANGS = ("en", "ja", "zh", "es")  # 2026-07-04 KST · TJ 지시 — es 추가

LANG_NAME = {"en": "English", "ja": "Japanese", "zh": "Simplified Chinese", "es": "Spanish"}


def mask_terms(text):
    """보호 용어 → 센티널 토큰. (마스킹된 텍스트, 토큰→용어 맵) 반환."""
    token_map = {}
    out = text
    idx = 0
    for term in _TERM_KEYS:
        if term in out:
            tok = _SENTINEL.format(idx)
            token_map[idx] = term
            out = out.replace(term, tok)
            idx += 1
    return out, token_map


def unmask_terms(text, token_map, target_lang):
    """센티널 토큰 → 언어별 고정 번역. LLM이 토큰을 훼손했으면 원어 복원."""
    def _sub(m):
        i = int(m.group(1))
        term = token_map.get(i)
        if term is None:
            return m.group(0)
        fixed = PROTECTED_TERMS.get(term, {})
        return fixed.get(target_lang, fixed.get("en", term))
    return _SENTINEL_RE.sub(_sub, text)


def sentinel_intact(masked_src, translated):
    """번역 결과에 센티널이 전부 살아있는지 검증 (훼손 시 재시도/폴백 판단용)."""
    src_toks = set(_SENTINEL_RE.findall(masked_src))
    out_toks = set(_SENTINEL_RE.findall(translated))
    return src_toks == out_toks


# ═══════════════════════════════════════════════════════════════════════════
# ② Gemini Flash 번역 — 신 SDK(google-genai) → 구 SDK(google-generativeai) 폴백
#    (mock_backend v53과 동일 패턴 · REST 직접호출 금지 원칙 준수)
# ═══════════════════════════════════════════════════════════════════════════
_GEMINI_MODEL = os.environ.get("CODIBANK_TRANSLATE_MODEL", "gemini-2.5-flash")


def _build_prompt(masked_text, target_lang):
    return (
        "You are a professional fashion-domain translator for a Korean styling app.\n"
        f"Translate the Korean text below into natural, fluent {LANG_NAME[target_lang]}.\n"
        "STRICT RULES:\n"
        "1. Tokens like \u27e6T0\u27e7 \u27e6T1\u27e7 are protected terms. Copy them into the "
        "translation VERBATIM at the natural position. NEVER translate, remove, or alter them.\n"
        "2. Keep the tone friendly and professional, as a personal stylist speaking to a client.\n"
        "3. Output ONLY the translation. No preamble, no quotes, no markdown.\n\n"
        f"Korean text:\n{masked_text}"
    )


def _gemini_call(prompt):
    """반환: 번역 문자열 또는 None. (호출 실패는 상위에서 원문 폴백)"""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        log.warning("[translate] GEMINI_API_KEY 미설정 — 번역 생략")
        return None
    # 1) 신 SDK
    try:
        from google import genai as genai_new  # type: ignore
        client = genai_new.Client(api_key=api_key)
        resp = client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        txt = getattr(resp, "text", None)
        if txt:
            return txt.strip()
    except Exception as e:
        log.info("[translate] google-genai 경로 실패(%s) → 구 SDK 폴백", e)
    # 2) 구 SDK
    try:
        import google.generativeai as genai_old  # type: ignore
        genai_old.configure(api_key=api_key)
        model = genai_old.GenerativeModel(_GEMINI_MODEL)
        resp = model.generate_content(prompt)
        txt = getattr(resp, "text", None)
        if txt:
            return txt.strip()
    except Exception as e:
        log.warning("[translate] Gemini 번역 실패: %s", e)
    return None


# ═══════════════════════════════════════════════════════════════════════════
# ③ Supabase 캐시 (PostgREST REST · requests) — 실패해도 파이프는 계속 동작
# ═══════════════════════════════════════════════════════════════════════════
_SB_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
_SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
_CACHE_TABLE = "translation_cache"


def _cache_key(text, target_lang):
    return hashlib.sha256((target_lang + "\x00" + text).encode("utf-8")).hexdigest()


def _sb_headers():
    return {
        "apikey": _SB_KEY,
        "Authorization": "Bearer " + _SB_KEY,
        "Content-Type": "application/json",
    }


def cache_get(text, target_lang):
    if not (_SB_URL and _SB_KEY):
        return None
    try:
        import requests
        key = _cache_key(text, target_lang)
        r = requests.get(
            f"{_SB_URL}/rest/v1/{_CACHE_TABLE}",
            params={"select": "translated", "cache_key": f"eq.{key}", "limit": "1"},
            headers=_sb_headers(), timeout=4,
        )
        if r.status_code == 200:
            rows = r.json()
            if rows:
                return rows[0].get("translated")
    except Exception as e:
        log.info("[translate] cache_get skip: %s", e)
    return None


def cache_set(text, target_lang, translated):
    if not (_SB_URL and _SB_KEY):
        return
    try:
        import requests
        requests.post(
            f"{_SB_URL}/rest/v1/{_CACHE_TABLE}",
            headers={**_sb_headers(), "Prefer": "resolution=ignore-duplicates"},
            data=json.dumps({
                "cache_key": _cache_key(text, target_lang),
                "target_lang": target_lang,
                "source_text": text[:4000],
                "translated": translated,
            }),
            timeout=4,
        )
    except Exception as e:
        log.info("[translate] cache_set skip: %s", e)


# ═══════════════════════════════════════════════════════════════════════════
# 파이프라인 본체
# ═══════════════════════════════════════════════════════════════════════════
def translate_text(text, target_lang):
    """한국어 장문 → target_lang. 어떤 단계가 실패해도 원문을 반환한다(무중단)."""
    if not text or not isinstance(text, str):
        return text
    target_lang = str(target_lang or "").lower()[:2]
    if target_lang not in SUPPORTED_LANGS:
        return text                                     # ko/미지원 → 원문
    stripped = text.strip()
    if not stripped or not re.search(r"[\uac00-\ud7a3]", stripped):
        return text                                     # 한글 없는 텍스트는 그대로

    # 1) 캐시
    cached = cache_get(stripped, target_lang)
    if cached:
        return cached

    # 2) 마스킹 → 번역 → 검증 → 복원
    masked, token_map = mask_terms(stripped)
    translated = _gemini_call(_build_prompt(masked, target_lang))
    if not translated:
        return text                                     # LLM 실패 → 원문
    if token_map and not sentinel_intact(masked, translated):
        # 토큰 훼손 → 1회 재시도, 재실패 시 원문 (오역 노출보다 원문이 안전)
        translated_retry = _gemini_call(_build_prompt(masked, target_lang))
        if translated_retry and sentinel_intact(masked, translated_retry):
            translated = translated_retry
        else:
            log.warning("[translate] sentinel 훼손 — 원문 폴백")
            return text
    result = unmask_terms(translated, token_map, target_lang)

    # 3) 캐시 저장
    cache_set(stripped, target_lang, result)
    return result


def translate_texts(texts, target_lang):
    return [translate_text(t, target_lang) for t in (texts or [])]


# ═══════════════════════════════════════════════════════════════════════════
# Flask Blueprint — mock_backend.py 에 2줄로 등록
# ═══════════════════════════════════════════════════════════════════════════
try:
    from flask import Blueprint, request, jsonify

    translate_bp = Blueprint("codibank_translate", __name__)

    @translate_bp.route("/api/translate", methods=["POST"])
    def _api_translate():
        try:
            body = request.get_json(silent=True) or {}
            lang = body.get("targetLang") or body.get("lang") or "en"
            if "texts" in body:
                return jsonify({"ok": True,
                                "translations": translate_texts(body.get("texts"), lang)})
            return jsonify({"ok": True,
                            "translated": translate_text(body.get("text", ""), lang)})
        except Exception as e:
            log.warning("[translate] endpoint error: %s", e)
            return jsonify({"ok": False, "error": str(e)}), 500
except Exception:                                        # Flask 미설치 환경(단위테스트 등)
    translate_bp = None
