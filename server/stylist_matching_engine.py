# -*- coding: utf-8 -*-
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

import json, random, hashlib, math
from datetime import date

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
    # 중동
    "middle east": "중동",
    "dubai": "중동", "abu dhabi": "중동", "uae": "중동", "riyadh": "중동",
    "saudi": "중동", "doha": "중동", "qatar": "중동", "bahrain": "중동",
    "kuwait": "중동", "oman": "중동", "istanbul": "중동", "turkey": "중동",
    "cairo": "중동", "egypt": "중동", "iran": "중동", "tehran": "중동",
    "israel": "중동", "tel aviv": "중동", "jordan": "중동", "lebanon": "중동",
    # 아프리카
    "africa": "아프리카",
    "cape town": "아프리카", "south africa": "아프리카", "johannesburg": "아프리카",
    "nairobi": "아프리카", "kenya": "아프리카", "lagos": "아프리카", "nigeria": "아프리카",
    "casablanca": "아프리카", "morocco": "아프리카",
    # 북미
    "north america": "북미",
    "new york": "북미", "los angeles": "북미", "chicago": "북미", "usa": "북미",
    "san francisco": "북미", "miami": "북미", "seattle": "북미", "boston": "북미",
    "washington": "북미", "houston": "북미", "toronto": "북미", "canada": "북미",
    "vancouver": "북미", "las vegas": "북미",
    # 남미
    "south america": "남미",
    "são paulo": "남미", "sao paulo": "남미", "rio": "남미", "brazil": "남미",
    "buenos aires": "남미", "argentina": "남미", "lima": "남미", "peru": "남미",
    "bogota": "남미", "colombia": "남미", "santiago": "남미", "chile": "남미",
    "mexico city": "남미", "mexico": "남미",
    # 오세아니아
    "oceania": "오세아니아",
    "sydney": "오세아니아", "melbourne": "오세아니아", "australia": "오세아니아",
    "auckland": "오세아니아", "new zealand": "오세아니아",
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
# 3. 여성 치마/바지 로테이션 — seed 기반 (다시코디마다 교차)
# ═══════════════════════════════════════════════════
def get_bottom_type_for_women(seed=0):
    """
    여성 하의 타입: 치마 우선, 다시코디마다 교차
    seed 0(첫 요청) = 치마
    seed 1(다시코디 1회) = 바지
    seed 2(다시코디 2회) = 치마
    ...짝수 = 치마, 홀수 = 바지
    """
    return "skirt" if (int(seed) % 2 == 0) else "pants"


def get_skirt_length_by_body(height_cm, weight_kg, bmi_category):
    """BMI + 키 기반 치마 길이 & 스타일 추천"""
    h = int(height_cm or 163)
    
    if bmi_category == "underweight":
        # 마른 체형: 볼륨 추가 — A라인, 플리츠
        if h >= 168:
            return "midi-length A-line or pleated skirt (below knee), adds volume and femininity"
        else:
            return "knee-length A-line or flared skirt, creates balanced silhouette for petite slim frame"
    
    elif bmi_category == "normal":
        # 표준 체형: 다양한 스타일 가능
        if h >= 168:
            return "midi pencil skirt or knee-length A-line, shows off balanced proportions elegantly"
        else:
            return "knee-length pencil or A-line skirt, elongates legs for standard petite build"
    
    elif bmi_category == "overweight":
        # 약간 통통: A라인, 랩스커트로 곡선 커버
        if h >= 168:
            return "midi wrap skirt or below-knee A-line, flattering drape for curvy tall figure"
        else:
            return "knee-length A-line or wrap skirt, slimming effect for curvy petite frame"
    
    elif bmi_category in ("obese1", "obese2"):
        # 과체중/비만: 편안한 A라인, 하이웨이스트
        if h >= 168:
            return "midi to long A-line skirt with high waist, flowy fabric for comfortable tall plus-size fit"
        else:
            return "knee-to-midi A-line skirt with high waist and stretch, comfortable coverage for petite plus-size"
    
    # fallback
    return "knee-length A-line skirt, universally flattering"


