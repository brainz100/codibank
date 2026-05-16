# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════
# 📋 수정 이력 (MODIFICATION HISTORY) — 최신순
# ═══════════════════════════════════════════════════════════════════════
# 이 블록은 파일 수정 때마다 최상단에 누적됩니다.
# 각 항목은 실제 수정 지점(줄번호)에도 동일한 날짜/요약 주석이 존재합니다.
# 점검 시 이 블록만 읽어도 파일의 최신 상태와 변경 이력을 알 수 있습니다.
#
# ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.7-fix3 engine) ─── [career 통일 부작용 수정]
#   배경: stylist_db_server.json의 career 11,200개를 모두 '패션 스타일리스트'로 통일
#         (TJ 지시: 이상한 경력 표현이 부적절)
#   부작용 진단:
#     · line 558 signature_directive: career를 핵심 차별화 요소로 사용
#       → 통일 후 모두 동일한 directive 생성 ("informed by 패션 스타일리스트")
#     · line 1221 STYLIST DNA HEAD의 Career 줄: 모든 스타일리스트 동일 → 무의미
#     · 결과: 11,200명 → 디자인 카테고리 12개로 평준화 (major 다양성 미활용)
#   수정 (2곳):
#     1) line 558 signature_directive:
#        · 이전: "informed by {career or major}"
#        · 변경: "specialty in {major}" (206개 다양성 활용)
#     2) line 1221 STYLIST DNA HEAD:
#        · "Career: ..." 줄 제거
#        · major를 "SPECIALTY: ..." 로 격상 강조
#        · "this is the stylist's expert domain — outfit MUST reflect it" 명시
#   효과:
#     · 11,200명 → 206개 major별 차별화 (×17 배 증가)
#     · STYLIST DNA HEAD의 SPECIALTY가 LLM attention 최상단 영역에서 차별화 유도
#   추가 진단 (다음 턴 작업 후보):
#     · design_categories 12개 → 30~50개 세분화로 더 강한 차별화
#     · major를 한글→영문 매핑 (이미지 모델 인식률 향상)
#     · closet.html colorDirective 셀프 강화 루프 제거
#
# ─── 2026-05-12 KST · TJ 지시 (v65) ─── [Phase 1+2+4 종합 픽스 - 4 Pass 통합]
#   사용자 보고: AI 스타일리스트 매번 다른데 이미지는 거의 동일 (흰티+그레이팬츠+검정백팩)
#   Phase 1 진단 결과:
#     · 전체 prompt 10,424 chars (LLM 한계 초과 — Gemini 권장 ~5,000)
#     · STYLIST DNA가 30~46% 중간 위치 → LLM attention drop 구간 (U자형 attention)
#     · 강제 표현 56회 (FORBIDDEN/MUST/ABSOLUTE/CRITICAL 등) → 우선순위 마비
#     · Gemini 3.1 Flash Image Preview가 prompt 끝 JSON SCHEMA 무시
#       (Render 로그: "분석 JSON 마커 없음, 템플릿 폴백 사용")
#   Phase 2 진단:
#     · google-genai SDK는 seed/temperature 정상 지원 (TypeError 안 남)
#     · 그러나 image generation 모델은 seed로 큰 그림 변경 어려움
#     · 진짜 문제는 prompt 구조 (DNA 위치 + 분량)
#   Phase 4 진단:
#     · 액세서리는 클라이언트 payload에 명시 안 됨 (codiStory 화면 표시만)
#     · 검정 백팩 반복 = Gemini 학습 편향 (한국 스포티/애슬레저 default)
#     · v60 personaIdx=0 고정 잔존 버그로 codiStory에 매번 같은 가방+시계 표시
#   [Pass 1 — Prompt 재구조화: DNA를 book-end로 양쪽 배치]
#     · process_styling_request: STYLIST DNA를 prompt 끝 append → 시작 prepend로 이동
#     · 압축된 DNA HEAD 형식 (signature_directive/refinement 제거, 핵심만)
#     · mock_backend.py 끝에 DNA REMINDER 블록 추가 (matched_stylist로 design_keywords 추출)
#     · 효과: DNA가 0~7.8% + 92.9~100% 양쪽 배치 (LLM attention 최대 영역)
#   [Pass 2 — 강제 표현 정리]
#     · build_styling_prompt 끝의 ABSOLUTE RULES 블록 완전 제거 (mock_backend CORE RULES와 중복)
#     · 강제 표현 56회 → 21회 (62.5% 감소)
#   [Pass 3 — 분량 압축]
#     · 전체 prompt 10,424 → 5,978 chars (42.7% 감소)
#     · mock_backend.py 모든 블록 압축 (자세한 내용은 mock_backend.py 히스토리 참조)
#   [Pass 4 — 클라이언트 액세서리 다양화] (closet.html에서 처리)
#   [검증]
#   · py_compile 통과 (stylist_matching_engine.py + mock_backend.py)
#   · 시뮬레이션: 분량/위치/표현 모두 목표 달성
#   · 매칭 stylist DNA가 prompt 시작과 끝에 명확히 표시됨
#
# ─── 2026-05-12 KST · TJ 지시 (v63) ─── [도시 활용 7개 도시 다양화]
#   사용자 보고: AI 스타일리스트 활동 지역이 항상 '서울 활동'으로만 표시됨
#               → 11,200명 중 1/7만 활용 (도시별 ~1,600명만 사용)
#   원인: REGION_CITY_MAP이 각 지역당 main + sub 단일 도시만 매핑
#         · 아시아 사용자 → 서울/뉴욕 2개만 (파리/런던/상파울루/두바이/밀라노 미활용)
#         · build_styling_prompt: `if seed % 2: main else: sub` → 짝/홀 2개 도시만 교차
#   사용자 요구:
#     · 첫 생성 (seed=0): 사용자 메인 도시 (서울)
#     · 다시코디/다른 날짜/다른 목적 (seed>0): 6개 서브 도시 중 랜덤 선정
#   [변경]
#   1) ALL_CITIES 상수 도입 (line 96)
#      · ['서울', '뉴욕', '파리', '런던', '상파울루', '두바이', '밀라노'] (7개)
#   2) REGION_CITY_MAP 단순화 (line 88~)
#      · main만 정의, sub_cities는 ALL_CITIES에서 main 제외 6개로 자동
#   3) get_main_sub_cities() 반환값 변경 (line 247~)
#      · 이전: (main_city, single_sub_city, region)
#      · 변경: (main_city, sub_cities_list, region)
#   4) build_styling_prompt 도시 선정 로직 (line 634~)
#      · seed==0: active_city = main_city (첫 생성)
#      · seed>0:  hash(user_id + date + purpose + seed) % 6 → sub_cities 선정
#      · 같은 (user, date, purpose, seed) → 항상 같은 도시 (재현성)
#      · 다른 (user, date, purpose, seed) → 다른 도시 (다양성)
#   5) metadata 호환: "sub_city" → "sub_cities" (list)
#   [검증]
#   · 시뮬레이션: 서울 사용자 180개 조합 → 6개 서브 도시 균등 활용
#     (분포: 13.9% ~ 20.0%, 이전엔 1개 도시 100%)
#
# ─── 2026-05-12 KST · TJ 지시 (v62) ─── [9,600 차별화 실종 픽스]
#   사용자 보고: 같은 코디목적 + 다른 날짜로 추천 코디 생성 시
#                AI 스타일리스트는 변경되지만 상의/하의 컬러/디자인/패턴이 동일
#                → 11,200명 차별화가 사실상 무효
#   원인: stylist 객체의 prompt 기여가 color1/color2 hint 2개 필드뿐
#         · major/career/level/exp는 prompt에 전혀 안 들어감
#         · color1/color2도 "guide, not mandate"로 약화 → AI가 무시
#         · 결과적으로 도시/목적이 같으면 stylist 다르더라도 출력 동일
#   [변경 — Option A: stylist DNA 동적 생성]
#   1) _generate_stylist_dna() 함수 신규 추가 (line ~250)
#      · major 키워드 매칭 → 12개 design category 매핑
#        (클래식포멀/캐주얼데일리/스트릿어반/미니멀모던/럭셔리고급/
#         아트크리에이티브/스포츠액티브/트래블글로벌/파티이벤트/
#         로맨틱데이트/테크퓨처/트렌드마케팅)
#      · 각 카테고리에 design_keywords 5~6개 + silhouette_pref + color_strength
#      · level + exp → refinement modifier (Master/Senior/Expert/Mid/Junior)
#      · 시뮬레이션: 11,200명 → 60개 unique DNA 조합 (이전엔 사실상 1개)
#   2) build_styling_prompt 강화 (line ~430)
#      · 이전: color1/color2만 "guide, not mandate" 표시
#      · 변경: STYLIST DNA 블록을 PRIMARY DIRECTIVE로 명시
#        - "MUST INFLUENCE OUTFIT CHOICES"
#        - "Different stylists MUST produce noticeably different outfits"
#        - design_keywords + silhouette_pref + refinement 모두 강제 반영
#      · color_strength에 따라 color1/color2 강조 톤 분기:
#        - strong: "PROMINENTLY featured"
#        - medium: "anchor tones"
#        - light: "loose inspiration"
#   [관련 변경 — Option D: mock_backend.py Gemini API]
#   · _ai_styling_via_gemini의 GenerateContentConfig:
#     - temperature 0.7 → 0.9 (더 다양한 출력)
#     - seed 명시 추가 (payload['seed'] 기반) — graceful fallback
#   · 효과: 같은 stylist + 같은 seed → 동일 결과 (재현성)
#           다른 seed → 명확히 다른 결과 (다양성)
#
# ─── 2026-05-12 KST · TJ 지시 (v60) ─── [바지 발목 덮음 강제 + dont_style ABSOLUTE FORBIDDEN]
#   1) calculate_bmi prompt 표현 완화 (line 205)
#      · 'slim and lean build, elongated silhouette, narrow shoulders' (슬림 유도)
#      · → 'slender build, naturally lean frame' (중립 묘사)
#   2) build_styling_prompt BOTTOM 강화 (line ~409)
#      · 남녀 모두 REGULAR FIT 발목 덮음 강제
#      · 'Hem MUST FULLY COVER the ankle bone (medial/lateral malleolus)'
#      · 'slightly overlap the shoe top'
#      · slim/skinny fit FORBIDDEN (custom 입력 없는 한)
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

