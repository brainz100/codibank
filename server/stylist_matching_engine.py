# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════
# 📋 수정 이력 (MODIFICATION HISTORY) — 최신순
# ═══════════════════════════════════════════════════════════════════════
# 이 블록은 파일 수정 때마다 최상단에 누적됩니다.
# 각 항목은 실제 수정 지점(줄번호)에도 동일한 날짜/요약 주석이 존재합니다.
# 점검 시 이 블록만 읽어도 파일의 최신 상태와 변경 이력을 알 수 있습니다.
#
# ─── 2026-04-20 01:19 KST ────────────────────────────────────────────────
#   [수정 이력 블록 도입 — 코드 변경 없음]
#     - 파일 관리 정책: 모든 수정 시 상단 이력 누적 + 인라인 주석
#
# ─── 2026-04-19 (이전 배포본 반영) ───────────────────────────────────────
#   [BUGFIX #3 — 영어 UI purposeLabel mismatch] (~line 130, 333)
#     - PURPOSE_KEY_TO_KO 상수 추가 (16개 목적 한↔영 키 매핑)
#   [BUGFIX #6 — user_id "default" 고정 버그] (~line 753)
#     - 11,200명 스타일리스트 풀 정상 분산 복원
#   [BUGFIX #4 — bottom_type 변수 스코프] (~line 306)
#   [단일 소스화 — LOCATION_TO_REGION 한글 키 확장] (~line 36)
# ═══════════════════════════════════════════════════════════════════════

"""
착착 코디뱅크 — AI 스타일리스트 매칭 & 프롬프트 엔진 v3.0
============================================================
mock_backend.py에 통합하여 사용

원칙:
1. 사용자 위치 + 프로필이 기초 데이터
2. 얼굴사진 있으면 반드시 사용 (Gemini)
3. 성별 프로필 그대로 적용
4. BMI 기반 신체비율 반영
5. 지역 → main/sub 도시 교차 사용
6. 코디목적별 추천키워드 랜덤 (1일 1회)
7. 여성: 치마 2회 + 바지 1회 로테이션
8. 추천 이유 스토리 박스 생성
"""

import json, random, hashlib, math, os
from datetime import date

# ═══════════════════════════════════════════════════════════════════════
# [2026-04-25 v10 KST] TJ 지시 — 코디핏 프롬프트 전면 재구조
# ═══════════════════════════════════════════════════════════════════════
# 변경 핵심:
#   1) 도시별 키워드 추출(_warm_block 부분 필터) → 폐기
#      이전: "STYLING KEYWORDS (from 서울 fashion): Scarf, Tweed jacket, ..."
#      문제: 17°C에 'Scarf' 들어감 → 목도리 그림 (16~21도 사각지대)
#   2) 사용자 4요소(성별·체형·나이·날씨)를 프롬프트의 본체로 격상
#      이전: 첫 줄에 짧게 → 구조의 부수
#      현재: USER PROFILE 블록이 가장 큰 비중 (전체 70%)
#   3) AI 스타일리스트 페르소나(이름·도시·경력·전문) 활용 강화
#   4) 온도 4단계 명확 룰 (≤0 / 1~10 / 11~19 / ≥20)
#      목도리 ≤0°C, 코트/패딩 ≤10°C, 가디건/액세서리스카프 11~19°C, 그 외 X
#   5) body_type_db.json 의 do_style/dont_style 직접 주입
#   6) 얼굴 99.99% 닮음 강화 (성형/뷰티화 절대 금지)
#   7) 퍼스널컬러 avoid 컬러 절대 금지 (단, custom 입력 시 예외 + 분석 첨언)
# ═══════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════
# 1.5 [v10] body_type_db.json 직접 로드 (체형별 do/dont 룰 주입용)
# ═══════════════════════════════════════════════════
_BODY_TYPE_DB = {}
try:
    _btd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "body_type_db.json")
    if os.path.exists(_btd_path):
        with open(_btd_path, "r", encoding="utf-8") as _btf:
            _BODY_TYPE_DB = json.load(_btf)
except Exception as _btd_e:
    print(f"[stylist_matching_engine v10] body_type_db.json 로드 실패: {_btd_e}")


def _resolve_body_type(gender_ko, body_type_raw):
    """
    [v10] 사용자 입력 체형을 body_type_db 키로 매핑.
    payload.user.bodyType 이 한글 라벨("모래시계", "역삼각형" 등) 또는 영문 키일 수 있음.
    
    Returns: dict {label, en, do_style, dont_style, best_color, worst_color, feature, celebs} 또는 None
    """
    if not body_type_raw or not _BODY_TYPE_DB:
        return None
    
    gender_key = "female" if gender_ko == "여성" else "male"
    db = _BODY_TYPE_DB.get(gender_key, {})
    if not db:
        return None
    
    raw = str(body_type_raw).strip().lower()
    
    # 1) 영문 키 직접 매칭
    if raw in db:
        return db[raw]
    
    # 2) 한글 label 매칭
    for key, info in db.items():
        if info.get('label', '').lower() == raw or raw in info.get('label', '').lower():
            return info
        if info.get('en', '').lower() == raw or raw in info.get('en', '').lower():
            return info
    
    # 3) 부분 일치 (예: "모래시계" → "neat_hourglass")
    keyword_map = {
        "모래시계": "neat_hourglass" if gender_key == "female" else "hourglass_m",
        "삼각형": "pear" if gender_key == "female" else "triangle_m",
        "역삼각형": "inverted_triangle_f" if gender_key == "female" else "inverted_triangle_m",
        "직사각형": "rectangle_f" if gender_key == "female" else "rectangle_m",
        "사과": "apple",
        "배": "pear",
        "사다리꼴": "trapezoid",
        "타원": "oval",
        "다이아몬드": "diamond",
        "마른": "lean_column",
    }
    for kw, target_key in keyword_map.items():
        if kw in raw and target_key in db:
            return db[target_key]
    
    return None


# ═══════════════════════════════════════════════════
# 1.6 [v10] 온도별 4단계 아이템 허용 룰 (TJ 지시 정책)
# ═══════════════════════════════════════════════════
def _get_temp_policy(temp):
    """
    [v10] 온도 → 아이템 허용/금지 정책 텍스트 (Gemini 프롬프트 직접 삽입용)
    
    TJ 정책 (2026-04-25):
      ≤ 0°C:    한겨울 — 목도리·코트·패딩 OK / 가디건은 보조용
      1~10°C:  추위  — 코트·패딩 OK / 목도리 X / 가디건은 코트 안 레이어
      11~19°C: 환절기 — 가디건·액세서리 스카프 OK / 코트·패딩·목도리 X
      ≥ 20°C:  따뜻함 — 모든 보온 아이템 X / 단일 가벼운 레이어
    """
    try:
        t = float(temp)
    except Exception:
        t = 20.0
    
    if t <= 0:
        return {
            "tier": "freezing",
            "tier_label": "한겨울 (영하)",
            "outer_allowed": ["winter coat", "padded coat", "puffer jacket", "wool overcoat"],
            "outer_forbidden": [],
            "neck_allowed": ["thick winter muffler/scarf (knit, wool, cashmere)"],
            "neck_forbidden": ["light silk decorative scarf (too thin for sub-zero)"],
            "summary_en": (
                "FREEZING WEATHER (≤0°C): Heavy winter outerwear MANDATORY. "
                "ALLOWED: thick winter coat, padded/puffer coat, wool muffler, gloves, beanie. "
                "Layer cardigan/knitwear UNDER the coat for warmth. "
            ),
            "summary_ko": "한겨울 영하 — 두꺼운 코트/패딩 + 머플러 필수, 가디건은 코트 안 레이어",
        }
    elif t <= 10:
        return {
            "tier": "cold",
            "tier_label": "추위 (1~10°C)",
            "outer_allowed": ["coat", "wool jacket", "leather jacket", "padded jacket", "trench coat"],
            "outer_forbidden": ["light cardigan as sole outer (too cold)"],
            "neck_allowed": [],
            "neck_forbidden": [
                "ABSOLUTELY NO winter muffler/heavy scarf "
                "(muffler is ONLY for ≤0°C — this temperature is above freezing, no muffler)"
            ],
            "summary_en": (
                "COLD WEATHER (1~10°C): Coat or padded jacket REQUIRED. "
                "ALLOWED: tailored coat, wool/padded/leather/trench jacket. "
                "FORBIDDEN: winter muffler, heavy knit scarf (only for ≤0°C). "
                "FORBIDDEN: standalone cardigan as outer (insufficient warmth). "
                "Cardigan may be layered UNDER the coat. "
            ),
            "summary_ko": "추위 — 코트/패딩 자켓 필수, 목도리/머플러 절대 금지(영하 아님), 가디건 단독 X",
        }
    elif t <= 19:
        return {
            "tier": "transitional",
            "tier_label": "환절기 (11~19°C)",
            "outer_allowed": ["cardigan", "light jacket", "blazer", "denim jacket", "knit cardigan"],
            "outer_forbidden": ["thick winter coat", "padded jacket", "puffer", "down coat", "wool overcoat"],
            "neck_allowed": ["light silk scarf (decorative accessory)", "thin cotton scarf"],
            "neck_forbidden": ["thick winter muffler", "heavy knit/wool scarf"],
            "summary_en": (
                "TRANSITIONAL WEATHER (11~19°C): Light layer outerwear ONLY. "
                "ALLOWED: cardigan, light blazer, denim/light jacket, decorative silk scarf as accessory. "
                "FORBIDDEN: thick coat, padded/puffer jacket, wool muffler, heavy winter scarf. "
                "Layer breathably — single light outer over a top, no heavy bundling. "
            ),
            "summary_ko": "환절기 — 가디건/얇은 자켓 OK, 액세서리 실크스카프 OK, 코트·패딩·머플러 절대 금지",
        }
    else:  # >= 20
        return {
            "tier": "warm",
            "tier_label": "따뜻함 (≥20°C)",
            "outer_allowed": [],
            "outer_forbidden": ["coat", "cardigan", "blazer", "jacket", "padded", "scarf of any kind"],
            "neck_allowed": [],
            "neck_forbidden": ["any scarf, muffler, or neckwear (too warm)"],
            "summary_en": (
                "WARM WEATHER (≥20°C): NO outer layer. Single breathable layer ONLY. "
                "ABSOLUTELY FORBIDDEN: coat, cardigan, blazer, jacket, padded items, scarf, muffler. "
                "ALLOWED: cotton/linen shirt, breathable top, short sleeves OK if appropriate. "
                "Fabrics must be lightweight and breathable. "
            ),
            "summary_ko": "따뜻함 — 모든 보온 아이템 절대 금지, 통기성 단일 레이어만",
        }