# ═══════════════════════════════════════════════════
# 4. 키워드 랜덤 선택 — seed 기반 (다시코디마다 다른 키워드)
# ═══════════════════════════════════════════════════
def select_daily_keywords(keywords_str, user_id, purpose, count=8, retry_seed=0):
    """
    키워드 문자열에서 랜덤 선택
    retry_seed가 바뀌면(다시코디) 다른 키워드 조합이 선택됨
    """
    if not keywords_str:
        return []
    
    # 키워드 파싱: "테일러드(Tailored), 네이비(Navy), ..." 형태
    keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
    
    today = date.today().isoformat()
    seed_str = f"{user_id}_{purpose}_{today}_{retry_seed}_keywords"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    
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
    # ── 사용자 프로필 추출 (closet.html: 'user', codistyle: 'user') ──
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
    
    # ── 코디 목적 (closet: purposeKey/purposeLabel, 기본: purpose) ──
    purpose = payload.get('purpose', '')
    if not purpose:
        pk = str(payload.get('purposeKey', '')).strip()
        pl = str(payload.get('purposeLabel', '')).strip()
        purpose = pl or pk or '데일리 오피스룩'
    purpose_info = fashion_db.get('base_prompts', {}).get(purpose, {})
    purpose_en = purpose_info.get('en', purpose)
    purpose_prompt_en = purpose_info.get('prompt_en', '')
    
    # ── 지역 → main/sub 도시 ──
    main_city, sub_city, region = get_main_sub_cities(user_location)
    
    # ── seed (다시코디 횟수) — 프론트에서 전달 ──
    retry_seed = int(payload.get('seed', 0))
    
    # ── main/sub 교차: seed 기반 (다시코디마다 교차) ──
    # seed 0(첫요청) = main, seed 1(다시코디) = sub, seed 2 = main, ...
    if retry_seed % 2 == 0:
        active_city = main_city
    else:
        active_city = sub_city
    
    # ── 성별에 따른 키워드 선택 ──
    city_kw = fashion_db.get('city_keywords', {}).get(active_city, {}).get(purpose, {})
    kw_key = "women" if gender_ko == "여성" else "men"
    keywords_str = city_kw.get(kw_key, '')
    
    user_id = str(profile.get('id', 'default'))
    selected_keywords = select_daily_keywords(keywords_str, user_id, purpose, count=8, retry_seed=retry_seed)
    
    # ── 온도 버킷 ──
    temp_bucket = _get_temp_bucket(temp)
    
    # ── 여성 하의 타입 결정 (seed 기반: 짝수=치마, 홀수=바지) ──
    bottom_type = "pants"  # 남성 기본값
    if gender_ko == "여성":
        bottom_type = get_bottom_type_for_women(retry_seed)
        if bottom_type == "skirt":
            skirt_guide = get_skirt_length_by_body(height, weight, bmi_info['category'])
            bottom_instruction = (
                f"BOTTOM (CRITICAL): The woman MUST wear a SKIRT (NOT pants, NOT trousers). "
                f"Skirt style and length: {skirt_guide}. "
                f"Height {height}cm considered for proportional skirt length. "
            )
        else:
            bottom_instruction = (
                "BOTTOM: The woman wears well-fitted trousers or slacks. "
                "Full ankle-length — FORBIDDEN: cropped, 7/8, calf-length. "
            )
    else:
        bottom_instruction = (
            "BOTTOM: The man wears well-fitted trousers or slacks. "
            "Full ankle-length — FORBIDDEN: cropped, 7/8, calf-length. "
        )
    
    # ── 얼굴 사진 여부 ──
    has_face = bool(payload.get('face_image'))
    face_instruction = ""
    if has_face:
        face_instruction = (
            "FACE (CRITICAL): A face reference photo is provided. "
            "You MUST preserve the EXACT facial identity, features, skin tone, and expression. "
            "The generated image must look like the same person in the reference photo. "
        )
    
    # ═══ 최종 프롬프트 조립 ═══
    prompt = (
        f"Create a photorealistic full-body fashion styling lookbook photo. "
        f"Subject: {gender_en}, age {age}, height {height}cm, weight {weight}kg. "
        f"Body type: {bmi_info['prompt']}. "
        f"\n\n"
        f"{face_instruction}"
        f"\n"
        f"PURPOSE: {purpose_en}. "
        f"{purpose_prompt_en} "
        f"\n\n"
        f"STYLING KEYWORDS (from {active_city} fashion): {', '.join(selected_keywords)}. "
        f"\n\n"
        f"{bottom_instruction}"
        f"\n"
        f"WEATHER: {temp}°C, {condition}. Outfit guide: {temp_bucket}. "
        f"\n\n"
        # ── 금지 항목 (CRITICAL) ──
        f"=== ABSOLUTE RULES (VIOLATION = GENERATION FAILURE) ===\n"
        f"BODY PROPORTION (CRITICAL): Upper body (head to waist) MUST be 40% or LESS. "
        f"Lower body (waist to feet) MUST be 60% or MORE. 3:7 ratio is MANDATORY. "
        f"5:5 or 4:6 ratio = GENERATION FAILURE.\n"
        f"SOCKS: Both feet MUST wear IDENTICAL socks — same color, same pattern. "
        f"Mismatched socks = STRICTLY FORBIDDEN.\n"
        f"STYLIST RULE: ONLY real-life wearable daily outfits. "
        f"FORBIDDEN: runway, fashion-show, avant-garde, asymmetric, experimental styling.\n"
        f"BACKGROUND (ABSOLUTE): Single SOLID FLAT PASTEL COLOR that CONTRASTS with outfit. "
        f"Studio paper backdrop ONLY — NO environment, NO objects, NO props.\n"
        f"NO text, NO watermark, NO logo, NO brand names visible.\n"
        f"=== END RULES ===\n"
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
        "keywords_selected": selected_keywords,
        "bottom_type": "skirt" if (gender_ko == "여성" and bottom_type == "skirt") else "pants" if gender_ko == "여성" else "pants",
        "temp": temp,
        "condition": condition,
        "has_face": has_face,
        "user_location": user_location,
    }
    
    return prompt, metadata


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
            "normal": "슬림핏과 레귤러핏을 적절히 믹스한 밸런스 좋은 실루엣입니다",
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
    도시 → 코디목적 → 성별 풀에서 스타일리스트 선정
    retry_seed가 바뀌면(다시코디) 다른 스타일리스트가 선정됨
    """
    gender_key = "women" if user_gender == "여성" else "men"
    
    city_data = stylist_db.get(city, {})
    purpose_data = city_data.get(purpose, {})
    pool = purpose_data.get(gender_key, [])
    
    if not pool:
        for fallback_purpose in [purpose, "직접입력", "데일리 오피스룩"]:
            pool = city_data.get(fallback_purpose, {}).get(gender_key, [])
            if pool:
                break
    
    if not pool:
        return None
    
    # 체형 매칭 우선
    if user_body_type:
        matched_pool = [s for s in pool if user_body_type in s.get("bodyType", "")]
        if matched_pool and len(matched_pool) >= 3:
            pool = matched_pool
    
    # seed 기반 선정 (다시코디마다 다른 스타일리스트)
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
    내옷장 추천코디 요청 처리 — 원스톱
    
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
    profile = payload.get('profile', {})
    if not profile:
        profile = payload.get('user', {})
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
    
    # 3. 스타일리스트 컬러를 프롬프트에 반영
    if stylist:
        color_addition = (
            f"\nSTYLIST COLOR DIRECTION: "
            f"Primary color tone: {stylist['color1']}. "
            f"Accent color: {stylist['color2']}. "
            f"Incorporate these colors naturally into the outfit coordination. "
        )
        prompt += color_addition
    
    # 4. 통합 스토리 생성
    story = generate_full_story(metadata, stylist, active_city)
    
    # 5. AI 모델 분기
    model_type = "gemini" if metadata['has_face'] else "dalle"
    
    return prompt, story, model_type, stylist