import json, random, hashlib, math, os, time, datetime
from datetime import date

# ═══════════════════════════════════════════════════
# 1. 지역 → main/sub 도시 매핑
# ═══════════════════════════════════════════════════
# ─── 2026-05-12 KST · TJ 지시 (v63) ─── 7개 도시 모두 활용 ───
# 배경: 이전 REGION_CITY_MAP은 main + sub 단일 도시만 매핑.
#       아시아 사용자 → 서울/뉴욕만, 파리/런던/상파울루/두바이/밀라노 stylist는
#       영원히 사용 불가. stylist_db_server.json의 11,200명 중 사실상 1/7만 활용됨.
# 변경: 7개 도시 ALL_CITIES 상수 도입.
#       REGION_CITY_MAP은 "main" 도시만 정의.
#       sub_cities는 ALL_CITIES에서 main 제외한 6개를 자동 사용.
#       get_main_sub_cities()는 (main_city, sub_cities_list, region) 반환.
ALL_CITIES = ['서울', '뉴욕', '파리', '런던', '상파울루', '두바이', '밀라노']

REGION_CITY_MAP = {
    "아시아":      {"main": "서울"},
    "유럽":        {"main": "파리"},
    "중동":        {"main": "두바이"},
    "아프리카":    {"main": "파리"},
    "북미":        {"main": "뉴욕"},
    "남미":        {"main": "상파울루"},
    "오세아니아":  {"main": "뉴욕"},
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
    """사용자 위치 → main / sub_cities list / region 결정.
    ─── 2026-05-12 KST · TJ 지시 (v63) ─── 7개 도시 모두 활용 ───
    이전: (main_city, single_sub_city, region) 반환 → 2개 도시만 사용
    변경: (main_city, sub_cities_list, region) 반환 → main 제외 6개 모두 활용
    """
    region = detect_region(user_location)
    mapping = REGION_CITY_MAP.get(region, REGION_CITY_MAP["아시아"])
    main_city = mapping["main"]
    # main 도시 제외 나머지 6개를 sub_cities로
    sub_cities = [c for c in ALL_CITIES if c != main_city]
    return main_city, sub_cities, region


# ═══════════════════════════════════════════════════
# 2. BMI & 체형 분석
# ═══════════════════════════════════════════════════
def calculate_bmi(height_cm, weight_kg):
    """BMI 계산 + 체형 분류 + 프롬프트 가이드
    ─── 2026-05-12 KST · TJ 지시 (v60) ─── 슬림 유도 표현 완화 ───
    이전: "slim and lean build, elongated silhouette, narrow shoulders" 같은 표현이
          AI에 슬림핏 + 발목 노출 바지를 유도하는 경향.
    변경: 중립적 신체 묘사만 남기고, 실루엣/핏 결정은 AI 자율에 맡김.
    """
    if not height_cm or not weight_kg or height_cm < 100:
        return {"bmi": 22, "category": "normal", "prompt": "average build, well-proportioned", "ko": "보통 체형"}
    
    h_m = height_cm / 100
    bmi = round(weight_kg / (h_m * h_m), 1)
    
    if bmi < 18.5:
        return {"bmi": bmi, "category": "underweight",
                "prompt": f"slender build (BMI {bmi}), naturally lean frame",
                "ko": "마른 체형",
                "skirt_hint": "A-line or flared skirts to add volume, midi length recommended"}
    elif bmi < 23:
        return {"bmi": bmi, "category": "normal",
                "prompt": f"average build (BMI {bmi}), well-proportioned figure",
                "ko": "표준 체형",
                "skirt_hint": "any skirt style works well, pencil or A-line, knee to midi length"}
    elif bmi < 25:
        return {"bmi": bmi, "category": "overweight",
                "prompt": f"slightly fuller build (BMI {bmi}), medium frame",
                "ko": "약간 통통한 체형",
                "skirt_hint": "A-line or wrap skirts for flattering fit, below-knee length preferred"}
    elif bmi < 30:
        return {"bmi": bmi, "category": "obese1",
                "prompt": f"fuller build (BMI {bmi}), broad frame",
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


# ═══════════════════════════════════════════════════
# 3-bis. (v62) 스타일리스트 동적 DNA 생성
#   ─── 2026-05-12 KST · TJ 지시 (v62) ─── 9,600 차별화 실종 픽스 ───
#   배경: stylist의 메타데이터(major/career/level/exp/color1/color2 등)가
#         prompt에 거의 반영 안 됨 → color1/color2 hint만 들어가서
#         11,200명 스타일리스트가 prompt에서 사실상 동일 출력.
#   해법(Option A): stylist의 major/career/level/exp/color1/color2를 조합해
#         동적 styling DNA 생성 (design_keywords 5~7개 + silhouette_pref +
#         signature_directive + color_strength + refinement).
#         build_styling_prompt에서 'STYLIST DNA' 블록으로 강제 반영.
# ═══════════════════════════════════════════════════
def _generate_stylist_dna(stylist):
    """
    stylist의 major/career/level/exp/color1/color2를 조합하여 동적 styling DNA 생성.
    11,200명 각자의 차별화를 prompt 강제 반영용 정보로 변환.
    
    Returns:
        dict {
            'design_keywords':    List[str],   # 5~6개 영문 design keyword (prompt 강제 반영)
            'silhouette_pref':    str,         # 실루엣 선호 (영문)
            'signature_directive': str,        # 한 줄 영문 directive
            'color_strength':     str,         # 'strong' | 'medium' | 'light'
            'refinement':         str,         # level/exp 기반 정제 강도
            'matched_category':   str,         # major 매칭 카테고리 (디버그용)
            'style_persona':      str,         # 디스플레이용 한 줄 페르소나
        }
    """
    major = stylist.get('major', '') if stylist else ''
    career = stylist.get('career', '') if stylist else ''
    level = stylist.get('level', '') if stylist else ''
    exp = stylist.get('exp', 0) if stylist else 0
    name = stylist.get('name', 'AI Stylist') if stylist else 'AI Stylist'
    
    # ── major 키워드 → design category 매핑 (12 카테고리, 206 major 커버) ──
    design_categories = {
        '클래식포멀': {
            'kw': ['비즈니스', '포멀', '맞춤', '테일러', '의례', '웨딩', '드레스', '브라이들',
                   '한복', '전통', '드레스디자인', '봉제기술', '남성복', '의례복'],
            'keywords': ['classic tailoring', 'refined silhouette', 'polished details',
                         'formal structure', 'sophisticated cuts', 'precise fit'],
            'silhouette': 'tailored and structured',
            'color_strength': 'strong',
        },
        '캐주얼데일리': {
            'kw': ['캐주얼', '데일리', '베이직', '일상', '컴포트', '에센셜', '유니섹스',
                   '캡슐', '놈코어', '에코디자인', '환경패션'],
            'keywords': ['relaxed comfort', 'everyday versatility', 'effortless basics',
                         'wearable mix', 'balanced proportions'],
            'silhouette': 'relaxed and easy',
            'color_strength': 'medium',
        },
        '스트릿어반': {
            'kw': ['스트릿', '스트리트', '힙합', '스니커', '서브컬처', '스케이트', '그래피티',
                   'Y2K', '팝아트', '커스텀', '인디브랜드', '데님디자인', '커뮤니티패션'],
            'keywords': ['oversized fit', 'graphic prints', 'urban edge',
                         'streetwear layering', 'bold accents', 'sneaker culture'],
            'silhouette': 'oversized and layered',
            'color_strength': 'medium',
        },
        '미니멀모던': {
            'kw': ['미니멀', '모노크롬', '바우하우스', '스칸디', '모던디자인', '제품디자인',
                   '지속가능', '제로웨이스트', '구조적', '패션철학', '에센셜디자인'],
            'keywords': ['clean lines', 'monochrome harmony', 'understated elegance',
                         'modern minimalism', 'considered restraint', 'quality fabrics'],
            'silhouette': 'clean and minimal',
            'color_strength': 'light',
        },
        '럭셔리고급': {
            'kw': ['럭셔리', '럭', '주얼', 'VIP', '향수', '비주얼머천다이징', '셀럽'],
            'keywords': ['luxurious materials', 'refined craftsmanship', 'sophisticated palette',
                         'premium textures', 'understated luxury'],
            'silhouette': 'tailored and luxurious',
            'color_strength': 'strong',
        },
        '아트크리에이티브': {
            'kw': ['아트', '일러스트', '포토', '그래픽', '타이포', '공간디자인', '순수미술',
                   '산업디자인', '건축', '비주얼커뮤니케이션', '크리에이티브', '문화인류',
                   '패션역사', '동양복식', '한국전통', '업사이클'],
            'keywords': ['artistic expression', 'creative layering', 'textural mix',
                         'curated details', 'editorial mood'],
            'silhouette': 'expressive and considered',
            'color_strength': 'medium',
        },
        '스포츠액티브': {
            'kw': ['스포츠', '애슬레저', '피트니스', '러닝', '요가', '댄스', '골프', '테니스',
                   '수상', '등산', '아웃도어', '사이클', '격투', '운동', '기능성', '퍼포먼스',
                   '바이오', '텍스타일엔지'],
            'keywords': ['athletic functionality', 'performance fabrics', 'mobility-focused fit',
                         'sporty layers', 'technical details'],
            'silhouette': 'functional and active',
            'color_strength': 'medium',
        },
        '트래블글로벌': {
            'kw': ['트래블', '여행', '리조트', '항공', '에어라인', '공항', '면세', '글로벌패션',
                   '글로벌브랜드', '기내', '레이어링전문'],
            'keywords': ['travel-ready versatility', 'wrinkle-resistant ease', 'cosmopolitan mix',
                         'effortless layering', 'transit-smart pieces'],
            'silhouette': 'easy and versatile',
            'color_strength': 'light',
        },
        '파티이벤트': {
            'kw': ['파티', '이벤트', '나이트', '클럽', '공연', '무대', 'DJ', '세레모니',
                   '플로리스트', '셀러브리티스타일', '소셜미디어'],
            'keywords': ['statement details', 'evening glamour', 'photo-ready impact',
                         'bold accents', 'memorable pieces'],
            'silhouette': 'statement and bold',
            'color_strength': 'strong',
        },
        '로맨틱데이트': {
            'kw': ['데이트', '로맨', '데이팅', '뷰티아트', '뷰티디자인', '와인', '에티켓',
                   '소믈리에', '의상심리'],
            'keywords': ['romantic softness', 'feminine details', 'flattering cuts',
                         'warm tones', 'inviting textures'],
            'silhouette': 'flattering and soft',
            'color_strength': 'medium',
        },
        '테크퓨처': {
            'kw': ['테크웨어', '디지털패션', 'AI', '데이터사이언스', 'NFT', '메타버스'],
            'keywords': ['technical materials', 'futuristic silhouette', 'sleek minimalism',
                         'experimental cuts', 'monochrome tech'],
            'silhouette': 'sleek and engineered',
            'color_strength': 'light',
        },
        '트렌드마케팅': {
            'kw': ['MD', '마케팅', '비즈니스경영', 'PR', '저널', '트렌드분석', '커뮤니케이션',
                   '소비자', '경영', '유통', '리테일', '이커머스', '커머스', '브랜딩', '브랜드',
                   '퍼스널브랜', '이미지컨설팅', '이미지메이킹', '에티켓학'],
            'keywords': ['trend-aware mix', 'market-driven palette', 'contemporary edits',
                         'brand-conscious styling', 'commercial appeal'],
            'silhouette': 'current and adaptive',
            'color_strength': 'medium',
        },
    }
    
    # ── major에서 카테고리 매칭 (키워드 부분 매칭) ──
    matched_cat = None
    for cat_key, cat_data in design_categories.items():
        for kw in cat_data['kw']:
            if kw in major:
                matched_cat = cat_key
                break
        if matched_cat:
            break
    
    # fallback: matched 안 되면 '트렌드마케팅' (가장 generic)
    if not matched_cat:
        matched_cat = '트렌드마케팅'
    
    cat_data = design_categories[matched_cat]
    
    # ── level + exp → refinement modifier ──
    try:
        exp_int = int(exp) if exp else 0
    except (TypeError, ValueError):
        exp_int = 0
    
    if level == 'Master' or exp_int >= 15:
        refinement = 'highly refined and signature-defining'
    elif level == 'Senior' or exp_int >= 10:
        refinement = 'refined and polished'
    elif level == 'Expert' or exp_int >= 7:
        refinement = 'experienced and well-versed'
    elif level == 'Mid-Level' or exp_int >= 4:
        refinement = 'current and market-aware'
    else:
        refinement = 'fresh and trend-forward'
    
    # ── category 영문 라벨 ──
    cat_label_en = {
        '클래식포멀': 'classic formal',
        '캐주얼데일리': 'casual daily',
        '스트릿어반': 'street urban',
        '미니멀모던': 'minimal modern',
        '럭셔리고급': 'premium luxury',
        '아트크리에이티브': 'artistic creative',
        '스포츠액티브': 'sports active',
        '트래블글로벌': 'travel global',
        '파티이벤트': 'party event',
        '로맨틱데이트': 'romantic date',
        '테크퓨처': 'tech futuristic',
        '트렌드마케팅': 'trend contemporary',
    }.get(matched_cat, 'contemporary')
    
    # ── signature directive ──
    # ─── 2026-05-14 KST · TJ 지시 ─── career 통일 후 차별화 활용 변경
    # 이전: f"informed by {career or major or 'fashion expertise'}"
    #       → career가 모두 '패션 스타일리스트'로 통일되어 차별화 사라짐
    # 변경: major를 핵심 차별화 요소로 활용 (206개 다양성 활용)
    signature_directive = (
        f"{refinement} interpretation of {cat_label_en} styling, "
        f"specialty in {major or 'contemporary fashion'}"
    )
    
    return {
        'design_keywords':     cat_data['keywords'],
        'silhouette_pref':     cat_data['silhouette'],
        'signature_directive': signature_directive,
        'color_strength':      cat_data['color_strength'],
        'refinement':          refinement,
        'matched_category':    matched_cat,
        'style_persona':       f"{name} — {refinement}, specializes in {major}",
    }


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
# [2026-05-14 KST · TJ 지시] 트렌드 캐시 — R2 trend_cache.json
#   GitHub Actions 배치(3일 1회)가 Brave Search + gpt-4.1-mini로
#   7도시×15목적 패션 트렌드 키워드를 생성 → R2에 업로드.
#   build_styling_prompt가 요청 시점에 이 캐시를 우선 조회,
#   없음/만료(6일+)/실패 시 fashion_keywords_db.json으로 자동 폴백.
# ═══════════════════════════════════════════════════
_TREND_CACHE = None
_TREND_CACHE_LOADED_AT = 0.0
_TREND_CACHE_TTL = 3600          # 1시간마다 R2 재조회 (서버 상주 대비)
_TREND_CACHE_MAX_AGE_SEC = 6 * 86400   # 6일 초과 시 만료 → 정적 DB 폴백

def _load_trend_cache():
    """R2에서 trend_cache.json 로드 (1시간 메모리 캐싱).
    실패/만료 시 None 반환 → 호출부가 정적 DB로 폴백."""
    global _TREND_CACHE, _TREND_CACHE_LOADED_AT
    now = time.time()
    # 메모리 캐시 유효 → 재사용
    if _TREND_CACHE is not None and (now - _TREND_CACHE_LOADED_AT) < _TREND_CACHE_TTL:
        return _TREND_CACHE
    # TTL 경과 — R2에서 재조회
    _TREND_CACHE_LOADED_AT = now
    try:
        import boto3
        bucket = os.getenv('R2_BUCKET_NAME', 'codibank')
        ep = os.getenv('R2_ENDPOINT', '').strip()
        if not ep:
            acct = os.getenv('R2_ACCOUNT_ID', '').strip()
            if acct:
                ep = f'https://{acct}.r2.cloudflarestorage.com'
        ak = os.getenv('R2_ACCESS_KEY_ID', '').strip()
        sk = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
        if not (ep and ak and sk):
            _TREND_CACHE = None
            return None
        client = boto3.client(
            's3', endpoint_url=ep,
            aws_access_key_id=ak, aws_secret_access_key=sk,
            region_name='auto',
        )
        resp = client.get_object(Bucket=bucket, Key='trend_cache.json')
        data = json.loads(resp['Body'].read().decode('utf-8'))
        # 신선도 체크 — 6일 초과 시 만료
        gen_str = str(data.get('generated_at', '')).replace('Z', '').strip()
        if gen_str:
            try:
                gen_dt = datetime.datetime.fromisoformat(gen_str)
                age = (datetime.datetime.utcnow() - gen_dt).total_seconds()
                if age > _TREND_CACHE_MAX_AGE_SEC:
                    print(f'[트렌드캐시] 만료 ({age/86400:.1f}일 경과) — 정적 DB 폴백', flush=True)
                    _TREND_CACHE = None
                    return None
            except Exception:
                pass  # 날짜 파싱 실패해도 캐시는 사용
        _TREND_CACHE = data
        _stats = data.get('stats', {})
        print(f"[트렌드캐시] ✅ 로드 완료 (generated_at={gen_str}, "
              f"성공 {_stats.get('ok','?')}건)", flush=True)
        return _TREND_CACHE
    except Exception as e:
        print(f'[트렌드캐시] 로드 실패 ({type(e).__name__}: {e}) — 정적 DB 폴백', flush=True)
        _TREND_CACHE = None
        return None


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
    # ─── 2026-05-12 KST · TJ 지시 (v63) ─── 7개 도시 모두 활용 ───
    # 이전: (main, single_sub) 반환 → 2개 도시만 사용
    # 변경: (main, sub_cities_list) 반환 → 6개 서브 도시 모두 활용
    main_city, sub_cities, region = get_main_sub_cities(user_location)
    
    # ─── 2026-05-12 KST · TJ 지시 (v63) ─── 도시 활용 다양화 ───
    # 사용자 요구:
    #   - 첫 생성 (seed=0): 사용자 메인 도시 (예: 서울) 스타일리스트
    #   - 다시코디/다른 날짜/다른 목적 (seed>0): 6개 서브 도시 랜덤 선정
    # 이전: seed % 2 → 짝수는 main, 홀수는 sub (단일 sub만) → 2개 도시만 활용
    # 변경: seed==0은 main, seed>0은 hash 기반 6개 서브 도시 중 선정
    #       hash(user_id + date + purpose + seed)로 안정성 + 다양성 보장
    retry_seed = int(payload.get('seed', 0))
    if retry_seed == 0:
        # 첫 생성 → 사용자 메인 도시
        active_city = main_city
    else:
        # 다시코디/다른 날짜/다른 목적 → 6개 서브 도시 중 hash 기반 선정
        _user_id_for_city = str(profile.get('id', profile.get('email', 'default')))
        _date_key = str(payload.get('date', ''))
        _hash_input = f"{_user_id_for_city}_{_date_key}_{purpose}_{retry_seed}"
        _idx = abs(hash(_hash_input)) % len(sub_cities)
        active_city = sub_cities[_idx]

    # ─── 2026-05-16 KST · TJ 지시 ─── _force_city 우회 버그 수정 ───
    # 이전 버그: STEP A 4도시 그리드가 보낸 _force_city가 weather.location으로
    #   들어가 detect_region→main_city로 재변환됨 (밀라노→유럽→파리, 런던→파리).
    # 수정: payload._force_city가 ALL_CITIES에 있으면 region 변환을 건너뛰고
    #   active_city로 직접 사용 → 도시별 차별화 정상 작동.
    _force_city = str(payload.get('_force_city') or '').strip()
    if _force_city and _force_city in ALL_CITIES:
        active_city = _force_city
        print(f"[엔진] _force_city 직접 적용: {active_city}", flush=True)

    # ── 성별에 따른 키워드 선택 ──
    kw_key = "women" if gender_ko == "여성" else "men"
    # ─── 2026-05-14 KST · TJ 지시 ─── 트렌드 캐시 우선 조회 ───
    # R2 trend_cache.json (3일 1회 Brave Search 갱신) → 해당 셀 있으면 사용
    # 없음/만료/실패 → fashion_keywords_db.json 정적 DB 폴백
    keywords_str = ''
    _trend = _load_trend_cache()
    if _trend:
        _tc_cell = (_trend.get('city_keywords', {})
                          .get(active_city, {})
                          .get(purpose, {}))
        keywords_str = _tc_cell.get(kw_key, '')
        if keywords_str:
            print(f"[트렌드캐시] 키워드 사용: {active_city}/{purpose}/{kw_key} "
                  f"({len(keywords_str) if isinstance(keywords_str, list) else '?'}개)", flush=True)
    # 폴백: 트렌드 캐시 없음/해당 셀 없음 → 정적 DB
    if not keywords_str:
        city_kw = fashion_db.get('city_keywords', {}).get(active_city, {}).get(purpose, {})
        keywords_str = city_kw.get(kw_key, '')

    user_id = str(profile.get('id', profile.get('email', 'default')))
    selected_keywords = select_daily_keywords(keywords_str, user_id, purpose, count=8, retry_seed=retry_seed)
    
    # [2026-04-06 추가] 온도 기반 키워드 필터링 — 25도에 Cardigan/Coat 제거
    _warm_block = ['coat','cardigan','sweater','knit','wool','muffler','scarf',
                   'turtleneck','fleece','padding','puffer','layered','layer',
                   'heavy','thick','down jacket','overcoat','trench']
    _cold_block = ['sleeveless','tank top','sandal','shorts','crop top']
    
    if temp >= 22:
        # 따뜻한 날씨 → 두꺼운/레이어드 키워드 제거
        selected_keywords = [kw for kw in selected_keywords 
                            if not any(w in kw.lower() for w in _warm_block)]
    elif temp <= 5:
        # 추운 날씨 → 시원한 키워드 제거
        selected_keywords = [kw for kw in selected_keywords 
                            if not any(w in kw.lower() for w in _cold_block)]
    
    # ── 온도 버킷 ──
    temp_bucket = _get_temp_bucket(temp)
    
    # ── 여성 하의 타입 결정 ──
    # ─── 2026-05-12 KST · TJ 지시 (v60) ─── 바지 발목 덮음 강제 통일 ───
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
                "⛔ BOTTOM (PANTS — HIGHEST PRIORITY): The woman wears well-fitted REGULAR FIT trousers. "
                "Hem MUST FULLY COVER the ankle bone (medial/lateral malleolus) and slightly overlap the shoe top. "
                "ABSOLUTELY FORBIDDEN: cropped, ankle-exposed, 7/8, capri, high-water, "
                "any visible ankle skin between hem and shoe. "
                "Slim/skinny fit FORBIDDEN unless user explicitly requested it. "
            )
    else:
        # [2026-04-19 BUGFIX #4] bottom_type 변수가 여성 분기에서만 정의되어
        # line 388 metadata 구성 시 NameError 위험 (현재 and 연산자 short-circuit으로 막혀있지만 취약)
        bottom_type = "pants"
        bottom_instruction = (
            "⛔ BOTTOM (PANTS — HIGHEST PRIORITY): The man wears well-fitted REGULAR FIT trousers. "
            "Hem MUST FULLY COVER the ankle bone (medial/lateral malleolus) and slightly overlap the shoe top. "
            "ABSOLUTELY FORBIDDEN: cropped, ankle-exposed, 7/8, capri, high-water, "
            "any visible ankle skin between hem and shoe. "
            "Slim/skinny fit FORBIDDEN unless user explicitly requested it. "
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
        # [2026-04-06 보강] 날씨=사용자 현지, 패션감각=스타일리스트 도시 분리
        f"WEATHER AT USER LOCATION (HIGH PRIORITY — MUST OVERRIDE GENERIC STYLING): "
        f"The user is currently at: {user_location or 'their local area'}. "
        f"Local temperature: {temp}°C, Condition: {condition}. "
        f"Outfit MUST be appropriate for THIS temperature — NOT for the stylist city. "
        f"Outfit weight guide: {temp_bucket}. "
        f"{'WARM WEATHER RULE: NO blazer, NO jacket, NO cardigan, NO sweater, NO coat, NO heavy layers. Single light layer ONLY. Shirt sleeves can be short or rolled up. Fabrics must be BREATHABLE (cotton, linen, lightweight). ' if temp >= 22 else ''}"
        f"{'COLD WEATHER RULE: Must include warm outer layer (coat/jacket). Layering is essential. Warm fabrics required. ' if temp <= 10 else ''}"
        f"\n\n"
        # ── [2026-04-27 v25 TJ] 정+후면 가로 와이드 LAYOUT (트라이온과 동일 정책) ──
        f"🖼️ CRITICAL OUTPUT FORMAT (MUST OBEY — top priority): "
        f"Generate a HORIZONTAL WIDE image. "
        f"Output dimensions: 2048 pixels wide × 1024 pixels tall (2:1 aspect ratio). "
        f"The width MUST be EXACTLY 2× the height. "
        f"DO NOT generate vertical, portrait, or square images. "
        f"DO NOT generate 9:16, 3:4, or 1:1 ratios. "
        f"If you cannot achieve exactly 2:1, output 16:9 (1920×1080) instead. "
        f"\n\n"
        f"═══ LAYOUT (within the wide canvas) ═══ "
        f"Output a SINGLE WIDE image with TWO poses of the SAME person, side by side: "
        f"  • LEFT half (pixels 0 to 1024 wide): FRONT view (full body, facing camera). "
        f"  • RIGHT half (pixels 1024 to 2048 wide): BACK view (full body, facing AWAY from camera, same pose). "
        f"Both views show the EXACT SAME outfit, lighting, hair, and styling. "
        f"The two figures are evenly spaced, not touching, on the same ground line. "
        f"FACE/HEAD: LEFT = face fully visible (preserve identity 99.99% to reference). "
        f"  RIGHT = face NOT visible (back of head only). FORBIDDEN: showing face on the BACK view. "
        f"═══ END LAYOUT ═══ "
        f"\n\n"
        # ─── 2026-05-12 KST · TJ 지시 (v65) ─── ABSOLUTE RULES 블록 제거 ───
        # 이전: build_styling_prompt 끝에 "ABSOLUTE RULES (VIOLATION = GENERATION FAILURE)"
        #        + BODY PROPORTION/SOCKS/STYLIST RULE/BACKGROUND/NO TEXT 블록 (강제 표현 8회)
        # 변경: mock_backend.py의 CORE RULES와 100% 중복이라 제거
        #        WIDTH=2×HEIGHT 리마인더도 LAYOUT 블록에서 이미 강조됨 → 제거
        # 효과: 분량 ~700 chars 감소, 강제 표현 8회 감소
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
        "sub_cities": sub_cities,
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
        print(f"🏙️ 도시: main={meta['main_city']}, sub_pool={meta.get('sub_cities', [])} → 선택: {meta['active_city']}")
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
    
    # 3. 스타일리스트 컬러를 프롬프트에 반영
    # ─── [2026-04-26 v21 TJ] 컬러 자유도 증가 ───
    # 이전: "Primary: X. Accent: Y. Incorporate these colors" → 매번 같은 색 조합
    # 변경: 가이드로 제시 + 스타일리스트가 코디 목적/날씨/계절에 맞춰 자유 조합
    # ─── 2026-05-12 KST · TJ 지시 (v62) ─── 9,600 차별화 강제 반영 ───
    # 사용자 보고: 같은 코디목적 + 다른 날짜 → AI 스타일리스트만 바뀌고 출력 동일
    # 원인: stylist의 color1/color2 hint만 prompt에 들어가서 차별화 실종
    # 변경: _generate_stylist_dna()로 major/career/level/exp 기반 DNA 생성 후
    #       'STYLIST DNA' 블록을 PRIMARY DIRECTIVE로 prompt에 강제 반영
    # ─── 2026-05-12 KST · TJ 지시 (v65) ─── Phase 1+2+4 종합 픽스 ───
    # 진단: v62의 STYLIST DNA가 prompt 끝(append)에 위치 → mock_backend가 추가하는
    #       5,588 chars 텍스트에 묻혀서 30~46% 지점이 됨 (LLM attention drop 구간)
    #       → DNA 지시를 LLM이 무시 → "stylist 이름만 다르고 outfit 동일"
    # 변경: STYLIST DNA를 prompt 시작에 prepend (book-end 1)
    #       + mock_backend에서 끝에 DNA REMINDER 추가 (book-end 2)
    #       + 강제 표현 56회 → 8회 이하로 정리
    #       + 분량 65% 압축
    if stylist:
        dna = _generate_stylist_dna(stylist)
        design_kw_str = ", ".join(dna['design_keywords'])
        
        # color_strength에 따라 color 강조 톤 분기
        if dna['color_strength'] == 'strong':
            color_line = f"SIGNATURE COLORS: '{stylist['color1']}' primary + '{stylist['color2']}' accent (feature prominently, respect avoid-colors)."
        elif dna['color_strength'] == 'medium':
            color_line = f"SIGNATURE COLORS: '{stylist['color1']}' + '{stylist['color2']}' (anchor tones, complement with neutrals)."
        else:  # light
            color_line = f"SIGNATURE COLORS (loose hint): '{stylist['color1']}', '{stylist['color2']}'. Lean muted/neutral palette."
        
        # ── v65: 압축된 DNA HEAD (prompt 시작에 배치) ──
        # ─── 2026-05-14 KST · TJ 지시 ─── career 통일 → Career 줄 제거 + major 강조
        # 이전: f"Career: {stylist.get('career', '')}\n" (모두 '패션 스타일리스트' 동일)
        # 변경: Career 줄 제거. major를 핵심 차별화 정보로 격상 (206개 다양성 활용)
        stylist_dna_head = (
            f"⭐ STYLIST DNA — DEFINES THIS OUTFIT (NOT a generic 'safe' look):\n"
            f"Name: {stylist.get('name', '')} · Level: {stylist.get('level', '')} · "
            f"Experience: {stylist.get('exp', 0)}yr\n"
            f"SPECIALTY: {stylist.get('major', '')} (this is the stylist's expert domain — outfit MUST reflect it)\n"
            f"DESIGN KEYWORDS: {design_kw_str}.\n"
            f"SILHOUETTE: {dna['silhouette_pref']}.\n"
            f"{color_line}\n"
            f"Different stylist DNA = clearly different outfit. The image must visibly express THIS DNA, not blend into neutrals.\n\n"
        )
        # v65: append → prepend (LLM attention 최대 영역에 배치)
        prompt = stylist_dna_head + prompt
    
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

# ═══════════════════════════════════════════════════
# [2026-05-16 KST · TJ 지시 · 방안 A] generate_outfit_spec 재설계
#   문제: 기존 딕셔너리가 목적별 단일값 → 스타일리스트/도시 무관 동일 옷.
#   해결: 각 카테고리를 후보 리스트(3개)로 확장하고, 스타일리스트
#         (name/major/level/color1) 기반 결정적 해시로 후보 중 선택.
#         → 같은 스타일리스트는 일관, 다른 스타일리스트는 다른 아이템.
# ═══════════════════════════════════════════════════
def _pick_by_stylist(candidates, stylist, salt=''):
    """후보 리스트에서 스타일리스트 기반 결정적 선택.
    같은 스타일리스트 → 항상 같은 선택 / 다른 스타일리스트 → 다른 선택.
    salt(카테고리명)로 카테고리별 인덱스가 동조화되지 않게 분리."""
    if not candidates:
        return None
    if isinstance(candidates, str):
        return candidates
    if len(candidates) == 1:
        return candidates[0]
    s = stylist or {}
    key = (f"{s.get('name','')}|{s.get('major','')}|{s.get('level','')}"
           f"|{s.get('color1','')}|{salt}")
    h = int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
    return candidates[h % len(candidates)]


_OUTER_ITEMS = {
    "extreme_cold": {"M": ["헤비 패딩 코트", "롱 다운 파카", "무스탕 코트"],
                     "F": ["롱 패딩 코트", "다운 롱코트", "무스탕 코트"]},
    "very_cold":    {"M": ["울 오버코트", "더블 울코트", "발마칸 코트"],
                     "F": ["울 롱코트", "핸드메이드 코트", "더블 코트"]},
    "cold":         {"M": ["트렌치코트", "울 싱글코트", "발마칸 코트"],
                     "F": ["트렌치코트", "울 코트", "라이트 롱코트"]},
    "chilly":       {"M": ["블레이저", "싱글 자켓", "필드 자켓"],
                     "F": ["테일러드 자켓", "블레이저", "트위드 자켓"]},
    "cool":         {"M": ["라이트 자켓", "니트 가디건", "셔켓"],
                     "F": ["가디건", "라이트 자켓", "니트 가디건"]},
    "mild":         {"M": ["얇은 자켓", "셔켓", "라이트 가디건"],
                     "F": ["라이트 가디건", "얇은 자켓", "니트 베스트"]},
}
_TOP_ITEMS = {
    "비즈니스 포멀": {"M": ["드레스 셔츠", "스프레드칼라 셔츠", "모크넥 니트"],
                 "F": ["실크 블라우스", "테일러드 셔츠", "노카라 블라우스"]},
    "데일리 오피스룩": {"M": ["옥스포드 셔츠", "버튼다운 셔츠", "니트 폴로"],
                  "F": ["니트 탑", "셔츠 블라우스", "라운드 니트"]},
    "면접룩": {"M": ["화이트 셔츠", "솔리드 드레스셔츠", "라이트블루 셔츠"],
            "F": ["클린 블라우스", "솔리드 블라우스", "라운드넥 니트"]},
    "결혼식 하객룩": {"M": ["드레스 셔츠", "윙칼라 셔츠", "실크 셔츠"],
                "F": ["시폰 블라우스", "새틴 블라우스", "레이스 탑"]},
    "소개팅룩": {"M": ["니트 셔츠", "캐주얼 셔츠", "라운드 니트"],
             "F": ["파스텔 니트", "셔링 블라우스", "라운드 니트"]},
    "로맨틱 데이트룩": {"M": ["캐시미어 니트", "터틀넥 니트", "실크 셔츠"],
                  "F": ["오프숄더 탑", "레이스 블라우스", "니트 탑"]},
    "상견례/가족모임": {"M": ["폴로 셔츠", "니트 셔츠", "버튼다운 셔츠"],
                  "F": ["단정한 블라우스", "라운드 니트", "셔츠 블라우스"]},
    "사교 모임/파티": {"M": ["새틴 셔츠", "벨벳 셔츠", "실크 셔츠"],
                  "F": ["새틴 캐미솔", "시퀸 탑", "실크 블라우스"]},
    "주말 나들이": {"M": ["스트라이프 티셔츠", "코튼 티셔츠", "헨리넥 티셔츠"],
               "F": ["프린트 티셔츠", "코튼 블라우스", "스트라이프 탑"]},
    "여행지 인생샷": {"M": ["린넨 셔츠", "오버셔츠", "코튼 셔츠"],
                "F": ["오버사이즈 셔츠", "린넨 블라우스", "프린트 탑"]},
    "꾸안꾸 데일리": {"M": ["플레인 티셔츠", "코튼 스웨트셔츠", "베이직 니트"],
                "F": ["베이직 니트", "코튼 티셔츠", "크루넥 스웨트"]},
    "스포티/애슬레저": {"M": ["테크 티셔츠", "퍼포먼스 탑", "집업 탑"],
                  "F": ["크롭 탑", "퍼포먼스 탑", "집업 탑"]},
    "공항 패션": {"M": ["캐시미어 니트", "오버핏 후디", "니트 풀오버"],
              "F": ["가디건 레이어드", "니트 풀오버", "오버핏 후디"]},
    "미니멀/심플": {"M": ["모크넥 니트", "크루넥 니트", "솔리드 셔츠"],
               "F": ["터틀넥 니트", "크루넥 니트", "솔리드 블라우스"]},
    "트렌디/스트릿": {"M": ["그래픽 티셔츠", "오버핏 후디", "니트 폴로"],
               "F": ["크롭 후디", "그래픽 티셔츠", "니트 베스트"]},
}
_BOTTOM_ITEMS_M = {
    "비즈니스 포멀": ["울 슬랙스", "테일러드 슬랙스", "노턱 슬랙스"],
    "데일리 오피스룩": ["치노 팬츠", "코튼 슬랙스", "슬림 슬랙스"],
    "면접룩": ["네이비 슬랙스", "차콜 슬랙스", "울 슬랙스"],
    "결혼식 하객룩": ["울 드레스 팬츠", "테일러드 슬랙스", "슬림 슬랙스"],
    "소개팅룩": ["슬림 치노", "코튼 슬랙스", "테이퍼드 팬츠"],
    "로맨틱 데이트룩": ["와이드 슬랙스", "테일러드 슬랙스", "슬림 슬랙스"],
    "상견례/가족모임": ["울 슬랙스", "코튼 슬랙스", "테일러드 슬랙스"],
    "사교 모임/파티": ["슬림 슬랙스", "테일러드 슬랙스", "블랙 슬랙스"],
    "주말 나들이": ["코튼 팬츠", "데님 팬츠", "치노 팬츠"],
    "여행지 인생샷": ["린넨 팬츠", "코튼 팬츠", "와이드 팬츠"],
    "꾸안꾸 데일리": ["코튼 팬츠", "데님 팬츠", "치노 팬츠"],
    "스포티/애슬레저": ["트레이닝 팬츠", "조거 팬츠", "테크 팬츠"],
    "공항 패션": ["조거 팬츠", "와이드 팬츠", "코튼 팬츠"],
    "미니멀/심플": ["스트레이트 슬랙스", "와이드 팬츠", "테이퍼드 팬츠"],
    "트렌디/스트릿": ["카고 팬츠", "와이드 데님", "배기 팬츠"],
}
_BOTTOM_ITEMS_F_SKIRT = {
    "비즈니스 포멀": ["미디 펜슬 스커트", "H라인 스커트", "테일러드 스커트"],
    "데일리 오피스룩": ["미디 A라인 스커트", "H라인 스커트", "플리츠 미디 스커트"],
    "면접룩": ["미디 펜슬 스커트", "H라인 스커트", "테일러드 스커트"],
    "결혼식 하객룩": ["A라인 미디 스커트", "플레어 미디 스커트", "플리츠 스커트"],
    "소개팅룩": ["플리츠 스커트", "플레어 스커트", "A라인 미니스커트"],
    "로맨틱 데이트룩": ["플레어 스커트", "플리츠 미디 스커트", "랩 스커트"],
    "상견례/가족모임": ["미디 A라인 스커트", "H라인 스커트", "플리츠 미디 스커트"],
    "사교 모임/파티": ["새틴 미디 스커트", "시퀸 스커트", "플레어 스커트"],
    "주말 나들이": ["플리츠 미니스커트", "데님 스커트", "A라인 스커트"],
    "여행지 인생샷": ["플레어 미디 스커트", "린넨 스커트", "랩 스커트"],
    "꾸안꾸 데일리": ["A라인 미디 스커트", "데님 스커트", "플리츠 스커트"],
    "미니멀/심플": ["H라인 미디 스커트", "스트레이트 스커트", "랩 스커트"],
    "트렌디/스트릿": ["카고 스커트", "데님 미니스커트", "플리츠 스커트"],
}
_BOTTOM_ITEMS_F_PANTS = {
    "비즈니스 포멀": ["와이드 슬랙스", "테일러드 슬랙스", "스트레이트 슬랙스"],
    "데일리 오피스룩": ["스트레이트 팬츠", "테이퍼드 슬랙스", "와이드 슬랙스"],
    "면접룩": ["스트레이트 슬랙스", "테일러드 슬랙스", "와이드 슬랙스"],
    "결혼식 하객룩": ["테일러드 와이드 팬츠", "스트레이트 슬랙스", "드레스 팬츠"],
    "소개팅룩": ["테이퍼드 팬츠", "스트레이트 슬랙스", "와이드 슬랙스"],
    "로맨틱 데이트룩": ["와이드 슬랙스", "플레어 팬츠", "스트레이트 슬랙스"],
    "상견례/가족모임": ["스트레이트 슬랙스", "테일러드 슬랙스", "와이드 슬랙스"],
    "사교 모임/파티": ["테일러드 와이드 팬츠", "슬림 슬랙스", "스트레이트 슬랙스"],
    "주말 나들이": ["코튼 팬츠", "데님 팬츠", "치노 팬츠"],
    "여행지 인생샷": ["린넨 팬츠", "와이드 팬츠", "코튼 팬츠"],
    "꾸안꾸 데일리": ["코튼 팬츠", "데님 팬츠", "와이드 슬랙스"],
    "스포티/애슬레저": ["레깅스", "조거 팬츠", "트레이닝 팬츠"],
    "공항 패션": ["와이드 팬츠", "조거 팬츠", "코튼 팬츠"],
    "미니멀/심플": ["스트레이트 슬랙스", "와이드 팬츠", "테이퍼드 팬츠"],
    "트렌디/스트릿": ["카고 팬츠", "와이드 데님", "배기 팬츠"],
}
_SHOES_M = {
    "비즈니스 포멀": ["옥스포드 슈즈", "더비 슈즈", "몽크스트랩"],
    "데일리 오피스룩": ["더비 슈즈", "로퍼", "첼시부츠"],
    "면접룩": ["스트레이트팁 슈즈", "옥스포드 슈즈", "더비 슈즈"],
    "결혼식 하객룩": ["몽크스트랩", "옥스포드 슈즈", "더비 슈즈"],
    "소개팅룩": ["로퍼", "첼시부츠", "미니멀 스니커즈"],
    "로맨틱 데이트룩": ["첼시부츠", "로퍼", "더비 슈즈"],
    "상견례/가족모임": ["로퍼", "더비 슈즈", "옥스포드 슈즈"],
    "사교 모임/파티": ["로퍼", "첼시부츠", "몽크스트랩"],
    "주말 나들이": ["캔버스 스니커즈", "화이트 스니커즈", "로퍼"],
    "여행지 인생샷": ["캔버스 스니커즈", "슬립온", "로퍼"],
    "꾸안꾸 데일리": ["미니멀 스니커즈", "캔버스 스니커즈", "로퍼"],
    "스포티/애슬레저": ["러닝화", "트레이닝화", "청키 스니커즈"],
    "공항 패션": ["슬립온", "미니멀 스니커즈", "첼시부츠"],
    "미니멀/심플": ["화이트 스니커즈", "미니멀 스니커즈", "로퍼"],
    "트렌디/스트릿": ["하이탑 스니커즈", "청키 스니커즈", "캔버스 스니커즈"],
}
_SHOES_F = {
    "비즈니스 포멀": ["포인티드 펌프스", "스틸레토 힐", "로퍼"],
    "데일리 오피스룩": ["로퍼", "블록힐", "메리제인"],
    "면접룩": ["클로즈드토 힐", "포인티드 펌프스", "로퍼"],
    "결혼식 하객룩": ["슬링백", "스트랩 힐", "포인티드 펌프스"],
    "소개팅룩": ["메리제인", "발레 플랫", "블록힐"],
    "로맨틱 데이트룩": ["스트랩 힐", "슬링백", "앵클 부츠"],
    "상견례/가족모임": ["로퍼", "블록힐", "메리제인"],
    "사교 모임/파티": ["스트랩 힐", "슬링백", "스틸레토 힐"],
    "주말 나들이": ["플랫 슈즈", "캔버스 스니커즈", "로퍼"],
    "여행지 인생샷": ["플랫 슈즈", "캔버스 스니커즈", "슬링백"],
    "꾸안꾸 데일리": ["발레 플랫", "로퍼", "캔버스 스니커즈"],
    "스포티/애슬레저": ["러닝화", "트레이닝화", "청키 스니커즈"],
    "공항 패션": ["컴포트 스니커즈", "슬립온", "로퍼"],
    "미니멀/심플": ["뮬", "로퍼", "미니멀 플랫"],
    "트렌디/스트릿": ["청키 스니커즈", "플랫폼 슈즈", "하이탑 스니커즈"],
}
_BAG_M = {
    "비즈니스 포멀": ["블랙 브리프케이스", "레더 토트", "서류 가방"],
    "공항 패션": ["캐리온 러기지", "더플백", "백팩"],
    "주말 나들이": ["캐주얼 백팩", "크로스백", "토트백"],
    "스포티/애슬레저": ["스포츠 백팩", "짐색", "크로스백"],
    "여행지 인생샷": ["데이팩", "크로스백", "더플백"],
}
_BAG_F = {
    "비즈니스 포멀": ["레더 토트백", "스트럭처드 토트", "핸드백"],
    "데일리 오피스룩": ["숄더백", "토트백", "핸드백"],
    "결혼식 하객룩": ["클러치", "미니 핸드백", "체인 백"],
    "소개팅룩": ["미니 크로스백", "체인 숄더백", "미니 토트"],
    "로맨틱 데이트룩": ["이브닝 클러치", "미니 크로스백", "체인 백"],
    "주말 나들이": ["캔버스 토트", "크로스백", "버킷백"],
    "공항 패션": ["여행 숄더백", "토트백", "백팩"],
    "사교 모임/파티": ["클러치", "체인 백", "미니 백"],
}
# 상의 컬러 — 목적별 후보 팔레트 (스타일리스트 해시로 선택)
_TOP_COLORS = {
    "비즈니스 포멀": ["화이트", "라이트 블루", "아이보리"],
    "데일리 오피스룩": ["아이보리", "라이트 그레이", "스카이 블루"],
    "면접룩": ["화이트", "라이트 블루", "아이보리"],
    "결혼식 하객룩": ["크림", "페일 핑크", "라이트 그레이"],
    "소개팅룩": ["파스텔 핑크", "크림", "라벤더"],
    "로맨틱 데이트룩": ["크림", "페일 핑크", "아이보리"],
    "상견례/가족모임": ["라이트 베이지", "아이보리", "페일 그레이"],
    "사교 모임/파티": ["샴페인", "블랙", "딥 버건디"],
    "주말 나들이": ["라이트 그레이", "화이트", "머스타드"],
    "여행지 인생샷": ["화이트", "베이지", "스카이 블루"],
    "꾸안꾸 데일리": ["오프화이트", "라이트 그레이", "베이지"],
    "스포티/애슬레저": ["화이트", "블랙", "쿨 그레이"],
    "공항 패션": ["크림", "오트밀", "차콜"],
    "미니멀/심플": ["오프화이트", "라이트 그레이", "블랙"],
    "트렌디/스트릿": ["블랙", "오프화이트", "카키"],
}

def _bottom_color_pool(purpose):
    """하의 컬러 후보 팔레트 — 목적 그룹별"""
    if purpose in ['비즈니스 포멀', '면접룩', '결혼식 하객룩', '상견례/가족모임']:
        return ['네이비', '차콜', '다크 그레이']
    if purpose in ['데일리 오피스룩', '사교 모임/파티', '미니멀/심플']:
        return ['차콜', '블랙', '다크 네이비']
    if purpose in ['여행지 인생샷', '주말 나들이', '꾸안꾸 데일리']:
        return ['베이지', '라이트 그레이', '인디고']
    return ['차콜', '네이비', '베이지']



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
    
    # ── 아우터 (20도 이상 제외) ──
    if temp <= -10: t_key = "extreme_cold"
    elif temp <= 0: t_key = "very_cold"
    elif temp <= 5: t_key = "cold"
    elif temp <= 10: t_key = "chilly"
    elif temp <= 15: t_key = "cool"
    elif temp <= 20: t_key = "mild"
    else: t_key = None
    
    if t_key:
        outer_items = _OUTER_ITEMS.get(t_key, {})
        # [2026-05-16 방안A] 후보 리스트 → 스타일리스트 해시로 선택
        outer_item = _pick_by_stylist(outer_items.get(gender, ["자켓"]), stylist, 'outer')
        # [2026-04-06 수정] color1에서 실제 컬러명만 추출 (아이템명 제거)
        _outer_color = _extract_color(color1) if color1 else '다크 네이비'
        spec['outer'] = {
            'item_ko': outer_item,
            'item_en': outer_item,
            'color_ko': _outer_color,
        }
    
    # ── 상의 (스카프는 별도 카테고리 — 상의에 포함하지 않음) ──
    # [2026-05-16 방안A] 후보 리스트 → 스타일리스트 해시로 선택
    top_map = _TOP_ITEMS.get(purpose, {"M": ["셔츠"], "F": ["블라우스"]})
    top_item = _pick_by_stylist(top_map.get(gender, ["셔츠"]), stylist, 'top')
    # [2026-04-06 수정] 상의 컬러는 스타일리스트 color2가 아닌 목적별 적절한 컬러 사용
    # [2026-04-06 추가] 따뜻한 날씨(22도+)에 상의를 가벼운 아이템으로 변경
    # [2026-05-16 방안A] 여름 상의도 후보 리스트 → 스타일리스트 해시 선택
    if temp >= 22:
        _summer_tops = {
            "M": {"비즈니스 포멀": ["린넨 셔츠", "반팔 드레스셔츠"],
                   "데일리 오피스룩": ["반팔 셔츠", "린넨 셔츠"],
                   "면접룩": ["반팔 드레스 셔츠", "린넨 셔츠"],
                   "소개팅룩": ["린넨 셔츠", "반팔 니트"],
                   "주말 나들이": ["반팔 티셔츠", "린넨 셔츠"],
                   "공항 패션": ["반팔 린넨 셔츠", "반팔 티셔츠"]},
            "F": {"비즈니스 포멀": ["반팔 블라우스", "슬리브리스 블라우스"],
                   "데일리 오피스룩": ["반팔 니트", "반팔 블라우스"],
                   "면접룩": ["반팔 블라우스", "슬리브리스 블라우스"],
                   "소개팅룩": ["슬리브리스 블라우스", "반팔 니트"],
                   "주말 나들이": ["반팔 티셔츠", "린넨 블라우스"],
                   "공항 패션": ["반팔 린넨 셔츠", "반팔 티셔츠"]},
        }
        _summer_cands = _summer_tops.get(gender, {}).get(purpose, [])
        if _summer_cands:
            top_item = _pick_by_stylist(_summer_cands, stylist, 'summer_top')

    # [2026-05-16 방안A] 상의 컬러 후보 팔레트 → 스타일리스트 해시 선택
    top_color = _pick_by_stylist(_TOP_COLORS.get(purpose, ['베이지']), stylist, 'top_color')
    spec['top'] = {
        'item_ko': top_item,
        'item_en': top_item,
        'color_ko': top_color,
    }
    
    # ── 하의 ──
    # [2026-05-16 방안A] 하의 아이템·컬러 모두 후보 리스트 → 스타일리스트 해시 선택
    _bt_color = _pick_by_stylist(_bottom_color_pool(purpose), stylist, 'bottom_color')
    if gender == "F" and bottom_type == "skirt":
        bt_item = _pick_by_stylist(_BOTTOM_ITEMS_F_SKIRT.get(purpose, ["A라인 스커트"]), stylist, 'bottom')
        spec['bottom'] = {'item_ko': bt_item, 'item_en': bt_item, 'color_ko': _bt_color}
    elif gender == "F":
        bt_item = _pick_by_stylist(_BOTTOM_ITEMS_F_PANTS.get(purpose, ["슬랙스"]), stylist, 'bottom')
        spec['bottom'] = {'item_ko': bt_item, 'item_en': bt_item, 'color_ko': _bt_color}
    else:
        bt_item = _pick_by_stylist(_BOTTOM_ITEMS_M.get(purpose, ["슬랙스"]), stylist, 'bottom')
        spec['bottom'] = {'item_ko': bt_item, 'item_en': bt_item, 'color_ko': _bt_color}
    
    # ── 신발 ──
    # [2026-05-16 방안A] 신발 후보 리스트 → 스타일리스트 해시 선택
    shoes_map = _SHOES_M if gender == "M" else _SHOES_F
    _shoe_cands = shoes_map.get(purpose, ["로퍼"] if gender == "M" else ["플랫 슈즈"])
    shoe = _pick_by_stylist(_shoe_cands, stylist, 'shoes')
    spec['shoes'] = {'item_ko': shoe, 'item_en': shoe, 'color_ko': '브라운' if gender == "M" else '베이지'}
    
    # ── 가방 (컬러 포함) ──
    # [2026-05-16 방안A] 가방 후보 리스트 → 스타일리스트 해시 선택
    bag_map = _BAG_M if gender == "M" else _BAG_F
    bag = _pick_by_stylist(bag_map.get(purpose, []), stylist, 'bag')
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
    lines = ["\n=== OUTFIT GUIDE (stylist's curated direction) ==="]
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
    
    # [2026-05-16 방안A] 톤 완화 — outfit_spec이 이미 스타일리스트별로
    #   다른 아이템을 선택하므로, EXACTLY 강제 대신 "강한 가이드"로.
    #   카테고리 구성·색상 일관성은 유지하되, 스타일리스트 해석 여지 허용.
    lines.append("This outfit guide reflects the stylist's curated direction. "
                 "Use it as a strong reference: keep the listed garment categories "
                 "and colors, while letting the stylist's signature style shape "
                 "the fabric, fit, and finishing details.")
    lines.append("=== END OUTFIT GUIDE ===\n")
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