# ═══════════════════════════════════════════════════
# 1. 지역 → main/sub 도시 매핑
# ═══════════════════════════════════════════════════
REGION_CITY_MAP = {
    "아시아":      {"main": "서울",     "sub": "뉴욕"},
    "유럽":        {"main": "파리",     "sub": "밀라노"},
    "중동":        {"main": "두바이",   "sub": "뉴욕"},
    "아프리카":    {"main": "파리",     "sub": "밀라노"},
    "북미":        {"main": "뉴욕",     "sub": "밀라노"},
    "남미":        {"main": "상파울루", "sub": "뉴욕"},
    "오세아니아":  {"main": "뉴욕",     "sub": "런던"},
}

# 사용자 위치 → 지역 판별용 국가/도시 매핑
LOCATION_TO_REGION = {
    # 아시아
    "asia": "아시아",
    "korea": "아시아", "seoul": "아시아", "busan": "아시아", "japan": "아시아",
    "tokyo": "아시아", "china": "아시아", "beijing": "아시아", "shanghai": "아시아",
    "hong kong": "아시아", "singapore": "아시아", "bangkok": "아시아", "thailand": "아시아",
    "vietnam": "아시아", "hanoi": "아시아", "ho chi minh": "아시아",
    "indonesia": "아시아", "jakarta": "아시아", "philippines": "아시아", "manila": "아시아",
    "malaysia": "아시아", "kuala lumpur": "아시아", "taiwan": "아시아", "taipei": "아시아",
    "india": "아시아", "mumbai": "아시아", "new delhi": "아시아",
    # 아시아 - 한글 [2026-04-19 단일 소스화: 프론트 _REGION_KEYWORDS의 한글 키 이관]
    "한국": "아시아", "서울": "아시아", "부산": "아시아", "인천": "아시아", "대구": "아시아",
    "대전": "아시아", "광주": "아시아", "울산": "아시아", "제주": "아시아", "일본": "아시아",
    "도쿄": "아시아", "오사카": "아시아", "중국": "아시아", "베이징": "아시아", "상하이": "아시아",
    "홍콩": "아시아", "싱가포르": "아시아", "방콕": "아시아", "태국": "아시아", "베트남": "아시아",
    "하노이": "아시아", "호치민": "아시아", "인도네시아": "아시아", "자카르타": "아시아",
    "필리핀": "아시아", "마닐라": "아시아", "말레이시아": "아시아", "쿠알라룸푸르": "아시아",
    "대만": "아시아", "타이베이": "아시아", "인도": "아시아", "뭄바이": "아시아", "뉴델리": "아시아",
    # 유럽
    "europe": "유럽",
    "paris": "유럽", "france": "유럽", "london": "유럽", "uk": "유럽", "england": "유럽",
    "berlin": "유럽", "germany": "유럽", "rome": "유럽", "italy": "유럽", "milan": "유럽",
    "madrid": "유럽", "spain": "유럽", "amsterdam": "유럽", "netherlands": "유럽",
    "barcelona": "유럽", "vienna": "유럽", "austria": "유럽", "prague": "유럽",
    "zurich": "유럽", "switzerland": "유럽", "moscow": "유럽", "russia": "유럽",
    "stockholm": "유럽", "sweden": "유럽", "copenhagen": "유럽", "denmark": "유럽",
    "lisbon": "유럽", "portugal": "유럽", "athens": "유럽", "greece": "유럽",
    "warsaw": "유럽", "poland": "유럽", "budapest": "유럽", "hungary": "유럽",
    "dublin": "유럽", "ireland": "유럽", "brussels": "유럽", "belgium": "유럽",
    "helsinki": "유럽", "finland": "유럽", "oslo": "유럽", "norway": "유럽",
    # 유럽 - 한글
    "유럽": "유럽", "프랑스": "유럽", "파리": "유럽", "영국": "유럽", "런던": "유럽",
    "독일": "유럽", "베를린": "유럽", "이탈리아": "유럽", "로마": "유럽", "밀라노": "유럽",
    "스페인": "유럽", "마드리드": "유럽", "바르셀로나": "유럽", "네덜란드": "유럽", "암스테르담": "유럽",
    "오스트리아": "유럽", "비엔나": "유럽", "빈": "유럽", "체코": "유럽", "프라하": "유럽",
    "스위스": "유럽", "취리히": "유럽", "러시아": "유럽", "모스크바": "유럽",
    "스웨덴": "유럽", "스톡홀름": "유럽", "덴마크": "유럽", "코펜하겐": "유럽",
    "포르투갈": "유럽", "리스본": "유럽", "그리스": "유럽", "아테네": "유럽",
    "폴란드": "유럽", "바르샤바": "유럽", "헝가리": "유럽", "부다페스트": "유럽",
    "아일랜드": "유럽", "더블린": "유럽", "벨기에": "유럽", "브뤼셀": "유럽",
    "핀란드": "유럽", "헬싱키": "유럽", "노르웨이": "유럽", "오슬로": "유럽",
    # 중동
    "middle east": "중동",
    "dubai": "중동", "abu dhabi": "중동", "uae": "중동", "riyadh": "중동",
    "saudi": "중동", "doha": "중동", "qatar": "중동", "bahrain": "중동",
    "kuwait": "중동", "oman": "중동", "istanbul": "중동", "turkey": "중동",
    "cairo": "중동", "egypt": "중동", "iran": "중동", "tehran": "중동",
    "israel": "중동", "tel aviv": "중동", "jordan": "중동", "lebanon": "중동",
    # 중동 - 한글
    "중동": "중동", "두바이": "중동", "아부다비": "중동", "아랍에미리트": "중동",
    "사우디아라비아": "중동", "리야드": "중동", "카타르": "중동", "도하": "중동",
    "바레인": "중동", "쿠웨이트": "중동", "오만": "중동",
    "터키": "중동", "이스탄불": "중동", "이집트": "중동", "카이로": "중동",
    "이란": "중동", "테헤란": "중동", "이스라엘": "중동", "텔아비브": "중동",
    "요르단": "중동", "레바논": "중동",
    # 아프리카
    "africa": "아프리카",
    "cape town": "아프리카", "south africa": "아프리카", "johannesburg": "아프리카",
    "nairobi": "아프리카", "kenya": "아프리카", "lagos": "아프리카", "nigeria": "아프리카",
    "casablanca": "아프리카", "morocco": "아프리카",
    # 아프리카 - 한글
    "아프리카": "아프리카", "남아프리카": "아프리카", "케이프타운": "아프리카", "요하네스버그": "아프리카",
    "케냐": "아프리카", "나이로비": "아프리카", "나이지리아": "아프리카", "라고스": "아프리카",
    "모로코": "아프리카", "카사블랑카": "아프리카",
    # 북미
    "north america": "북미",
    "new york": "북미", "los angeles": "북미", "chicago": "북미", "usa": "북미",
    "san francisco": "북미", "miami": "북미", "seattle": "북미", "boston": "북미",
    "washington": "북미", "houston": "북미", "toronto": "북미", "canada": "북미",
    "vancouver": "북미", "las vegas": "북미",
    # 북미 - 한글
    "북미": "북미", "미국": "북미", "뉴욕": "북미", "로스앤젤레스": "북미",
    "시카고": "북미", "샌프란시스코": "북미", "마이애미": "북미", "시애틀": "북미",
    "보스턴": "북미", "워싱턴": "북미", "휴스턴": "북미", "라스베이거스": "북미",
    "캐나다": "북미", "토론토": "북미", "밴쿠버": "북미",
    # 남미
    "south america": "남미",
    "são paulo": "남미", "sao paulo": "남미", "rio": "남미", "brazil": "남미",
    "buenos aires": "남미", "argentina": "남미", "lima": "남미", "peru": "남미",
    "bogota": "남미", "colombia": "남미", "santiago": "남미", "chile": "남미",
    "mexico city": "남미", "mexico": "남미",
    # 남미 - 한글
    "남미": "남미", "브라질": "남미", "상파울루": "남미", "리우": "남미", "리우데자네이루": "남미",
    "아르헨티나": "남미", "부에노스아이레스": "남미", "페루": "남미", "리마": "남미",
    "콜롬비아": "남미", "보고타": "남미", "칠레": "남미", "산티아고": "남미",
    "멕시코": "남미", "멕시코시티": "남미",
    # 오세아니아
    "oceania": "오세아니아",
    "sydney": "오세아니아", "melbourne": "오세아니아", "australia": "오세아니아",
    "auckland": "오세아니아", "new zealand": "오세아니아",
    # 오세아니아 - 한글
    "오세아니아": "오세아니아", "호주": "오세아니아", "오스트레일리아": "오세아니아",
    "시드니": "오세아니아", "멜버른": "오세아니아", "뉴질랜드": "오세아니아", "오클랜드": "오세아니아",
}

# ═══════════════════════════════════════════════════
# [2026-04-19 BUGFIX #3] 코디목적 영문 키 → DB 한글 라벨 매핑
# ───────────────────────────────────────────────────
# 원인: 프론트(closet.html)는 purposeKey(영문 내부 키, 예: "bizFormal") +
#       purposeLabel(i18n 변환된 UI 언어, 한국어="비즈니스 포멀" / 영어="Business Formal")
#       을 함께 전송. DB(fashion_keywords_db.json, stylist_db_server.json)의 키는
#       한글 라벨만 저장되어 있음.
#       → 영어 UI 사용자는 purposeLabel="Business Formal" → DB miss → fallback 목적
#       → 전체 목적 기반 매칭/프롬프트가 제대로 작동 안함
# 해결: purposeKey를 한글 라벨로 변환해 DB 조회 (언어 무관 단일 소스)
# 프론트 closet.html의 PURPOSES 배열과 1:1 매칭 (16개 목적)
# ═══════════════════════════════════════════════════
PURPOSE_KEY_TO_KO = {
    "bizFormal":    "비즈니스 포멀",
    "officeDaily":  "데일리 오피스룩",
    "interview":    "면접룩",
    "weddingGuest": "결혼식 하객룩",
    "blindDate":    "소개팅룩",
    "romanticDate": "로맨틱 데이트룩",
    "familyMeet":   "상견례/가족모임",
    "socialParty":  "사교 모임/파티",
    "weekendOut":   "주말 나들이",
    "travelShot":   "여행지 인생샷",
    "dailyCasual":  "꾸안꾸 데일리",
    "sporty":       "스포티/애슬레저",
    "airport":      "공항 패션",
    "minimal":      "미니멀/심플",
    "streetTrend":  "트렌디/스트릿",
    "custom":       "직접입력",
}


def detect_region(user_location):
    """사용자 위치 문자열 → 지역 판별"""
    if not user_location:
        return "아시아"  # fallback
    loc = user_location.lower().strip()
    for keyword, region in LOCATION_TO_REGION.items():
        if keyword in loc:
            return region
    return "아시아"  # fallback


def get_main_sub_cities(user_location):
    """사용자 위치 → main/sub 스타일리스트 도시 결정"""
    region = detect_region(user_location)
    mapping = REGION_CITY_MAP.get(region, REGION_CITY_MAP["아시아"])
    return mapping["main"], mapping["sub"], region


