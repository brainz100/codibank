"""
착착 코디뱅크 — mock_backend.py 글로벌 패치 v2.1
=================================================

핵심 원칙:
  - 날씨/기온: 사용자의 실제 위치 기반 (프론트에서 전달)
  - 패션 힌트: 매칭된 AI 스타일리스트의 도시에서 가져옴 (6대 도시 DB)
  - 온도 버킷: 순수 기온 기반 (위치 무관)

수정 위치: build_prompt(), codistyle_generate(), _ai_styling_via_gemini()
"""


# ═══════════════════════════════════════════════
# 수정 1: 온도 버킷 — 순수 기온 기반 (위치 분기 제거)
# ═══════════════════════════════════════════════
def get_temp_bucket(temp):
    """순수 기온으로만 판단. 서울이 40도면 extreme heat, 두바이가 10도면 chilly."""
    if temp <= -10:
        return "extreme cold (heavy padded coat, thermal layers, insulated boots, warm accessories)"
    elif temp <= 0:
        return "very cold (winter coat with layers, warm knitwear, boots)"
    elif temp <= 5:
        return "cold (thick coat, sweater or fleece, closed shoes)"
    elif temp <= 10:
        return "chilly (jacket with long-sleeve shirt, light layers)"
    elif temp <= 15:
        return "cool (light jacket or cardigan, comfortable layers)"
    elif temp <= 20:
        return "mild (single outer layer optional, versatile clothing)"
    elif temp <= 25:
        return "warm (light single layer, breathable fabrics)"
    elif temp <= 30:
        return "hot (light clothing, breathable materials, sun protection)"
    elif temp <= 35:
        return "very hot (minimal layers, UV protection, light colors)"
    else:
        return "extreme heat (lightest breathable fabrics, full sun protection essential)"


# ═══════════════════════════════════════════════
# 수정 2: 사용자 위치 처리 (하드코딩 제거)
# ═══════════════════════════════════════════════
def get_user_location(weather_data):
    """
    프론트엔드가 전달한 사용자의 실제 위치를 추출.
    '서울' 하드코딩 완전 제거 — 위치 모르면 빈 문자열.
    """
    location = str(weather_data.get('location') or '').strip()
    if not location:
        location = str(weather_data.get('city') or '').strip()
    return location  # 비어있을 수 있음 — OK


# ═══════════════════════════════════════════════
# 수정 3: 패션 문화 힌트 — 스타일리스트 도시 기반
#          (사용자 위치가 아닌, 매칭된 스타일리스트 풀의 도시)
# ═══════════════════════════════════════════════
STYLIST_CITY_HINTS = {
    "서울": "Korean fashion: K-fashion trends, clean silhouettes, layered styling, color coordination, modern minimalist aesthetic. ",
    "뉴욕": "New York fashion: urban versatile style, mixing high-low brands, practical for active city life, street-smart. ",
    "파리": "Parisian fashion: effortless chic, understated elegance, neutral tones with subtle accent, quality over quantity. ",
    "런던": "London fashion: heritage tailoring meets modern street, eclectic layering, weather-adaptive style. ",
    "상파울루": "São Paulo fashion: vibrant tropical influence, bold colors, mix of casual and smart, cultural diversity in style. ",
    "두바이": "Dubai fashion: smart luxury, modest yet elegant options, lightweight premium fabrics, international cosmopolitan mix. ",
}

def get_stylist_fashion_hint(stylist_city):
    """
    매칭된 AI 스타일리스트의 도시에서 패션 문화 힌트를 가져온다.
    사용자 위치가 아닌, 스타일리스트 DB의 도시 기준.
    
    사용 예:
      stylist = matched_stylist  # 코디뱅크 DB에서 매칭된 스타일리스트
      hint = get_stylist_fashion_hint(stylist.get('city', '서울'))
    """
    return STYLIST_CITY_HINTS.get(stylist_city, "")