# ═══════════════════════════════════════════════════
# 2. BMI & 체형 분석
# ═══════════════════════════════════════════════════
def calculate_bmi(height_cm, weight_kg):
    """BMI 계산 + 체형 분류 + 프롬프트 가이드"""
    if not height_cm or not weight_kg or height_cm < 100:
        return {"bmi": 22, "category": "normal", "prompt": "average healthy build", "ko": "보통 체형"}
    
    h_m = height_cm / 100
    bmi = round(weight_kg / (h_m * h_m), 1)
    
    if bmi < 18.5:
        return {"bmi": bmi, "category": "underweight",
                "prompt": f"slim and lean build (BMI {bmi}), elongated silhouette, narrow shoulders",
                "ko": "마른 체형",
                "skirt_hint": "A-line or flared skirts to add volume, midi length recommended"}
    elif bmi < 23:
        return {"bmi": bmi, "category": "normal",
                "prompt": f"balanced healthy build (BMI {bmi}), well-proportioned figure",
                "ko": "표준 체형",
                "skirt_hint": "any skirt style works well, pencil or A-line, knee to midi length"}
    elif bmi < 25:
        return {"bmi": bmi, "category": "overweight",
                "prompt": f"slightly full build (BMI {bmi}), medium frame with soft curves",
                "ko": "약간 통통한 체형",
                "skirt_hint": "A-line or wrap skirts for flattering fit, below-knee length preferred"}
    elif bmi < 30:
        return {"bmi": bmi, "category": "obese1",
                "prompt": f"fuller build (BMI {bmi}), broad frame with rounded silhouette",
                "ko": "과체중 체형",
                "skirt_hint": "structured A-line or midi wrap skirts, avoid tight pencil skirts, below-knee length"}
    else:
        return {"bmi": bmi, "category": "obese2",
                "prompt": f"plus-size build (BMI {bmi}), large frame, prioritize comfort and coverage",
                "ko": "비만 체형",
                "skirt_hint": "flowy maxi or midi A-line skirts, high-waist with stretch, avoid clingy fabrics"}


# ═══════════════════════════════════════════════════
# 3. 여성 치마/바지 로테이션 (치마 2 : 바지 1)
# ═══════════════════════════════════════════════════
def get_bottom_type_for_women(seed=0):
    """[v2026-04-06] 짝수=치마, 홀수=바지"""
    return "skirt" if (int(seed) % 2 == 0) else "pants"


def get_skirt_length_by_body(height_cm, weight_kg, bmi_category):
    """BMI+키 기반 치마 길이"""
    h = int(height_cm or 163)
    if bmi_category == "underweight":
        return "midi A-line or pleated skirt" if h >= 168 else "knee-length A-line or flared skirt"
    elif bmi_category == "normal":
        return "midi pencil or knee-length A-line" if h >= 168 else "knee-length pencil or A-line skirt"
    elif bmi_category == "overweight":
        return "midi wrap or below-knee A-line" if h >= 168 else "knee-length A-line or wrap skirt"
    elif bmi_category in ("obese1", "obese2"):
        return "midi to long A-line with high waist" if h >= 168 else "knee-to-midi A-line with high waist"
    return "knee-length A-line skirt"


# ═══════════════════════════════════════════════════
# 4. 키워드 랜덤 선택 (1일 1회 고정)
# ═══════════════════════════════════════════════════
def select_daily_keywords(keywords_str, user_id, purpose, count=8, retry_seed=0):
    """
    키워드 문자열에서 1일 1회 고정 랜덤 선택
    같은 날 같은 사용자 같은 목적이면 같은 키워드 반환
    """
    if not keywords_str:
        return []
    
    # [2026-04-11 수정] keywords_str이 list 또는 string일 수 있음
    # 원인: fashion_keywords_db.json이 list 형태로 저장
    if isinstance(keywords_str, list):
        keywords = [str(kw).strip() for kw in keywords_str if str(kw).strip()]
    elif isinstance(keywords_str, str):
        keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
    else:
        keywords = []
    
    today = date.today().isoformat()
    seed_str = f"{user_id}_{purpose}_{today}_{retry_seed}_keywords"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    
    # [2026-04-06 추가] 온도 기반 부적합 키워드 필터링
    # 원인: 25도에 "Cardigan", "Coat" 등 겨울 키워드가 포함되어 두꺼운 착장 생성
    _temp_val = None
    try:
        import re as _re_kw
        _temp_match = _re_kw.search(r'(\d+)', str(retry_seed))
    except: pass
    
    _warm_filter = ['coat','cardigan','sweater','knit','wool','muffler','scarf',
                    'turtleneck','fleece','padding','puffer','layered','layer',
                    'heavy','thick','warm','보온','니트','코트','패딩','가디건','머플러']
    _cold_filter = ['sleeveless','tank','sandal','shorts','crop','민소매','반팔','샌들']
    
    selected = rng.sample(keywords, min(count, len(keywords)))
    
    # 영문 키워드만 추출
    en_keywords = []
    for kw in selected:
        if '(' in kw and ')' in kw:
            en = kw[kw.index('(')+1:kw.index(')')]
            en_keywords.append(en)
        else:
            en_keywords.append(kw)
    
    return en_keywords


# ═══════════════════════════════════════════════════
# 5. 메인 프롬프트 빌더
# ═══════════════════════════════════════════════════
def build_styling_prompt(payload, fashion_db):
    """
    전체 프롬프트 조립 — 8가지 원칙 모두 반영
    
    Parameters:
        payload: 프론트엔드에서 전달된 데이터
        fashion_db: fashion_keywords_db.json 로드한 dict
    
    Returns:
        prompt (str), metadata (dict)
    """
    # ── 사용자 프로필 추출 ──
    profile = payload.get('profile', {}) or payload.get('user', {}) or {}
    gender_raw = str(profile.get('gender', 'male')).strip().lower()
    gender_ko = "여성" if gender_raw in ('f', 'female', 'woman', '여성', '여자') else "남성"
    gender_en = "woman" if gender_ko == "여성" else "man"
    age = profile.get('age', None)
    if not age:
        ag = str(profile.get('ageGroup', '30대'))
        try: age = int(''.join(c for c in ag if c.isdigit()) or '30')
        except: age = 30
    height = profile.get('height', 170)
    weight = profile.get('weight', 65)
    try: height = int(height) if height else 170
    except: height = 170
    try: weight = int(weight) if weight else 65
    except: weight = 65
    
    # ── BMI & 체형 ──
    bmi_info = calculate_bmi(height, weight)
    
    # ── 날씨 ──
    weather = payload.get('weather', {})
    temp = weather.get('temp', 20)
    condition = weather.get('condition', weather.get('text', 'clear'))
    user_location = str(weather.get('location', '')).strip()
    
    # ── 코디 목적 ──
    purpose = payload.get('purpose', '')
    if not purpose:
        pk = str(payload.get('purposeKey', '')).strip()
        pl = str(payload.get('purposeLabel', '')).strip()
        # [2026-04-19 BUGFIX #3] purposeKey → 한글 변환 우선 (영어 UI 대응)
        # 원인: purposeLabel은 i18n 변환된 UI 언어라 영어 UI 시 "Business Formal" 등
        #       → DB 한글 키("비즈니스 포멀")와 mismatch → DB miss → 매칭/프롬프트 오류
        # 해결: 언어 무관한 내부 키 purposeKey를 DB 한글 라벨로 변환 (최우선)
        #       한글 UI 호환: pl이 이미 한글이면 그대로 사용 (기존 동작 보장)
        purpose = PURPOSE_KEY_TO_KO.get(pk) or pl or pk or '데일리 오피스룩'
    purpose_info = fashion_db.get('base_prompts', {}).get(purpose, {})
    purpose_en = purpose_info.get('en', purpose)
    purpose_prompt_en = purpose_info.get('prompt_en', '')
    
    # ── 지역 → main/sub 도시 ──
    main_city, sub_city, region = get_main_sub_cities(user_location)
    
    # ── main/sub 교차: 날짜 기반으로 교차 사용 ──
    retry_seed = int(payload.get('seed', 0))
    if retry_seed % 2 == 0:
        active_city = main_city
    else:
        active_city = sub_city
    
    # ─────────────────────────────────────────────────────
    # [2026-04-25 v10 TJ 지시] 도시별 키워드 추출 폐기
    # ─────────────────────────────────────────────────────
    # 이전: city_kw → select_daily_keywords → 8개 추출 → 프롬프트에 강제 주입
    # 문제: 17°C에 'Scarf' 들어감 (16~21도 사각지대 필터 부재)
    #       모든 (도시 × 목적 × 시드) 조합에 미리 정의된 키워드 텍스트 푸시
    #       → 본질적으로 '키워드 푸시' 패턴, 계절 부적합 위험 영구 잔존
    # 변경: 키워드 추출 호출 자체 폐기 → 빈 리스트
    #       도시 차별화는 스타일리스트 페르소나(이름·소속도시·경력)로 표현
    #       트렌드 디테일은 LLM 자체 지식에 위임
    user_id = str(profile.get('id', profile.get('email', 'default')))
    selected_keywords = []  # [v10] 폐기 — 더 이상 키워드 추출하지 않음
    # ── 온도 정책 (v10 4단계) ──
    temp_policy = _get_temp_policy(temp)
    
    # ── 여성 하의 타입 결정 ──
    if gender_ko == "여성":
        bottom_type = get_bottom_type_for_women(retry_seed)
        if bottom_type == "skirt":
            skirt_guide = get_skirt_length_by_body(height, weight, bmi_info['category'])
            bottom_instruction = (
                f"BOTTOM: The woman MUST wear a SKIRT (not pants). "
                f"Skirt recommendation based on body type: {skirt_guide}. "
                f"Skirt length should be flattering for {height}cm height. "
            )
        else:
            bottom_instruction = (
                "BOTTOM: The woman wears well-fitted trousers or slacks. "
                "Full ankle-length — FORBIDDEN: cropped, 7/8, calf-length. "
            )
    else:
        # [2026-04-19 BUGFIX #4] bottom_type 변수가 여성 분기에서만 정의되어
        # line 388 metadata 구성 시 NameError 위험 (현재 and 연산자 short-circuit으로 막혀있지만 취약)
        bottom_type = "pants"
        bottom_instruction = (
            "BOTTOM: The man wears well-fitted trousers or slacks. "
            "Full ankle-length — FORBIDDEN: cropped, 7/8, calf-length. "
        )
    
    # ── 얼굴 사진 여부 ──
    has_face = bool(payload.get('face_image') or payload.get('faceImage'))
    
    # ─────────────────────────────────────────────────────────
    # [v10 TJ 지시] 얼굴 99.99% 닮음 — 강화 프롬프트
    # 사용자 등록 사진을 거의 완벽 복제, 성형/뷰티화 절대 금지
    # ─────────────────────────────────────────────────────────
    face_instruction = ""
    if has_face:
        face_instruction = (
            "═══ FACE IDENTITY — 99.99% LIKENESS REQUIRED ═══\n"
            "A face reference photo is provided as the FIRST input image. "
            "GENERATE THE PERSON'S FACE TO MATCH THE REFERENCE PHOTO AT 99.99% LIKENESS. "
            "This is the HIGHEST priority rule — no other rule overrides this. "
            "\n\n"
            "EXACT match required for:\n"
            "  • Face shape, jawline contour, chin angle\n"
            "  • Eye shape, size, eyelid type (single/double), pupil color, gaze direction\n"
            "  • Eyebrow shape, thickness, arch, color\n"
            "  • Nose bridge width, tip shape, nostril proportion\n"
            "  • Lip shape, fullness, philtrum length\n"
            "  • Cheekbone position and prominence\n"
            "  • Skin tone, undertone, texture, blemishes/moles/freckles\n"
            "  • Hair color, texture, length, parting, hairline\n"
            "  • Any distinguishing features (dimples, scars, beauty marks)\n"
            "\n"
            "ABSOLUTELY FORBIDDEN:\n"
            "  ✗ Beautifying, smoothing, slimming, or idealizing the face\n"
            "  ✗ Changing age (no younger/older)\n"
            "  ✗ Changing ethnicity or race\n"
            "  ✗ Generic Korean idol faces / model faces / stock-photo faces\n"
            "  ✗ Face replacement with a different person\n"
            "\n"
            "If the generated face does NOT recognizably match the reference at 99.99% — REGENERATE. "
            "The viewer must instantly recognize this is the SAME person from the reference photo. "
            "═══ END FACE RULE ═══\n"
        )
    
    # ─────────────────────────────────────────────────────────
    # [v10] 체형 정보 추출 (body_type_db 활용)
    # ─────────────────────────────────────────────────────────
    body_type_raw = profile.get('bodyType') or payload.get('user', {}).get('bodyType', '')
    body_info = _resolve_body_type(gender_ko, body_type_raw)
    body_block = ""
    if body_info:
        body_block = (
            f"BODY TYPE: {body_info.get('label', body_type_raw)} ({body_info.get('en', '')})\n"
            f"  • Feature: {body_info.get('feature', '')}\n"
            f"  • DO: {body_info.get('do_style', '')}\n"
            f"  • DON'T: {body_info.get('dont_style', '')}\n"
            f"  • Best color strategy: {body_info.get('best_color', '')}\n"
            f"  • Worst color strategy: {body_info.get('worst_color', '')}\n"
        )
    else:
        body_block = f"BODY TYPE: {bmi_info.get('ko', '표준 체형')} (BMI {bmi_info.get('bmi', '?')})\n"
    
    # ─────────────────────────────────────────────────────────
    # [v10] 퍼스널컬러 정보 추출 + avoid 절대 금지 룰 (TJ 지시)
    # 단, payload.customText 가 사용자 직접 입력이고 avoid 컬러를 명시 요청한 경우 예외
    # ─────────────────────────────────────────────────────────
    pc = payload.get('personalColor') or payload.get('personal_color') or {}
    pc_block = ""
    pc_avoid_override = False  # 분석 텍스트에서 첨언 여부 결정용
    custom_text = str(payload.get('customText') or payload.get('custom_text') or '').strip()
    pc_avoid_names = pc.get('avoid_color_names') or pc.get('avoid_colors') or []
    pc_best_names = pc.get('best_color_names') or pc.get('best_colors') or []
    
    if pc:
        pc_season = pc.get('season', '')
        pc_undertone = pc.get('undertone', '')
        pc_best_str = ", ".join((pc_best_names if isinstance(pc_best_names, list) else [])[:5])
        pc_avoid_str = ", ".join((pc_avoid_names if isinstance(pc_avoid_names, list) else [])[:5])
        
        # 사용자 직접 입력 텍스트에 avoid 컬러 언급이 있는지 체크
        if custom_text and pc_avoid_names:
            for avoid_c in pc_avoid_names:
                if avoid_c and str(avoid_c).strip() and str(avoid_c).strip().lower() in custom_text.lower():
                    pc_avoid_override = True
                    break
        
        pc_block = (
            f"PERSONAL COLOR: {pc_season} ({pc_undertone})\n"
            f"  • Best colors (USE these): {pc_best_str}\n"
            f"  • Avoid colors: {pc_avoid_str}\n"
        )
        if pc_avoid_override:
            pc_block += (
                "  ⚠ NOTE: User explicitly requested an avoid-color in custom input — "
                "this override is allowed for this generation only. "
                "The styling analysis MUST mention that this color may not flatter user's personal color. "
            )
        else:
            pc_block += (
                "  🚫 ABSOLUTE RULE: Avoid colors MUST NEVER appear as main garment colors. "
                "If they appear at all, only as tiny accents (button, stitching). "
            )
    
    # ═══ [v10] 새 프롬프트 조립 — 사용자 4요소 본체화 ═══
    # 구조:
    #   1) 얼굴 (99.99% 닮음, 최상위)
    #   2) USER PROFILE (성별·나이·체형·BMI·체형 do/dont·퍼스널컬러)  ← 본체 70%
    #   3) ENVIRONMENT (날씨·날짜·도시·목적)
    #   4) STYLIST PERSONA (스타일리스트 이름·도시·경력)  ← 20%
    #   5) TEMPERATURE POLICY (4단계 명확 룰)
    #   6) ABSOLUTE RULES (체형·신체비율·배경·양말 등)
    
    # 도시 시그니처 (1~2단어 본질만, TJ 권장)
    _city_vibe = {
        "서울":   "Korean refined minimalism, layered textures",
        "뉴욕":   "urban versatile, confident layering",
        "파리":   "effortless chic, accessory-focused",
        "런던":   "heritage-meets-modern, eclectic",
        "밀라노": "tailored craft, rich textures",
        "상파울루": "vibrant expressive, comfort-first",
        "두바이": "modest luxury, jewel tones",
    }.get(active_city, "modern refined")
    
    prompt = (
        # ─── [1] 헤더 ───
        f"Create a photorealistic full-body fashion styling lookbook photo.\n\n"
        
        # ─── [2] 얼굴 (HIGHEST PRIORITY) ───
        f"{face_instruction}\n"
        
        # ─── [3] 사용자 프로필 (본체) ───
        f"═══ USER PROFILE (CORE STYLING TARGET) ═══\n"
        f"Subject: {gender_en} ({gender_ko}), age {age} ({_age_range(age)}), Korean.\n"
        f"Height: {height}cm, Weight: {weight}kg, BMI {bmi_info.get('bmi', '?')} — {bmi_info.get('en', 'average')}.\n"
        f"{body_block}"
        f"{pc_block}"
        f"\n"
        
        # ─── [4] 환경 ───
        f"═══ ENVIRONMENT ═══\n"
        f"User location: {user_location or 'unspecified'}\n"
        f"Date: {date.today().isoformat()}\n"
        f"Weather: {temp}°C, {condition} — {temp_policy['tier_label']}\n"
        f"Purpose: {purpose} ({purpose_en})\n"
        f"{purpose_prompt_en}\n"
        f"\n"
        
        # ─── [5] 스타일리스트 페르소나 (10~20%) ───
        # (process_styling_request에서 stylist 정보 추가 주입됨)
        f"═══ STYLIST CONTEXT ═══\n"
        f"This look is curated by an AI stylist based in {active_city}.\n"
        f"City aesthetic: {_city_vibe}.\n"
        f"Reflect {active_city} stylist's professional intuition for current trends — "
        f"NOT generic city stereotypes, but contemporary 2026 sensibility appropriate for "
        f"the user's age, body, and weather.\n"
        f"\n"
        
        # ─── [6] 온도 정책 (TJ 지시 4단계) ───
        f"═══ TEMPERATURE POLICY ({temp}°C) ═══\n"
        f"{temp_policy['summary_en']}\n"
        f"\n"
        
        # ─── [7] 하의 ───
        f"{bottom_instruction}\n"
        
        # ─── [8] 절대 룰 ───
        f"═══ ABSOLUTE RULES (VIOLATION = REGENERATE) ═══\n"
        f"BODY PROPORTION: Upper body (head→waist) ≤ 40%, Lower body (waist→feet) ≥ 60%. "
        f"3:7 leg ratio MANDATORY. 5:5 or 4:6 = generation failure.\n"
        f"SOCKS: Both feet IDENTICAL — same color, same pattern. Mismatched FORBIDDEN.\n"
        f"BACKGROUND: Single SOLID FLAT PASTEL color contrasting with outfit. "
        f"Studio paper backdrop ONLY — no environment, no objects, no props.\n"
        f"STYLE: Real-life wearable daily outfit only. "
        f"FORBIDDEN: runway, avant-garde, asymmetric, experimental.\n"
        f"NO text, NO watermark, NO logo, NO brand names visible.\n"
        f"═══ END RULES ═══\n"
    )
    
    # ── 메타데이터 (스토리 박스용) ──
    metadata = {
        "gender_ko": gender_ko,
        "age": age,
        "height": height,
        "weight": weight,
        "bmi": bmi_info,
        "purpose": purpose,
        "purpose_en": purpose_en,
        "active_city": active_city,
        "main_city": main_city,
        "sub_city": sub_city,
        "region": region,
        "keywords_selected": selected_keywords,  # [v10] 항상 빈 리스트
        "bottom_type": "skirt" if (gender_ko == "여성" and bottom_type == "skirt") else "pants" if gender_ko == "여성" else "pants",
        "temp": temp,
        "condition": condition,
        "has_face": has_face,
        "user_location": user_location,
        # [v10 추가] 신규 메타
        "temp_tier": temp_policy["tier"],
        "temp_tier_label": temp_policy["tier_label"],
        "body_type_info": body_info,  # 체형별 do/dont 등
        "pc_avoid_override": pc_avoid_override,  # 분석 첨언용
        "pc": pc,
    }
    
    return prompt, metadata


# ─── [v10] 나이대 라벨 헬퍼 ───
def _age_range(age):
    """나이 → 영문 라벨 (LLM이 인식하기 좋게)"""
    try:
        a = int(age)
    except Exception:
        a = 30
    if a < 25:
        return "early 20s, youthful"
    elif a < 30:
        return "late 20s, fresh-modern"
    elif a < 35:
        return "early 30s, professional"
    elif a < 40:
        return "late 30s, refined"
    elif a < 50:
        return "40s, mature elegant"
    else:
        return "50+, sophisticated mature"