# ═══════════════════════════════════════════════
# 적용 가이드: build_prompt() 수정
# ═══════════════════════════════════════════════
APPLY_GUIDE_BUILD_PROMPT = """
[기존 코드 — build_prompt() 내]
    location = str(weather.get('location') or '').strip() or 'Seoul'
    ...
    f"Location culture hint: {location}. "

[수정 코드]
    # 사용자의 실제 위치 (날씨용)
    user_location = get_user_location(weather)
    
    # 기온 버킷 (순수 기온 기반)
    temp_num = weather.get('temp', 20)
    temp_bucket = get_temp_bucket(temp_num)
    
    # 패션 힌트 (스타일리스트 도시 기반 — 향후 DB 연동 시)
    stylist_city = payload.get('stylist_city', '서울')  # 프론트에서 전달
    fashion_hint = get_stylist_fashion_hint(stylist_city)
    
    # 프롬프트에 삽입
    prompt += f"Weather at user location: {temp_num}°C, feels like {feels_like}°C. "
    prompt += f"Condition: {weather.get('condition', 'clear')}. "
    prompt += f"Outfit temperature guide: {temp_bucket}. "
    if user_location:
        prompt += f"User is in: {user_location}. "
    prompt += fashion_hint
"""


# ═══════════════════════════════════════════════
# 적용 가이드: codistyle_generate() 동일 패턴
# ═══════════════════════════════════════════════
APPLY_GUIDE_CODISTYLE = """
[기존]
    f"Location culture hint: {str(weather.get('location') or '').strip() or 'Seoul'}. "

[수정]
    user_location = get_user_location(weather)
    temp_bucket = get_temp_bucket(weather.get('temp', 20))
    stylist_city = payload.get('stylist_city', '서울')
    fashion_hint = get_stylist_fashion_hint(stylist_city)
    
    prompt += f"Weather: {weather.get('temp')}°C, {weather.get('condition')}. "
    prompt += f"Outfit guide: {temp_bucket}. "
    if user_location:
        prompt += f"User location: {user_location}. "
    prompt += fashion_hint
"""


# ═══════════════════════════════════════════════
# 적용 가이드: _ai_styling_via_gemini() 동일 패턴
# ═══════════════════════════════════════════════
APPLY_GUIDE_GEMINI = """
[수정] — 위 두 함수와 동일한 패턴 적용
"""


# ═══════════════════════════════════════════════
# 테스트
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 70)
    print("착착 코디뱅크 — 글로벌 패치 v2.1 테스트")
    print("=" * 70)
    
    print("\n▶ 온도 버킷 테스트 (순수 기온 — 위치 무관)")
    print("-" * 50)
    test_temps = [-15, -5, 3, 8, 13, 18, 23, 28, 33, 40]
    for t in test_temps:
        print(f"  {t:>4}°C → {get_temp_bucket(t)}")
    
    print("\n▶ 사용자 위치 추출 테스트 (하드코딩 없음)")
    print("-" * 50)
    test_weather = [
        {"location": "Dubai"},
        {"location": "Ho Chi Minh City"},
        {"city": "Reykjavik"},
        {},  # 위치 없음
    ]
    for w in test_weather:
        loc = get_user_location(w)
        print(f"  입력: {w} → 위치: '{loc}' (빈 문자열 OK)")
    
    print("\n▶ 스타일리스트 패션 힌트 테스트 (6대 도시 DB)")
    print("-" * 50)
    for city in ["서울", "뉴욕", "파리", "런던", "상파울루", "두바이"]:
        hint = get_stylist_fashion_hint(city)
        print(f"  {city}: {hint[:50]}...")
    
    print("\n▶ 핵심 확인: 날씨 ≠ 패션 도시")
    print("-" * 50)
    print("  사용자 위치: 베트남 호치민 (35°C)")
    print(f"  → 온도 버킷: {get_temp_bucket(35)}")
    print(f"  → 사용자 위치: {get_user_location({'location': 'Ho Chi Minh City'})}")
    print(f"  → 매칭 스타일리스트(서울풀): {get_stylist_fashion_hint('서울')[:40]}...")
    print(f"  → 매칭 스타일리스트(파리풀): {get_stylist_fashion_hint('파리')[:40]}...")
    print("  ✅ 같은 사용자 위치에서도 스타일리스트 도시에 따라 패션 힌트가 다름")
    
    print("\n" + "=" * 70)
    print("✅ 테스트 완료 — 날씨(사용자 위치) / 패션(스타일리스트 도시) 분리 확인")