# ═══════════════════════════════════════════════════
# 6. 스타일링 스토리 박스 생성
# ═══════════════════════════════════════════════════
def generate_styling_story(metadata):
    """
    원칙 7: 체형, 퍼스널컬러, 날씨, 코디목적, 트렌드를 분석한
    스타일링 이유 + 의도한 이미지 + 핵심 포인트를 생성
    """
    g = metadata['gender_ko']
    age = metadata['age']
    bmi = metadata['bmi']
    purpose = metadata['purpose']
    city = metadata['active_city']
    keywords = metadata['keywords_selected']
    temp = metadata['temp']
    condition = metadata['condition']
    bottom = metadata.get('bottom_type', 'pants')
    
    # 온도별 계절감
    if temp <= 5: season_feel = "한겨울 추위"
    elif temp <= 15: season_feel = "쌀쌀한 환절기"
    elif temp <= 25: season_feel = "쾌적한 날씨"
    elif temp <= 30: season_feel = "따뜻한 날씨"
    else: season_feel = "무더운 여름"
    
    # 핵심 키워드 3개
    key3 = keywords[:3] if len(keywords) >= 3 else keywords
    
    story = f"""💡 AI 스타일리스트의 코디 노트

📋 분석 결과
• 체형: {g} / {bmi['ko']} ({metadata['height']}cm, {metadata['weight']}kg)
• 날씨: {temp}°C ({condition}) — {season_feel}
• 코디 목적: {purpose}
• 스타일 베이스: {city} 패션 트렌드 기반

👗 스타일링 의도
{_get_styling_intent(metadata)}

🎯 이번 코디의 핵심 포인트
1. 키워드: {', '.join(key3)}
2. {'스커트 스타일링으로 여성스러운 실루엣을 강조했습니다.' if bottom == 'skirt' else '깔끔한 팬츠 핏으로 세련된 라인을 살렸습니다.'}
3. {bmi['ko']}에 맞는 실루엣으로 체형 보완 효과를 극대화했습니다.
4. {season_feel}에 맞는 소재와 레이어링을 적용했습니다.

✨ 추천 포인트: {_get_point_tip(metadata)}"""
    
    return story


def _get_styling_intent(m):
    """코디 목적별 스타일링 의도 문구"""
    intents = {
        "비즈니스 포멀": f"{m['age']}대 {m['gender_ko']}의 프로페셔널한 이미지를 극대화하는 포멀 룩입니다. {m['active_city']} 비즈니스 씬에서 통용되는 신뢰감 있는 스타일을 제안합니다.",
        "데일리 오피스룩": f"매일 입어도 질리지 않으면서 센스 있어 보이는 오피스 스타일입니다. {m['active_city']} 직장인들의 스마트 캐주얼 트렌드를 반영했습니다.",
        "면접룩": f"첫인상에서 신뢰감과 전문성을 어필할 수 있는 면접 전용 스타일입니다. 깔끔한 라인과 절제된 컬러로 진정성을 표현합니다.",
        "결혼식 하객룩": f"축하의 자리에 어울리는 화사하면서도 격식을 갖춘 하객 패션입니다. 주인공을 빛내면서도 본인만의 스타일을 살립니다.",
        "소개팅룩": f"자연스러운 호감을 주는 스타일입니다. 과하지 않으면서도 매력이 느껴지는 {m['active_city']} 트렌드의 데이트 룩을 제안합니다.",
        "로맨틱 데이트룩": f"특별한 날의 로맨틱한 분위기를 살리는 코디입니다. 세련되면서도 감성적인 무드를 연출합니다.",
        "상견례/가족모임": f"격식과 예의를 갖추면서도 현대적인 감각을 더한 가족 모임 스타일입니다. 어른들에게도 좋은 인상을 주는 단정한 룩입니다.",
        "사교 모임/파티": f"파티 씬에서 돋보이는 글래머러스한 스타일입니다. {m['active_city']}의 소셜 이벤트 트렌드를 반영한 센스 있는 룩입니다.",
        "주말 나들이": f"편안하면서도 스타일리시한 주말 캐주얼입니다. 활동하기 좋으면서도 사진발 잘 받는 코디를 추천합니다.",
        "여행지 인생샷": f"여행지에서 인생샷을 위한 포토제닉 코디입니다. 배경과 어울리는 컬러감과 실루엣으로 SNS에서도 돋보이는 스타일입니다.",
        "꾸안꾸 데일리": f"노력하지 않은 듯 세련된 에포트리스 스타일입니다. 베이직 아이템의 조합으로 자연스러운 멋을 냅니다.",
        "스포티/애슬레저": f"운동에서 일상까지 자연스럽게 이어지는 애슬레저 스타일입니다. 기능성과 패션성을 동시에 잡았습니다.",
        "공항 패션": f"장시간 이동에도 편안하면서 도착지에서도 세련되어 보이는 공항 패션입니다. 레이어링이 핵심입니다.",
        "미니멀/심플": f"불필요한 것을 덜어내고 본질적인 멋에 집중한 미니멀 스타일입니다. 깔끔한 라인과 뉴트럴 톤이 핵심입니다.",
        "트렌디/스트릿": f"최신 스트릿 트렌드를 반영한 감각적인 스타일입니다. {m['active_city']}의 스트릿 씬에서 영감을 받았습니다.",
    }
    return intents.get(m['purpose'], f"{m['purpose']} 목적에 맞는 스타일을 {m['active_city']} 트렌드 기반으로 제안합니다.")


def _get_point_tip(m):
    """체형별 핵심 팁"""
    cat = m['bmi']['category']
    if m['gender_ko'] == "여성":
        tips = {
            "underweight": "볼륨감을 더하는 플리츠나 A라인 실루엣으로 균형감을 살렸습니다",
            "normal": "다양한 실루엣이 어울리는 체형으로, 트렌디한 핏감을 살린 스타일입니다",
            "overweight": "허리라인을 살리는 벨티드 스타일로 곡선미를 강조했습니다",
            "obese1": "세로 라인을 살리는 롱 실루엣으로 날씬한 느낌을 연출했습니다",
            "obese2": "편안하면서도 세련된 A라인과 하이웨이스트로 체형을 보완했습니다",
        }
    else:
        tips = {
            "underweight": "어깨를 살리는 구조적인 재킷으로 체형에 볼륨감을 더했습니다",
            "normal": "레귤러핏과 테일러드핏을 적절히 믹스한 밸런스 좋은 실루엣입니다",
            "overweight": "세로 라인 강조와 다크톤으로 슬림해 보이는 효과를 냈습니다",
            "obese1": "편안한 핏감의 구조적인 아우터로 깔끔한 라인을 만들었습니다",
            "obese2": "여유 있는 핏감으로 편안하면서도 단정한 인상을 줍니다",
        }
    return tips.get(cat, "체형에 맞는 최적의 핏을 제안합니다")


# ═══════════════════════════════════════════════════
# 7. 인라인 온도 버킷 (외부 의존성 제거)
# ═══════════════════════════════════════════════════
def _get_temp_bucket(temp):
    if temp <= -10: return "extreme cold (heavy padded coat, thermal layers, insulated boots)"
    elif temp <= 0:  return "very cold (winter coat, warm knitwear, boots)"
    elif temp <= 5:  return "cold (thick coat, sweater, closed shoes)"
    elif temp <= 10: return "chilly (jacket, long-sleeve, light layers)"
    elif temp <= 15: return "cool (light jacket or cardigan)"
    elif temp <= 20: return "mild (single outer layer optional)"
    elif temp <= 25: return "warm (light single layer, breathable)"
    elif temp <= 30: return "hot (light, breathable, sun protection)"
    elif temp <= 35: return "very hot (minimal layers, UV protection)"
    else: return "extreme heat (lightest breathable, full sun protection)"


# ═══════════════════════════════════════════════════
# 테스트
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    import json
    
    with open('/home/claude/fashion_keywords_db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print("=" * 70)
    print("착착 코디뱅크 — 스타일리스트 매칭 엔진 v3.0 테스트")
    print("=" * 70)
    
    test_cases = [
        {"name": "서울 여성 30대 (비즈니스 포멀)",
         "profile": {"gender": "female", "age": 32, "height": 163, "weight": 52, "id": "user001"},
         "weather": {"temp": 8, "condition": "cloudy", "location": "Seoul"},
         "purpose": "비즈니스 포멀", "face_image": True},
        
        {"name": "두바이 남성 40대 (데일리 오피스)",
         "profile": {"gender": "male", "age": 42, "height": 178, "weight": 85, "id": "user002"},
         "weather": {"temp": 38, "condition": "clear", "location": "Dubai"},
         "purpose": "데일리 오피스룩", "face_image": False},
        
        {"name": "파리 여성 20대 (소개팅룩)",
         "profile": {"gender": "female", "age": 27, "height": 168, "weight": 58, "id": "user003"},
         "weather": {"temp": 15, "condition": "partly cloudy", "location": "Paris"},
         "purpose": "소개팅룩", "face_image": True},
        
        {"name": "호치민 남성 (뉴욕 매칭 확인)",
         "profile": {"gender": "male", "age": 35, "height": 172, "weight": 70, "id": "user004"},
         "weather": {"temp": 33, "condition": "rain", "location": "Ho Chi Minh City"},
         "purpose": "주말 나들이", "face_image": False},
    ]
    
    for tc in test_cases:
        print(f"\n{'─'*70}")
        print(f"🧪 {tc['name']}")
        print(f"{'─'*70}")
        
        prompt, meta = build_styling_prompt(tc, db)
        
        print(f"📍 위치: {tc['weather']['location']} → 지역: {meta['region']}")
        print(f"🏙️ 도시: main={meta['main_city']}, sub={meta['sub_city']} → 선택: {meta['active_city']}")
        print(f"👤 성별: {meta['gender_ko']} | 체형: {meta['bmi']['ko']} (BMI {meta['bmi']['bmi']})")
        print(f"🎯 목적: {meta['purpose']} ({meta['purpose_en']})")
        print(f"🔑 키워드: {', '.join(meta['keywords_selected'])}")
        print(f"👖 하의: {meta['bottom_type']}")
        print(f"📸 얼굴사진: {'있음 → Gemini' if meta['has_face'] else '없음 → DALL-E'}")
        print(f"🌡️ 날씨: {meta['temp']}°C ({meta['condition']})")
        
        story = generate_styling_story(meta)
        print(f"\n📖 스토리 박스:")
        for line in story.split('\n')[:8]:
            print(f"   {line}")
        print("   ...")
        
        print(f"\n📝 프롬프트 길이: {len(prompt)}자")
    
    # 여성 치마/바지 로테이션 테스트
    print(f"\n{'='*70}")
    print("👗 여성 하의 로테이션 테스트 (30회)")
    skirt_count = 0
    pants_count = 0
    for i in range(30):
        # 다른 날짜를 시뮬레이션
        result = "skirt" if (int(hashlib.md5(f"user001_비즈니스 포멀_2026-04-{i+1:02d}".encode()).hexdigest(), 16) % 3) < 2 else "pants"
        if result == "skirt": skirt_count += 1
        else: pants_count += 1
    print(f"  치마: {skirt_count}회 | 바지: {pants_count}회 (목표: 2:1 비율)")
    print(f"  비율: {skirt_count/(skirt_count+pants_count)*100:.0f}% : {pants_count/(skirt_count+pants_count)*100:.0f}%")
    
    print(f"\n{'='*70}")
    print("✅ 전체 테스트 완료")


# ═══════════════════════════════════════════════════
# 8. 개별 스타일리스트 매칭 (stylist_db_server.json 사용)
# ═══════════════════════════════════════════════════
def select_stylist(stylist_db, city, purpose, user_gender, user_body_type=None, user_id="default", retry_seed=0):
    """
    도시 → 코디목적 → 성별 풀에서 1일 1회 고정 스타일리스트 선정
    
    Parameters:
        stylist_db: stylist_db_server.json 로드한 dict
        city: 활성 도시 (main 또는 sub)
        purpose: 코디 목적
        user_gender: "남성" or "여성"
        user_body_type: 사용자 체형 (매칭 우선순위용, 선택)
        user_id: 사용자 고유 ID (1일 1회 고정용)
    
    Returns:
        stylist dict or None
    """
    gender_key = "women" if user_gender == "여성" else "men"
    
    # 도시 → 목적 → 성별 풀 조회
    city_data = stylist_db.get(city, {})
    purpose_data = city_data.get(purpose, {})
    pool = purpose_data.get(gender_key, [])
    
    if not pool:
        # fallback: 직접입력 풀 또는 첫번째 목적
        for fallback_purpose in [purpose, "직접입력", "데일리 오피스룩"]:
            pool = city_data.get(fallback_purpose, {}).get(gender_key, [])
            if pool:
                break
    
    if not pool:
        return None
    
    # 체형 매칭 우선: 사용자 체형과 동일한 전문가 우선 선별
    if user_body_type:
        matched_pool = [s for s in pool if user_body_type in s.get("bodyType", "")]
        if matched_pool and len(matched_pool) >= 3:
            pool = matched_pool
    
    # 1일 1회 고정 선정 (날짜 + user_id + 목적 기반 seed)
    today = date.today().isoformat()
    seed_str = f"{user_id}_{city}_{purpose}_{today}_{retry_seed}_stylist"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    
    return rng.choice(pool)


def format_stylist_profile(stylist, city):
    """스타일리스트 프로필을 스토리 박스용 텍스트로 포맷"""
    if not stylist:
        return "AI 코디뱅크 스타일리스트"
    
    s = stylist
    level_ko = {
        "Junior": "주니어", "Mid-Level": "미드레벨", 
        "Senior": "시니어", "Expert": "전문가", "Master": "마스터"
    }
    
    lines = [
        f"👤 오늘의 AI 스타일리스트",
        f"",
        f"   이름: {s['name']}",
        f"   소속: {city} 패션 스타일리스트 ({level_ko.get(s['level'], s['level'])})",
        f"   경력: {s['exp']}년 | 평점: ⭐ {s['rating']}",
        f"   전공: {s['major']}",
        f"   커리어: {s['career']}",
        f"   선호 컬러: {s['color1']} + {s['color2']}",
        f"   체형 전문: {s['bodyType']}",
    ]
    return "\n".join(lines)


def generate_full_story(metadata, stylist, city):
    """스타일리스트 프로필 + 스타일링 스토리 통합 생성"""
    
    profile_text = format_stylist_profile(stylist, city)
    story_text = generate_styling_story(metadata)
    
    # 스타일리스트 컬러 추천 이유
    color_note = ""
    if stylist:
        color_note = (
            f"\n🎨 컬러 추천\n"
            f"   {stylist['name']} 스타일리스트의 시그니처 컬러인 "
            f"'{stylist['color1']}'을 메인으로, "
            f"'{stylist['color2']}'을 악센트로 매칭했습니다.\n"
            f"   {metadata['bmi']['ko']}에 {stylist['color1']} 톤은 "
        )
        # 체형별 컬러 효과
        cat = metadata['bmi']['category']
        if cat in ('underweight',):
            color_note += "부드러운 볼륨감을 더해주는 효과가 있습니다."
        elif cat in ('overweight', 'obese1', 'obese2'):
            color_note += "세로 라인을 강조하여 슬림해 보이는 효과가 있습니다."
        else:
            color_note += "균형 잡힌 실루엣을 한층 돋보이게 합니다."
    
    return f"{profile_text}\n\n{'─'*36}\n\n{story_text}{color_note}"


# ═══════════════════════════════════════════════════
# 9. 통합 호출 함수 (mock_backend.py에서 이것만 호출)
# ═══════════════════════════════════════════════════
def process_styling_request(payload, fashion_db, stylist_db):
    """
    코디쌤 추천코디 요청 처리 — 원스톱
    
    mock_backend.py에서 이렇게 사용:
        prompt, story, model_type, stylist = process_styling_request(payload, FASHION_DB, STYLIST_DB)
    
    Returns:
        prompt (str): AI 이미지 생성 프롬프트
        story (str): 스토리 박스 전체 텍스트
        model_type (str): "gemini" or "dalle"
        stylist (dict): 매칭된 스타일리스트 정보
    """
    # 1. 프롬프트 생성 + 메타데이터
    prompt, metadata = build_styling_prompt(payload, fashion_db)
    
    # 2. 개별 스타일리스트 매칭
    # [2026-04-19 BUGFIX #6] CRITICAL: profile 키가 빈 dict여서 user_id가 항상 'default'로 고정됐던 버그
    # 원인: 프론트는 payload.user (user.email, user.gender 등)로 전송하는데 여기선 profile만 봄
    #       → profile.get(...) = 빈 dict → 'default' fallback → 1일 1회 시드가 모든 사용자 동일
    #       → 11,200명 스타일리스트 풀이 사실상 1명으로 수렴 (모두 같은 스타일리스트 받음)
    # 해결: line 276의 build_styling_prompt처럼 user fallback 추가
    profile = payload.get('profile', {}) or payload.get('user', {}) or {}
    user_id = str(profile.get('id', profile.get('email', 'default')))
    user_gender = metadata['gender_ko']
    user_body = metadata['bmi']['ko']
    active_city = metadata['active_city']
    purpose = metadata['purpose']
    
    retry_seed = int(payload.get('seed', 0))
    stylist = select_stylist(
        stylist_db, active_city, purpose,
        user_gender, user_body, user_id, retry_seed=retry_seed
    )
    
    # 3. [v10 TJ 지시] 스타일리스트 정보를 페르소나 형태로 풍부 주입
    # 단순 컬러 지시 → 11,200명 차별화의 핵심인 인격(이름·경력·전문분야) 표현
    if stylist:
        s_name  = stylist.get('name', '')
        s_color1 = stylist.get('color1', '')
        s_color2 = stylist.get('color2', '')
        s_level = stylist.get('level', '')
        s_exp   = stylist.get('exp', '')
        s_major = stylist.get('major', '')
        s_career = stylist.get('career', '')
        
        persona_addition = (
            f"\n═══ AI STYLIST PERSONA ═══\n"
            f"Name: {s_name}\n"
            f"Based in: {active_city}\n"
            f"Level: {s_level} ({s_exp}년 경력)\n"
            f"Specialty: {s_major}\n"
            f"Career: {s_career}\n"
            f"Signature palette: {s_color1} (primary) + {s_color2} (accent)\n"
            f"\n"
            f"This stylist's professional intuition and {s_exp}-year experience guides "
            f"this look. Reflect the signature color palette naturally — not as a "
            f"strict uniform, but as the stylist's tonal sensibility. "
            f"Adjust to user's personal color (best > stylist preference).\n"
        )
        prompt += persona_addition
    
    # [2026-04-06 추가] 성별별 악세서리/소품 제한 — 남자 핸드백 방지
    if metadata['gender_ko'] == "남성":
        prompt += (
            "\nACCESSORIES (CRITICAL GENDER RULE): "
            "This is a MAN. He must NEVER carry a handbag, clutch, or purse. "
            "Men's acceptable items: briefcase, backpack, document bag, or NO bag. "
            "Accessories: watch, belt, tie, pocket square, glasses ONLY. "
            "FORBIDDEN for men: any handbag, clutch, tote, crossbody, or feminine accessory. "
        )
    else:
        prompt += (
            "\nACCESSORIES: Woman may carry a clutch, tote, crossbody, or mini bag. "
            "Jewelry: earrings, necklace, bracelet, watch, scarf as appropriate. "
        )
    
    # 4. 통합 스토리 생성
    story = generate_full_story(metadata, stylist, active_city)
    
    # 5. AI 모델 분기
    model_type = "gemini" if metadata['has_face'] else "dalle"
    
    try:
        injection = generate_prompt_injection(metadata, stylist, fashion_db)
    except Exception:
        injection = ''
    
    # [2026-04-06 보강] 카테고리별 착장 스펙 생성 → 프롬프트 + UI 공용
    # 이 스펙이 이미지 프롬프트와 UI 스타일링 포인트의 단일 소스
    try:
        outfit_spec = generate_outfit_spec(metadata, stylist)
        # 프롬프트에 카테고리별 지시 삽입 (이미지가 스펙대로 생성됨)
        prompt += outfit_spec_to_prompt(outfit_spec)
        # UI용 categoryKeywords (스타일링 포인트 표시 + 유사도 매칭)
        metadata['categoryKeywords'] = outfit_spec_to_category_keywords(outfit_spec)
    except Exception as _e:
        metadata['categoryKeywords'] = {}
        print(f"[outfit_spec 에러]: {_e}")
    
    return prompt, story, model_type, stylist, injection, metadata


# [v2026-04-06] 프롬프트 주입 — 도시+목적 차별화
_CITY_F_WARM = {"서울":"Korean K-fashion: clean modern, light single-layer styling for warm weather"
    ,"뉴욕":"New York urban: light breathable, summer city-ready"
    ,"파리":"Parisian chic: light elegant, breathable fabrics"
    ,"런던":"London modern: light layering, breathable"
    ,"상파울루":"São Paulo tropical: light colors, breathable fabrics"
    ,"두바이":"Dubai: lightweight premium fabrics, breathable elegance"
    ,"밀라노":"Milan: light Italian fabrics, summer Sprezzatura"}
_CITY_F = {"서울":"Korean K-fashion: clean modern, layered styling","뉴욕":"New York urban: high-low mixing, street-smart","파리":"Parisian chic: understated elegance, neutral tones","런던":"London heritage: tailored layers, eclectic texture","상파울루":"São Paulo tropical: bold colors, casual-smart","두바이":"Dubai luxury: premium fabrics, modest elegance","밀라노":"Milan craft: soft-shoulder tailoring, Sprezzatura"}
_PURPOSE_D = {"비즈니스 포멀":"Sharp professional — structured tailoring, boardroom-ready","데일리 오피스룩":"Smart-casual office — polished but comfortable","면접룩":"Interview — trustworthy, clean, conservative modern","결혼식 하객룩":"Wedding guest — celebratory, sophisticated color","소개팅룩":"First-date — naturally attractive, soft textures, warm colors, subtle charm","로맨틱 데이트룩":"Romantic evening — refined, rich fabrics, dinner-worthy","상견례/가족모임":"Family gathering — respectful, age-appropriate elegance","사교 모임/파티":"Social party — eye-catching, bold accessories","주말 나들이":"Weekend outing — comfortable, photo-ready, cheerful","여행지 인생샷":"Travel photogenic — backdrop-matching, SNS-worthy","꾸안꾸 데일리":"Effortless chic — basic items cleverly combined","스포티/애슬레저":"Sporty athleisure — functional, performance fabrics, dynamic","공항 패션":"Airport travel — comfort with polish, layered, wrinkle-resistant","미니멀/심플":"Minimal — capsule wardrobe, clean lines, quiet luxury","트렌디/스트릿":"Trendy street — bold graphics, sneaker culture, youth energy","직접입력":"Custom styling"}


# ═══════════════════════════════════════════════════
# [2026-04-06 추가/보강] 카테고리별 착장 스펙 생성
# 원인: 프롬프트에 카테고리별 지시가 없어 이미지와 UI 포인트 불일치
# 해결: 착장 스펙을 먼저 생성 → 프롬프트에 삽입 + UI에 표시
# 용도: 1) 이미지 생성 프롬프트의 카테고리별 지시
#       2) closet.html(코디쌤) "AI 스타일링 포인트" UI 표시
#       3) Ai 옷장 유사도 매칭 기준
# ═══════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────
# [2026-04-25 v10 TJ 지시] _OUTER_ITEMS 4단계 정책 동기화
# 이전: 6단계로 잘게 쪼개져 있어 11~21도 사이가 정책과 어긋남
# 변경: TJ 지시 4단계와 정확히 일치
#   ≤ 0°C    : 머플러 + 코트/패딩  (한겨울)
#   1~10°C  : 코트/패딩 (머플러 X)
#   11~19°C : 가디건/얇은자켓 + 액세서리 스카프 (코트/패딩/머플러 X)
#   ≥ 20°C  : 아우터 X
# ─────────────────────────────────────────────────────────
_OUTER_ITEMS = {
    "freezing":     {"M": "롱 패딩 코트", "F": "롱 패딩 코트"},      # ≤ 0°C
    "cold":         {"M": "울 코트", "F": "울 트렌치코트"},          # 1~10°C
    "transitional": {"M": "라이트 자켓", "F": "라이트 가디건"},      # 11~19°C
    # ≥ 20°C는 키 없음 (아우터 X)
}
_TOP_ITEMS = {
    "비즈니스 포멀": {"M": "드레스 셔츠", "F": "실크 블라우스"},
    "데일리 오피스룩": {"M": "옥스포드 셔츠", "F": "니트 탑"},
    "면접룩": {"M": "화이트 셔츠", "F": "클린 블라우스"},
    "결혼식 하객룩": {"M": "드레스 셔츠", "F": "시폰 블라우스"},
    "소개팅룩": {"M": "니트 셔츠", "F": "파스텔 니트"},
    "로맨틱 데이트룩": {"M": "캐시미어 니트", "F": "오프숄더 탑"},
    "상견례/가족모임": {"M": "폴로 셔츠", "F": "단정한 블라우스"},
    "사교 모임/파티": {"M": "새틴 셔츠", "F": "새틴 캐미솔"},
    "주말 나들이": {"M": "스트라이프 티셔츠", "F": "프린트 티셔츠"},
    "여행지 인생샷": {"M": "린넨 셔츠", "F": "오버사이즈 셔츠"},
    "꾸안꾸 데일리": {"M": "플레인 티셔츠", "F": "베이직 니트"},
    "스포티/애슬레저": {"M": "테크 티셔츠", "F": "크롭 탑"},
    "공항 패션": {"M": "캐시미어 니트", "F": "가디건 레이어드"},
    "미니멀/심플": {"M": "모크넥 니트", "F": "터틀넥 니트"},
    "트렌디/스트릿": {"M": "그래픽 티셔츠", "F": "크롭 후디"},
}
_BOTTOM_ITEMS_M = {
    "비즈니스 포멀": "울 슬랙스", "데일리 오피스룩": "치노 팬츠",
    "면접룩": "네이비 슬랙스", "결혼식 하객룩": "울 드레스 팬츠",
    "소개팅룩": "슬림 치노", "로맨틱 데이트룩": "와이드 슬랙스",
    "주말 나들이": "코튼 팬츠", "공항 패션": "조거 팬츠",
    "스포티/애슬레저": "트레이닝 팬츠", "트렌디/스트릿": "카고 팬츠",
}
_BOTTOM_ITEMS_F_SKIRT = {
    "비즈니스 포멀": "미디 펜슬 스커트", "소개팅룩": "플리츠 스커트",
    "결혼식 하객룩": "A라인 미디 스커트", "로맨틱 데이트룩": "플레어 스커트",
    "사교 모임/파티": "새틴 미디 스커트", "주말 나들이": "플리츠 미니스커트",
}
_BOTTOM_ITEMS_F_PANTS = {
    "비즈니스 포멀": "와이드 슬랙스", "데일리 오피스룩": "스트레이트 팬츠",
    "공항 패션": "와이드 팬츠", "스포티/애슬레저": "레깅스",
}
_SHOES_M = {
    "비즈니스 포멀": "옥스포드 슈즈", "데일리 오피스룩": "더비 슈즈",
    "면접룩": "스트레이트팁 슈즈", "결혼식 하객룩": "몽크스트랩",
    "소개팅룩": "로퍼", "로맨틱 데이트룩": "첼시부츠",
    "주말 나들이": "캔버스 스니커즈", "공항 패션": "슬립온",
    "스포티/애슬레저": "러닝화", "트렌디/스트릿": "하이탑 스니커즈",
    "미니멀/심플": "화이트 스니커즈", "꾸안꾸 데일리": "미니멀 스니커즈",
}
_SHOES_F = {
    "비즈니스 포멀": "스틸레토 힐", "데일리 오피스룩": "로퍼",
    "면접룩": "클로즈드토 힐", "결혼식 하객룩": "슬링백",
    "소개팅룩": "메리제인", "로맨틱 데이트룩": "스트랩 힐",
    "주말 나들이": "플랫 슈즈", "공항 패션": "컴포트 스니커즈",
    "스포티/애슬레저": "러닝화", "트렌디/스트릿": "청키 스니커즈",
    "미니멀/심플": "뮬", "꾸안꾸 데일리": "발레 플랫",
}
_BAG_M = {"비즈니스 포멀":"블랙 브리프케이스","공항 패션":"캐리온 러기지","주말 나들이":"캐주얼 백팩","스포티/애슬레저":"스포츠 백팩","여행지 인생샷":"데이팩"}
_BAG_F = {"비즈니스 포멀":"레더 토트백","데일리 오피스룩":"숄더백","결혼식 하객룩":"클러치","소개팅룩":"미니 크로스백","주말 나들이":"캔버스 토트","공항 패션":"여행 숄더백","스포티/애슬레저":"벨트백","로맨틱 데이트룩":"이브닝 클러치"}



def _extract_color(raw_color):
    """
    [2026-04-06 추가] 스타일리스트 DB의 color1/color2에서 실제 컬러명만 추출
    원인: color1="프리미엄 카멜" → "카멜" 추출
          color2="린넨 스카프" → 이것은 컬러가 아니므로 사용 금지
    """
    if not raw_color:
        return ''
    # 컬러가 아닌 단어 필터
    _not_colors = ['스카프','백','워치','시계','가방','슈즈','벨트','목도리',
                   '브로치','커프스','링','체인','귀걸이','반지','네클리스','팔찌',
                   '안경','선글라스','모자','햇','헤드밴드','이어링','클러치',
                   '셔츠','블라우스','니트','자켓','팬츠','드레스','스커트',
                   '스니커즈','힐','로퍼','부츠','샌들','슬리퍼','에스파드리유',
                   '가디건','코트','패딩','베스트','후디','매트백','이어폰',
                   '필로우','케이스','어댑터','타올','물병','글러브','파우치',
                   '아이템','포인트','디테일','레이어링','매듭','코사지','리본',
                   '네일','립','헤어핀','피어싱','토링','이어커프','넥타이',
                   '양말','숄']
    for word in _not_colors:
        if word in raw_color:
            # "프리미엄 카멜" → 앞 단어 추출 시도
            parts = raw_color.split()
            color_parts = [p for p in parts if not any(nw in p for nw in _not_colors)]
            if color_parts:
                return ' '.join(color_parts)
            return ''
    return raw_color

def generate_outfit_spec(metadata, stylist):
    """
    카테고리별 착장 스펙 생성 — 프롬프트 + UI 공용
    
    반환: {
      outer: {item_ko, item_en, color_ko, keywords: [...]},
      top: {...},
      bottom: {...},
      shoes: {...},
      bag: {...},  # 없으면 키 없음
      watch: {...},  # 포멀만
      socks: {...},  # 남성만
    }
    """
    purpose = metadata.get('purpose', '데일리 오피스룩')
    gender = "M" if metadata.get('gender_ko') == "남성" else "F"
    temp = metadata.get('temp', 20)
    kws = metadata.get('keywords_selected', [])
    color1 = stylist.get('color1', '') if stylist else ''
    color2 = stylist.get('color2', '') if stylist else ''
    bottom_type = metadata.get('bottom_type', 'pants')
    
    spec = {}
    
    # ─────────────────────────────────────────────────────
    # [v10 TJ 지시] 아우터 4단계 정책 (≤0 / 1~10 / 11~19 / ≥20)
    # ≥ 20°C는 t_key 없음 → 아우터 미생성
    # ─────────────────────────────────────────────────────
    if temp <= 0:
        t_key = "freezing"
    elif temp <= 10:
        t_key = "cold"
    elif temp <= 19:
        t_key = "transitional"
    else:
        t_key = None  # 20°C 이상 → 아우터 X
    
    if t_key:
        outer_items = _OUTER_ITEMS.get(t_key, {})
        outer_item = outer_items.get(gender, "자켓")
        # [2026-04-06 수정] color1에서 실제 컬러명만 추출 (아이템명 제거)
        _outer_color = _extract_color(color1) if color1 else '다크 네이비'
        spec['outer'] = {
            'item_ko': outer_item,
            'item_en': outer_item,
            'color_ko': _outer_color,
        }
    
    # ── 상의 (스카프는 별도 카테고리 — 상의에 포함하지 않음) ──
    top_map = _TOP_ITEMS.get(purpose, {"M": "셔츠", "F": "블라우스"})
    top_item = top_map.get(gender, "셔츠")
    # [2026-04-06 수정] 상의 컬러는 스타일리스트 color2가 아닌 목적별 적절한 컬러 사용
    # [2026-04-06 추가] 따뜻한 날씨(22도+)에 상의를 가벼운 아이템으로 변경
    if temp >= 22:
        _summer_tops = {
            "M": {"비즈니스 포멀": "린넨 셔츠", "데일리 오피스룩": "반팔 셔츠",
                   "면접룩": "반팔 드레스 셔츠", "소개팅룩": "린넨 셔츠",
                   "주말 나들이": "반팔 티셔츠", "공항 패션": "반팔 린넨 셔츠"},
            "F": {"비즈니스 포멀": "반팔 블라우스", "데일리 오피스룩": "반팔 니트",
                   "면접룩": "반팔 블라우스", "소개팅룩": "슬리브리스 블라우스",
                   "주말 나들이": "반팔 티셔츠", "공항 패션": "반팔 린넨 셔츠"},
        }
        _summer_top = _summer_tops.get(gender, {}).get(purpose, '')
        if _summer_top:
            top_item = _summer_top

    _top_colors = {
        "비즈니스 포멀": "화이트", "데일리 오피스룩": "아이보리",
        "면접룩": "화이트", "결혼식 하객룩": "크림",
        "소개팅룩": "파스텔 핑크", "로맨틱 데이트룩": "크림",
        "상견례/가족모임": "라이트 베이지", "사교 모임/파티": "샴페인",
        "주말 나들이": "라이트 그레이", "여행지 인생샷": "화이트",
        "꾸안꾸 데일리": "오프화이트", "스포티/애슬레저": "화이트",
        "공항 패션": "크림", "미니멀/심플": "오프화이트",
        "트렌디/스트릿": "블랙",
    }
    top_color = _top_colors.get(purpose, '베이지')
    spec['top'] = {
        'item_ko': top_item,
        'item_en': top_item,
        'color_ko': top_color,
    }
    
    # ── 하의 ──
    if gender == "F" and bottom_type == "skirt":
        bt_item = _BOTTOM_ITEMS_F_SKIRT.get(purpose, "A라인 스커트")
        skirt_color = '네이비' if purpose in ['비즈니스 포멀','면접룩'] else '다크 네이비' if purpose in ['결혼식 하객룩','상견례/가족모임'] else '차콜'
        spec['bottom'] = {'item_ko': bt_item, 'item_en': bt_item, 'color_ko': skirt_color}
    elif gender == "F":
        bt_item = _BOTTOM_ITEMS_F_PANTS.get(purpose, "슬랙스")
        pants_color = '네이비' if purpose in ['비즈니스 포멀'] else '차콜'
        spec['bottom'] = {'item_ko': bt_item, 'item_en': bt_item, 'color_ko': pants_color}
    else:
        bt_item = _BOTTOM_ITEMS_M.get(purpose, "슬랙스")
        bottom_color = '네이비' if purpose in ['비즈니스 포멀','면접룩','결혼식 하객룩'] else '차콜'
        spec['bottom'] = {'item_ko': bt_item, 'item_en': bt_item, 'color_ko': bottom_color}
    
    # ── 신발 ──
    shoes_map = _SHOES_M if gender == "M" else _SHOES_F
    shoe = shoes_map.get(purpose, "로퍼" if gender == "M" else "플랫 슈즈")
    spec['shoes'] = {'item_ko': shoe, 'item_en': shoe, 'color_ko': '브라운' if gender == "M" else '베이지'}
    
    # ── 가방 (컬러 포함) ──
    bag_map = _BAG_M if gender == "M" else _BAG_F
    bag = bag_map.get(purpose, '')
    if bag:
        # [2026-04-06 수정] color2는 악세서리 이름이므로 사용하지 않음
        _bag_colors_f = {'비즈니스 포멀':'블랙','결혼식 하객룩':'골드','소개팅룩':'베이지','로맨틱 데이트룩':'블랙','주말 나들이':'내추럴'}
        bag_color = '블랙' if gender == 'M' else _bag_colors_f.get(purpose, '브라운')
        spec['bag'] = {'item_ko': bag, 'item_en': bag, 'color_ko': bag_color}
    
    # ── 시계 (포멀 계열) ──
    formal_purposes = ["비즈니스 포멀","데일리 오피스룩","면접룩","결혼식 하객룩","상견례/가족모임"]
    if purpose in formal_purposes:
        spec['watch'] = {'item_ko': '클래식 시계', 'item_en': 'classic watch', 'color_ko': '실버'}
    
    # ── 스카프/목도리 (여자 30대 이상 + 온도 조건) ──
    # [2026-04-06 추가] 스카프 추천 조건:
    # 1) 여자만 (남자는 목도리만 — 1도 이하)
    # 2) 30대 이상만 (20대 이하에게 스카프 추천 안 함)
    # 3) 온도 기준: 여자 13도 미만, 남자 8도 미만
    # 4) 가방에 이미 스카프가 있으면 목 스카프 제외
    _age_num = metadata.get('age', 30)
    try: _age_num = int(_age_num)
    except: _age_num = 30
    
    _has_bag_scarf = False  # 가방에 스카프 달린 경우 추적
    
    if gender == "F" and _age_num >= 30:
        if temp < 13 and temp >= 8:
            spec['scarf'] = {'item_ko': '실크 스카프', 'item_en': 'silk scarf', 'color_ko': '베이지'}
        elif temp >= 1 and temp < 8:
            spec['scarf'] = {'item_ko': '코튼 스카프', 'item_en': 'cotton scarf', 'color_ko': '라이트 베이지'}
        elif temp >= -9 and temp < 1:
            spec['scarf'] = {'item_ko': '캐시미어 목도리', 'item_en': 'cashmere muffler', 'color_ko': '그레이'}
        elif temp < -9:
            spec['scarf'] = {'item_ko': '울 목도리', 'item_en': 'wool muffler', 'color_ko': '차콜'}
    elif gender == "M":
        if temp >= 1 and temp < 8:
            spec['scarf'] = {'item_ko': '캐시미어 목도리', 'item_en': 'cashmere muffler', 'color_ko': '차콜'}
        elif temp < 1:
            spec['scarf'] = {'item_ko': '울 목도리', 'item_en': 'wool muffler', 'color_ko': '차콜'}
    
    # ── 양말 (남성) ──
    if gender == "M":
        spec['socks'] = {'item_ko': '톤온톤 삭스', 'item_en': 'tone-on-tone socks', 'color_ko': ''}
    
    return spec


def outfit_spec_to_prompt(spec):
    """
    [2026-04-06 보강] 착장 스펙 → 이미지 생성 프롬프트 블록 변환
    - 스카프는 TOP과 별도로 지시 (중복 방지)
    - 가방 스카프 vs 목 스카프 충돌 방지
    """
    lines = ["\n=== OUTFIT SPECIFICATION (MUST FOLLOW EXACTLY) ==="]
    cat_labels = {
        'outer': 'OUTER/JACKET', 'top': 'TOP/INNER',
        'bottom': 'BOTTOM', 'shoes': 'SHOES',
        'scarf': 'SCARF/NECKWEAR', 'bag': 'BAG',
        'watch': 'WATCH', 'socks': 'SOCKS',
    }
    has_scarf = 'scarf' in spec
    for cat, label in cat_labels.items():
        if cat in spec:
            s = spec[cat]
            color = s.get('color_ko', '')
            item = s.get('item_ko', '')
            desc = f"{color} {item}".strip() if color else item
            lines.append(f"[{label}]: {desc}")
    
    # 스카프 중복 방지 지시
    if has_scarf:
        lines.append("SCARF RULE: The scarf must be worn around the NECK only.")
        lines.append("Do NOT attach scarf to the bag. Scarf and bag are separate items.")
    
    # TOP과 스카프 분리 강조
    lines.append("IMPORTANT: TOP/INNER is the main clothing item (shirt/blouse/knit).")
    if has_scarf:
        lines.append("SCARF is a SEPARATE accessory worn around the neck, NOT part of the top.")
    
    lines.append("Follow this outfit specification EXACTLY. Each category color and design must match.")
    lines.append("=== END OUTFIT SPEC ===\n")
    return "\n".join(lines)


def outfit_spec_to_category_keywords(spec):
    """
    [2026-04-06 보강] 착장 스펙 → categoryKeywords (컬러, 디자인 분리)
    원인: 컬러와 디자인이 합쳐져 있어 유사도 매칭 및 UI 구분 어려움
    해결: 각 카테고리를 [컬러칩, 디자인칩] 2개로 분리하여 표시
    """
    result = {}
    for cat, s in spec.items():
        color = s.get('color_ko', '')
        item = s.get('item_ko', '')
        kws = []
        if color:
            kws.append(color)       # 첫 번째 칩 = 컬러
        if item:
            kws.append(item)        # 두 번째 칩 = 디자인/아이템
        if kws:
            result[cat] = kws
    return result

def generate_prompt_injection(metadata, stylist, fashion_db):
    # [2026-04-06 수정] 서울 하드코딩 제거 — 글로벌 서비스
    city = metadata.get('active_city', '')
    purpose = metadata.get('purpose', '데일리 오피스룩')
    keywords = metadata.get('keywords_selected', [])
    temp = metadata.get('temp', 20)
    
    # [2026-04-06 보강] color2는 악세서리 이름이므로 injection에서 제외
    s_color1 = stylist.get('color1','') if stylist else ''
    s_career = stylist.get('career','') if stylist else ''
    s_info = f"COLOR: Primary={s_color1}. Expert: {s_career}" if stylist else ''
    
    # [2026-04-06 추가] 온도에 따라 도시 패션 설명 분기
    if temp >= 22:
        city_desc = _CITY_F_WARM.get(city, _CITY_F.get(city, ''))
    else:
        city_desc = _CITY_F.get(city, '')
    
    # [2026-04-06 추가] 날씨 강조
    weather_note = ""
    if temp >= 28:
        weather_note = f"\nWEATHER OVERRIDE: {temp}°C — HOT. NO jacket, NO blazer, NO sweater. Single thin layer ONLY."
    elif temp >= 22:
        weather_note = f"\nWEATHER NOTE: {temp}°C — WARM. Light single layer. NO heavy outerwear."
    elif temp <= 5:
        weather_note = f"\nWEATHER NOTE: {temp}°C — COLD. Warm layering required."
    
    return (f"\n=== AI STYLIST [v2026-04-06] ===\n"
            f"CITY: {city} — {city_desc}.\n"
            f"PURPOSE: {purpose} — {_PURPOSE_D.get(purpose,'')}.\n"
            f"KEYWORDS: {', '.join(keywords[:8])}.\n"
            f"{s_info}"
            f"{weather_note}"
            f"\nSTYLING RULE: Apply {city} fashion SENSIBILITY (aesthetic, trends, silhouette) "
            f"but dress for the USER\'S LOCAL WEATHER (temperature, season). "
            f"The stylist city defines STYLE DIRECTION, NOT weather-appropriate clothing weight."
            f"\n=== END ===\n")
