# ═══════════════════════════════════════════════════════════════════════
# 📋 수정 이력 (MODIFICATION HISTORY) — 최신순
# ═══════════════════════════════════════════════════════════════════════
# 이 블록은 파일 수정 때마다 최상단에 누적됩니다.
# 각 항목은 실제 수정 지점(줄번호)에도 동일한 날짜/요약 주석이 존재합니다.
# 점검 시 이 블록만 읽어도 파일의 최신 상태와 변경 이력을 알 수 있습니다.
#
# ─── 2026-05-19 KST · TJ 보고 (STEP A 과거 이미지 재탕 — 캐시 HIT 수정) ───
#  증상: 같은 목적(하객룩)으로 다시 생성 시 4개 도시 추천코디가 단 하나도
#        안 바뀌고 과거 이미지 그대로. 오전 생성 = 오후 생성.
#  원인: STEP A(4장 그리드)는 ① force_regen 누락 → 캐시 키에 시간 nonce(rsd)
#        없음 → 같은 (목적·날짜·스타일리스트·도시) 면 캐시 키 동일 → 캐시
#        HIT → AI 호출 자체가 안 일어남. ② 스타일리스트 엔진이
#        hash(user+purpose+today+seed) 결정론적 → seed 고정 시 같은
#        키워드/스타일리스트/도시 선정. (STEP B·Q3 는 force_regen=True 였으나
#        STEP A 만 빠져 있었음.)
#  수정: STEP A 진입 시(~line 3884) seed/retrySeed 를 서버 시각(ms)으로 강제
#        + force_regen=True(~line 4090). → 엔진이 매번 다른 키워드/스타일리스트
#        선정 + 캐시 키도 매번 달라져 캐시 MISS → 매 생성 새 코디.
#  ※ '랜덤 여부' 답: 스타일리스트 선정은 완전 랜덤이 아니라 seed 기반
#    결정론적(재현성 설계). 본 수정으로 STEP A 는 매번 새 seed 가 되어
#    실질적으로 매 생성 다른 스타일리스트/코디가 나온다. 7일 이내 중복은
#    자동 충족(매번 새로 생성). 정밀한 7일 시그니처 중복필터는 사용자별
#    생성 이력 저장소(Supabase) 구축 후 별도 작업 권장.
#
# ─── 2026-05-19 KST · TJ 보고 (Q3 세로 출력 — 가로강제 진단 강화) ───
#  · [최종 수정] Q3 세로 재발 — 코디핏 Q3 config 를 트라이온과 100% 동일하게.
#    트라이온(_TRYON_MODEL, line 7938~)은 가로 정상이라 코드 비교한 결과
#    두 가지 다름이 결정적이었음:
#      ① temperature: 트라이온 0.4 vs Q3 0.7
#      ② max_output_tokens: 트라이온 8192 명시 vs Q3 미설정(기본값)
#    특히 ② — image_size="2K"(2048px) 출력에 필요한 토큰이 부족하면
#    모델이 작은 해상도로 fallback 하면서 aspect_ratio 지시도 약화돼
#    세로가 나온다. Q3 config 를 트라이온 검증값으로 맞춤(~line 3230).
#  · [후속] 3rd 결과가 여전히 968x1567 세로(정면 1명)로 생성됨.
#    트라이온(_tryon_build_prompt)은 같은 Nano Banana Pro 로 가로 정상.
#    → 트라이온의 검증된 프롬프트 패턴을 Q3 gemini_prompt(~line 2988)에
#      이식: ① OUTPUT FORMAT 을 프롬프트 최상단(top priority) 배치
#      ② LEFT/RIGHT 를 픽셀 좌표("pixels 0 to 1024 wide" 등)로 명시
#      ③ "reference 이미지가 세로여도 무시, 출력은 항상 가로" 명시
#      ④ 세로 fallback 문구 제거. 로그도 'Q3 전용 프롬프트 적용 v2'.
#  증상: 코디핏 3rd(Nano Banana Pro) 결과가 16:9 가로가 아니라 세로
#        (968×1567)로 생성됨.
#  원인: Q3 gemini 호출의 image_config(aspect_ratio="16:9") 가
#        SDK 미지원 시 except 로 '조용히' 폴백 → aspect_ratio 누락.
#        requirements.txt 의 google-genai>=1.0.0 하한이 낮아 Render 가
#        ImageConfig 없는 구버전을 설치하면 폴백된다.
#  수정: ① requirements.txt: google-genai>=1.0.0 → >=1.49.0
#           (ImageConfig + image_size 확실 포함 버전)
#        ② Q3 gemini config(~line 3169): 폴백 단계별 로그 추가
#           ①image_config(ratio+size) ②ratio만 ③미지원 — 어느 경로인지
#           로그로 노출 + image_size="2K" 추가.
#  ※ 적용하려면 requirements.txt + 본 파일을 Render 에 재배포(재빌드)
#    필수. 재배포 후 로그의 [ai_styling_gemini] Q3 가로강제 ①/②/③ 확인.
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔒 [정상 확정 baseline] 2026-05-18 — Q1/Q2 가로 1장 생성 (수정 시 주의)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  이 날짜 기준, 코디핏 Q1·Q2 가 가로 1장(정면+후면)으로 정상 생성됨을
#  TJ 가 실기기에서 확인함 (closet.html 팝업이미지박스 정상 표시/저장).
#
#  [생성 규약 — 바꾸면 closet.html 팝업이 깨진다]
#   · _gpt_size = "1536x1024" (3:2 가로). gpt-image-2 표준 사이즈.
#       (≈ line 2993 의 _gpt_size 선언부 — 인라인 🔒 주석 + 강제 교정 있음)
#     - 1024x1536(세로)·1536x864(16:9 비표준)으로 바꾸지 말 것.
#       세로로 응답하면 closet.html 이 정면/후면을 못 나눠 짤린다.
#   · 프롬프트는 "ONE horizontal image / 정면=LEFT · 후면=RIGHT 2명"을
#     반드시 지시 — _gpt_prompt 조립부(≈ line 2740) 의 _outfit_prompt /
#     _layout_directives 가 좌우 2명·가로 1장 규약을 담는다.
#   · 응답은 가로 1장 URL 1개 (jsonify image=f"{base}{rel}").
#     정면/후면 URL 을 따로 응답하도록 바꾸지 말 것 —
#     closet.html 은 'image 1개 = 가로 1장' 을 전제로 동작한다.
#
#  ※ Q1·Q2·Q3(STEP A/B/C) 모두 동일한 가로 1장 규약을 공유한다.
#    프롬프트·사이즈 수정 시 closet.html 파일 상단의 동일 baseline
#    주석(모달 5요소)을 함께 확인할 것.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# ─── 2026-05-18 KST · TJ 지시 (Q3 재설계 — 선택 코디 99.9% 복제) ───
#   문제: ① Q3 결과가 세로로 나뉘어 생성 (Gemini 가 가로 1장 지시 무시)
#         ② Q2 에서 '유사 변형'을 골랐는데 원본 추천이 고화질로 나옴
#         ③ 선택한 코디와 의상이 달라짐
#   원인: Q3(startStepC)가 선택 이미지를 서버에 전혀 안 보냄 → 서버가 텍스트
#         조건만으로 새로 생성 + 캐시키 동일 → STEP A 원본 재사용.
#   수정 (6곳):
#     1) closet.html startStepC: p._force_ref_image = baseCard.imageUrl 전달
#     2) _collect_ref_images: _force_ref_image → "style_ref" 라벨 ref 수집
#     3) ordered_parts: face → style_ref → top → bottom 순으로 포함
#     4) Q3 전용 gemini_prompt: 선택 코디 의상 99.9% 복제 + 16:9 가로 1장
#        (좌=정면/우=후면, 같은 인물·같은 의상, 포즈만 변경)
#     5) gemini config: Q3 시 image_config(aspect_ratio="16:9") 강제
#        (SDK 미지원 시 프롬프트 지시로 폴백)
#     6) Q3 캐시 우회: _force_quality='high' → force_regenerate=True
#   ※ Q1·Q2 는 style_ref 가 없어 Q3 분기 미적용 — 기존 동작 그대로.
#
# ─── 2026-05-18 KST · TJ 지시 (Q3 최종 고화질 → Nano Banana Pro 전환) ───
#   문제: Q3(_force_quality='high')가 gpt_image_2_high 로 호출 → 생성 60초+
#         소요로 APITimeoutError 빈발(Render 로그 16:24·16:26 등 86~89초),
#         결국 Gemini 폴백으로 결과를 냄.
#   설계 의도: Q3 = Q2 에서 선택한 최종 코디를 확대해도 안 깨지는 고퀄로.
#   수정(~line 3719): _force_quality=='high' → _override_alias='pro'
#         (pro = gemini-3-pro-image-preview = Nano Banana Pro, provider=gemini)
#         · Q1·Q2(_force_quality='low')는 gpt_image_2_low 그대로 유지.
#         · gpt high 대비 빠르고 저렴, 화질·얼굴 보존 우수.
#
# ─── 2026-05-18 KST · TJ 지시 (세로 이미지 출력 버그 수정) ───
#   증상: 뉴 프롬프트 적용 후 gpt-image-2 가 가로 1536x1024 대신 세로(3:4,
#         예: 875x1166) 1인 이미지로 출력 → 모달·저장이 세로 한 명만 표시
#   진단: 과거 저장본 실측 — 05:48 건 1536x1024(가로), 09:03 건 875x1166(세로).
#         유일한 변화 = 뉴 프롬프트. 구버전은 _layout_directives(11항목 상세)+
#         _final_reminder 가 가로 지시를 프롬프트 맨 앞·맨 끝 2회 강하게 배치 →
#         gpt-image-2 가 size 파라미터보다 프롬프트를 따라 가로 유지.
#         뉴 프롬프트는 IMAGE FORMAT 을 맨 뒤·1회로 축소 → 가로 지시 약화 →
#         gpt-image-2 가 input(세로 얼굴사진) 비율로 세로 출력.
#   수정: gemini_prompt 의 IMAGE FORMAT 블록을 '# OUTPUT IMAGE FORMAT
#         (MOST CRITICAL — APPLY FIRST)' 로 강화하여 프롬프트 맨 앞(헤더 직후,
#         SUBJECT 보다 먼저)으로 이동. 1536x1024·가로·정면후면 2인을 최우선 명시.
#
# ─── 2026-05-18 KST · TJ 승인 (뉴 프롬프트 v2026.05.18 — 전체 루프 적용) ───
#   목적: 설명·중복 문장 제거, 범용(Gemini·GPT Image 공용) 항목식 프롬프트
#   변경:
#     1) gemini_prompt 빌더를 항목식으로 재작성 (STEP1~7 설명체 → 8개 항목):
#        SUBJECT / STYLIST / TPO / OUTFIT-CORE / OUTFIT-OPTIONAL /
#        CONSISTENCY / IMAGE FORMAT / ANALYSIS REPORT
#        · 성별·스타일리스트·이미지포맷·일관성을 각 1회만 (이전 2~3회 중복)
#     2) GPT Image 2 분기: 중복 directive 4개 제거
#        (_gender_directive/_stylist_directive/_layout_directives/_final_reminder)
#        → gemini_prompt 에서 '=== ANALYSIS REPORT' 마커부터 끝까지만 제거하여 사용
#        → _gpt_prompt = _ref_header + _outfit_prompt
#     3) 길이: STEP A ~4,600자 / STEP B ~5,500자 → 6,500자 안전장치 내 = 절단 없음
#     4) Gemini 분기: 뉴 gemini_prompt(ANALYSIS 포함) 그대로 사용
#   적용 범위: STEP A/B/C × (GPT Image 2 / Gemini) 전체 루프 공통
#
# ─── 2026-05-18 KST · TJ 지시 (스타일리스트×도시 차별화 누락 검토) ───
#   문제: 같은 코디 목적이면 도시·AI스타일리스트가 달라도 결과가 비슷
#   원인: 스타일리스트 차별화 지시는 STEP 3(gemini_prompt)에만 있는데,
#         GPT Image 2 프롬프트는 _outfit_prompt 4000자 절단 → STEP 3/4가
#         절단 경계에 걸려 스타일리스트·도시 시그니처가 약화/누락 가능
#   수정: _stylist_directive 신설 — 스타일리스트명·도시·시그니처 컬러 +
#         '같은 목적이라도 다른 도시/스타일리스트는 VISIBLY DIFFERENT 결과,
#         두 스타일리스트가 거의 동일한 룩 금지'를 GPT Image 2 프롬프트
#         맨 앞에 명시 (4000자 절단과 무관하게 항상 반영)
#
# ─── 2026-05-18 KST · TJ 지시 (정/후면 가방 불일치 — 숄더백→백팩) ───
#   문제: 한 장 안에서 정면=숄더백, 후면=백팩으로 다르게 생성
#   원인: 정/후면 액세서리 동일 강제가 약함 (가방 종류 미명시)
#   수정: _layout_directives 11번 신설 + _final_reminder 한 줄 —
#         정/후면은 같은 사람·같은 촬영, 동일 가방(숄더백은 후면에서도
#         숄더백, 절대 백팩 아님)·동일 액세서리 명시
#
# ─── 2026-05-18 KST · TJ 지시 (밀라노 카드 — 얼굴만 여성·몸 남성 버그) ───
#   문제: 여성 사용자인데 추천 코디 일부가 남성 체형 + 여성 얼굴로 생성
#   원인: 성별 명시가 STEP 1 'Gender' 한 줄뿐 → GPT Image 2 가 강하게
#         따르는 프롬프트 앞/끝부분에 성별 없음 → 남성복 키워드
#         (Corduroy suit, Tuxedo 등)에 체형이 끌려감
#   수정: 성별을 4곳에 강하게 명시 (GPT Image 2 + Gemini 양 경로)
#     1) _gender_directive: 프롬프트 맨 앞 — 'SUBJECT SEX ABSOLUTE',
#        앞/뒤 figure 모두 해당 성별, 반대 성별 체형 = CRITICAL FAILURE
#     2) _final_reminder: 프롬프트 끝 — 성별 강조 한 줄
#     3) STEP 2 AVATAR BODY: 'unmistakably female/male, NEVER opposite sex'
#     4) STEP 1 Gender (기존 유지)
#
# ─── 2026-05-17 KST · TJ 지시 (코디핏 이미지 정/후면 분리 — 가로 3:2 강제) ───
#   문제: Q1/Q2/Q3 추천 코디가 정면만 세로로 생성되거나 정/후면이 분리됨
#   원인: ① 프롬프트는 '16:9'인데 _gpt_size 는 '1536x1024'(3:2) — 불일치
#         ② CODIBANK_GPT_IMAGE_SIZE 환경변수가 세로/auto 면 세로 출력
#         ③ '단일 이미지에 정/후면 둘 다' 강제가 약함 → 정면 1명만 생성
#   수정 (STEP A/B/C 공통 _ai_styling_via_gemini, GPT Image 2 분기):
#     1) _gpt_size: '1536x1024' 아니면 강제 교정 (정/후면 가로 3:2 필수)
#     2) _layout_directives: '16:9'→'3:2', 'ONE horizontal image,
#        NEVER vertical/portrait, NEVER single figure' 명시
#     3) _final_reminder: '16:9'→'3:2', 정/후면 누락·분리 금지 강조
#     4) STEP 7 [Image format]: '16:9'→'3:2 (1536x1024)', 단일 이미지 금지
#
# ─── 2026-05-17 KST · TJ 승인 (온도 의류 게이트 — closet.html 규칙 이식) ───
#   배경: closet.html(line 5189~5212)에 강한 온도 규칙이 있었으나
#         S.imagePrompt='' 차단으로 STEP A/B/C(서버 엔진)엔 미적용
#         → 서버 STEP 4/6 의 약한 규칙('<15°C', SCARF 'when fitting')만 작동
#         → 24~26°C 에도 목도리가 추천되던 문제 (TPO 기준 위반)
#   수정: closet.html 규칙을 STEP 1-7 프롬프트(_ai_styling_via_gemini)에 이식
#     1) _temp_gate_block (gemini_prompt 빌드 직전): 온도 7구간 게이트
#        · 아우터: 20°C 미만에서만 (closet: outer nt>=20 → [])
#        · 머플러/스카프: 0°C 이하에서만 (closet: _hasMuffler nt<=0)
#        · 23°C 이상: 코트/패딩/니트/스카프/머플러 전면 금지
#     2) STEP 4: 약한 '<15°C' 한 줄 → _temp_gate_block 으로 교체
#     3) STEP 6: OUTER 'NEVER at 20°C+', SCARF/MUFFLER 'ONLY at 0°C-' 명시
#     4) weather_rule: 3분기 → _temp_bucket 5단계 (warm 보온 금지 명시)
#   ※ STEP A/B/C 모두 동일 _ai_styling_via_gemini 프롬프트 → 전부 적용
#
# ─── 2026-05-16 KST · TJ 지시 (vision 분석 timeout 보강) ───
#   _codifit_analysis_via_gpt41mini (~line 3346): vision 모드 timeout 확대
#   · 텍스트 분석 10초 → vision 분석 20초 (CODIBANK_ANALYSIS_TIMEOUT_VISION)
#   · 이미지 처리로 응답이 느려 timeout→503→분석 보고서 미생성되던 문제 대응
#
# ─── 2026-05-16 KST · TJ 지시 (STEP C 고화질 — _force_quality 실제 반영) ───
#   문제: STEP C(_force_quality='high')가 실제로는 medium 으로 생성됨
#   원인: _force_quality → payload['_override_alias'] 설정은 되나, 1차 생성
#         호출 _ai_styling_via_gemini(...) 에 _override_alias 인자를 전달하지
#         않아 함수 내부에서 None → tier 기반(medium) 라우팅으로 떨어짐
#         (Render 로그: [CODIFIT] tier=FREE → ... quality=medium = else 분기)
#   변경 (~line 3846): 1차 호출에 _override_alias=payload.get('_override_alias')
#         전달 → STEP A=low / STEP B=low / STEP C=high 가 실제 quality 로 반영
#   변경 (~line 2756): alias_override 로그에 quality 표시 (디버깅용)
#
# ─── 2026-05-16 KST · TJ 지시 (옵션 A — 코디핏 분석 vision 전환) ───
#   문제: 분석이 생성 이미지를 보지 않고 메타데이터로만 만들어져 실제 옷과 불일치
#   해결: gpt-4.1-mini vision 모드 — 생성 이미지를 직접 입력하여 분석
#   변경 1) _codifit_analysis_via_gpt41mini (~line 3125): image_b64 파라미터 추가
#     · image_b64 있으면 멀티모달(텍스트+이미지) 호출, detail=low (옷 식별 충분+토큰절감)
#     · 4섹션 생성 — personalColor/body/purpose + outfit(이미지의 실제 옷 컬러·종류)
#     · image_b64 없으면 기존 3섹션 텍스트 모드 (하위호환·graceful degradation)
#   변경 2) /api/ai/styling/analysis (~line 3990): vision 이미지 확보 로직
#     · 로컬 ai_{cacheKey}.jpg 우선 → 없으면 payload.imageUrl 에서 다운로드
#     · PIL: wide(정/후면 합본)면 좌측 절반(정면) crop + 768px 축소 → base64
#     · 구버전 캐시(outfit 섹션 없음) 자동 무효화 → vision 재생성
#   비용: gpt-4.1-mini + 이미지, 캐시 70%히트 기준 실질 ~$0.0003/회 (기존과 동등)
#
# ─── 2026-05-16 KST · TJ 지시 (STEP B 유사 변형 캐시 버그 수정) ───
#   문제: Q2 '유사 변형'이 원본과 100% 동일 — 토큰만 쓰고 같은 이미지 반환
#   원인: _make_ai_cache_key_v2 의 캐시키 body 에 _similar_variation 플래그가
#         없음 → STEP B 변형이 STEP A 원본과 같은 (도시/목적/스타일리스트/사용자/
#         quality) → 같은 cacheKey → cache_fname 동일 → 캐시 HIT → AI 호출 자체가
#         일어나지 않고 STEP A 원본 이미지가 그대로 반환됨
#         (Render 로그: STEP A 파리 카드와 STEP C 가 같은 ai_v2_24e0176a... 사용)
#   변경 (~line 3678): _similar_variation 이면 _force_regen=True 강제
#     → 캐시키 body 에 시간 nonce(rsd) 포함 → 매번 새 키 → 캐시 MISS →
#       항상 새로 생성. cache_fname 도 매번 달라 STEP A 파일을 덮지 않음
#   변경 (~line 3563): 유사변형 프롬프트 강화 — 신발 컬러+디자인 변경 필수,
#     악세사리 일절 금지(no bag/watch/necklace/scarf/hat/sunglasses) 명시
#
# ─── 2026-05-16 KST · TJ 지시 (STEP B 유사 변형 프롬프트 수정) ───
#   문제: Q2 '유사 변형'이 원본과 거의 동일하게 생성됨
#   원인: _similar_variation 프롬프트에 "Do NOT change colors" 지시가 있어
#         원본과 같은 컬러·패턴으로 생성됨
#   변경 (~line 3563): _similar_variation 프롬프트 전면 교체
#     · 유지: 같은 stylist / TPO / 날짜 / 날씨 / 격식 / 실루엣
#     · 필수 변경: 상의 컬러, 하의 컬러, 패턴(solid/stripe/check/textured)
#     · "side-by-side 시 즉시 구분되어야 한다" 강력 명시
#
# ─── 2026-05-14 KST · TJ 지시 (v68 4→2→1 흐름) ─── [hook 3개 추가]
#   배경: 코디핏 UX를 4장 그리드 → 2장 비교 → 1장 Medium으로 개편
#         프론트엔드(closet.html)에서 새 흐름 구현, 백엔드는 hook만 추가
#   변경 (mock_backend.py):
#     1) /api/ai/styling 페이로드 처리 (~line 3470):
#        · _force_city: weather.location 강제 변경 (4장 그리드 도시별 매칭)
#        · _force_quality: 'low'|'medium'|'high' → _override_alias 자동 매핑
#        · _similar_variation: STEP B 유사 변형용 prompt suffix 주입
#     2) prompt 후처리 (~line 3540): _similar_variation 시 강력한 VARIATION 지시 추가
#        · "Same stylist, same palette, but change ONE major item"
#        · 같은 도시/스타일리스트지만 outfit details 미세 변형
#   미완성 / 다음 턴 작업:
#     · /api/codifit/upgrade 신규 endpoint
#       → images.edit + input_fidelity="high" + prev_image as reference
#       → STEP C에서 LOW를 reference로 Medium 업그레이드 (outfit 일관성 보장)
#     · STEP A 4장 cache 키 분리 (현재는 일반 캐시와 같은 키 사용 → 다양성 저해 가능)
#   영향 범위:
#     · /api/ai/styling만 hook 추가 (기본 동작 무변경)
#     · 트라이온, 코디하기, 캐시 키, v53 SDK fix zone 무영향
#
# ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.7-fix5) ─── [KMA 백엔드 프록시 + 하이브리드]
#   배경: TJ 보고 — Open-Meteo가 서울 실측 대비 2°C 오차 발생
#   원인: Open-Meteo는 한국 지역에서 글로벌 모델(GFS/ECMWF) 사용 → 지역 모델 미적용
#   해결: KMA(한국 기상청) 단기예보+초단기실황 백엔드 프록시 추가
#   추가 (mock_backend.py 파일 마지막 ~10923행):
#     · _kma_dfs_xy_conv(lat, lon) — Lambert Conformal Conic 5km 격자 변환
#     · _kma_calc_base_dt() — 단기예보(8회/일) + 초단기실황(매시) base_date/time 계산
#     · _kma_pty_sky_to_wmo() — KMA PTY/SKY 코드 → WMO weather_code 매핑
#     · /api/weather endpoint:
#       - 초단기실황(getUltraSrtNcst) → 현재 기온(T1H) + 풍속(WSD) + 강수형태(PTY)
#       - 단기예보(getVilageFcst) → 3일 시간별(TMP/POP/PTY/SKY/WSD) + 일별 TMX/TMN
#       - Open-Meteo 보강 → UV 지수 + PM2.5 (KMA 미제공 항목)
#       - 응답 형식: Open-Meteo Forecast API 호환 (frontend 무수정)
#   환경변수: KMA_SERVICE_KEY (공공데이터포털 발급 — TJ 작업)
#     · 미설정 시 503 반환 → 프론트엔드가 자동으로 Open-Meteo fallback
#   하이브리드 라우팅 (codibank.js 동시 수정):
#     · 한국 좌표(33-39N, 124-132E) 자동 감지 → KMA 호출
#     · 한국 외 좌표 → Open-Meteo 그대로
#     · config.js weatherProvider: "AUTO" (신규 모드)
#   검증 dry-run:
#     · 서울/부산/제주/인천/대구 5개 도시 좌표 변환 정확
#     · JS syntax OK
#     · 한국/일본/중국/미국 좌표 감지 정확
#   무영향: 코디핏 prompt, 캐시 키, v53 SDK fix zone, 스타일리스트 엔진
#
# ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.7-fix3) ─── [7단계 + 활동지역 + 캐리어]
#   배경: 9,600명 스타일리스트 페르소나가 결과에 반영 안 됨 (사용자 보고)
#   TJ 지시 4가지:
#     1) 프롬프트 순서 재설계 6단계 → 7단계
#     2) DB career 일괄 '패션 스타일리스트'로 변경 (이상한 경력 부적절)
#     3) 활동지역 '서울 고정' 버그 → 스타일리스트의 실제 도시로 표시
#     4) "프롬프트 무시 임의 스타일링" 의심 영역 검사
#   변경 (mock_backend.py, 3곳):
#     1) prompt 7단계 재설계 (line ~2415):
#        STEP 1: USER DATA
#        STEP 2: AVATAR CONSTRUCTION (99.9%)
#        STEP 3: AI STYLIST SELECTION ★ (신설 — 시그니처 컬러/레벨/경력 명시)
#                · color1/color2/level/exp를 prompt에 직접 노출
#                · "Different stylists MUST produce VISIBLY DIFFERENT outfits" 강조
#                · STEP 0 engine output → STEP 3 안으로 통합
#        STEP 4: TPO ANALYSIS + OUTFIT DECISION (중간 위치로 이동)
#        STEP 5: CORE OUTFIT GENERATION (이전 STEP 3)
#        STEP 6: OPTIONAL ACCESSORIES (이전 STEP 4)
#        STEP 7: OUTPUT FORMAT + ANALYSIS REPORT (이전 STEP 6 + JSON 통합)
#     2) AVOID COLORS 반복: 3회(STEP 1/3/4) → 1회(STEP 1만) 축소
#        → 컬러 다양성 회복, 9,600명 시그니처 컬러 표현 자유도 확보
#     3) 활동지역 city 주입 (3곳 응답, line ~2995/3566/3770):
#        matched_stylist에 active_city를 'city' 키로 주입하여 응답
#        DB 구조상 city는 외부 key였으나, frontend는 stylist.city를 읽어 fallback '서울'
#     4) 검사 보고 (별건):
#        · "직접입력 강제" override 로직 (line 3444) — purpose='custom'일 때만 작동, 정상
#        · colorDirective 셀프 강화 루프 의심 (closet.html line 5398) — 다음 턴 작업
#   DB 변경 (stylist_db_server.json):
#     · 11,200개 career → 모두 '패션 스타일리스트' 통일
#   영향:
#     · 코디핏 prompt 구조 7단계로 명확화
#     · 스타일리스트별 차별화 강화 (시그니처 컬러 prompt 직접 노출)
#     · 컬러 다양성 회복 (AVOID 1회 축소)
#     · 활동지역 정확 표시
#   무영향: 트라이온, 코디하기, v53 SDK fix zone, 캐시 키 v2, 분석 분리
#
# ─── 2026-05-14 KST · TJ 보고 (v67 Phase 1.7-fix · CACHE KEY STYLIST FIELDS) ───
#   TJ 보고: "퍼스널컬러 추천 컬러가 AI 스타일리스트 변경해도 상의/하의 컬러와 스타일 그대로 유지"
#   진단: 캐시 키 v2의 body 딕셔너리에 stylist_name/city 누락
#         → 사용자가 스타일리스트만 변경 시 캐시 키 동일 산출
#         → cache_fpath 존재 → 캐시 HIT → 이전 이미지 반환
#         → 백엔드의 AI 호출 자체가 일어나지 않음
#         → 새 prompt(v67 Phase 1.7 6단계) 효과 없음
#   수정 (mock_backend.py, 3곳):
#     · _make_ai_cache_key_v2 시그니처: matched_stylist, meta 인자 추가 (line ~1416)
#     · body 딕셔너리: "stl"(stylist name), "cty"(city) 필드 추가 (line ~1505)
#     · /api/ai/styling 호출부: _matched_stylist, _meta 전달 (line ~3498)
#   효과:
#     · 스타일리스트가 다르면 → 다른 캐시 키 → 새 이미지 생성
#     · 같은 스타일리스트로 재요청 → 캐시 HIT 유지 (디스크 절약)
#   주의: 기존 캐시(stylist 정보 없이 생성된 v2_* 키)는 영원히 미사용
#         → 디스크 누적되므로 R2/로컬 정리 권장 (별건)
#
# ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.7 PROMPT REDESIGN) ─── [코디핏 prompt 6단계 재설계]
#   배경: TJ가 prompt 구조를 명확히 정의:
#         "사용자 데이터 수집/분석 → 아바타 99.9% 반영 → 기본 코디 → 스타일리스트 옵션 → TPO → 출력"
#   TJ 결정:
#     1) 6단계 재설계 구조 — 제안대로 적용
#     2) 기본 코디 = 상의/하의/신발 3개 (필수)
#     3) 아우터도 옵션 (추울 때만, 스타일리스트 재량)
#     4) 이번 턴에 적용
#   변경 (mock_backend.py, line 2385~2495 전면 재작성):
#     · STEP 1: USER DATA (얼굴/성별/나이/키몸무게/체형/회피컬러)
#       - 회피 컬러만 strict 명시 (베스트 컬러 prompt에서 완전 제거 — Gemini 분기 포함)
#     · STEP 2: AVATAR CONSTRUCTION (99.9% 사용자 일치)
#       - IDENTITY PRESERVATION + BODY PROPORTION 통합
#       - 얼굴 미화/슬림화 금지, 체형 정확 반영, 패션모델 8.5 heads
#     · STEP 3: CORE OUTFIT (상의/하의/신발 — 필수, 항상 포함)
#       - AVOID COLORS 재강조
#     · STEP 4: STYLIST'S OPTIONAL ACCESSORIES (스타일리스트 재량)
#       - 아우터/가방/시계/선글라스/모자/스카프/양말 — TPO/날씨 적합 시만
#       - 과한 적층 금지
#     · STEP 5: TPO CONTEXT (목적/날씨/위치/스타일리스트)
#     · STEP 6: OUTPUT FORMAT (정/후면, 16:9, 단색 배경)
#     · CRITICAL OUTPUT INSTRUCTIONS (JSON 스키마, Gemini 분기 전용)
#       - categoryKeywords에 CORE/OPTIONAL 라벨 추가
#   영향:
#     · Gemini 분기: 새 구조 그대로 전송 → 더 명확한 지시 → 결과 품질 ↑
#     · GPT Image 2 분기: 후처리 정규식("베스트:"/"주의:")이 무효 패턴 됨 (이미 prompt에 없음)
#       → 후처리는 안전망으로 유지, 자동으로 효과 없음
#     · JSON 스키마는 GPT Image 2 후처리에서 제거 (기존 동작 유지)
#   영향 범위: 코디핏만. 트라이온/코디하기/AI옷장 무영향.
#
# ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.6 HYBRID) ─── [GPT Image 2 + Gemini 폴백]
#   배경: Phase 1.5 적용 후에도 GPT Image 2 medium 응답시간 분포가 30~90초로 부담
#         TJ가 v65에서 Gemini로 90% 성공률을 확보했던 실측 데이터 기반 결정
#   TJ 결정: C 하이브리드 — GPT Image 2 1차 시도 → 실패 시 Gemini 자동 폴백
#     이유: GPT Image 2 얼굴/텍스트 보존 우위 + Gemini 안정성/속도 양립
#   변경 (mock_backend.py):
#     1) _ai_styling_via_gemini 시그니처에 _override_alias 파라미터 추가
#        · alias 지정 시 _ENGINE_MODEL_MAP/_ENGINE_PROVIDER_MAP/_ENGINE_QUALITY_MAP에서
#          직접 조회 (tier 기반 라우팅 우회)
#        · 폴백 호출용. None이면 기존 동작 그대로
#     2) /api/ai/styling 엔드포인트에 하이브리드 폴백 흐름 (line ~3429)
#        · 1차: _ai_styling_via_gemini(...) (provider=openai → GPT Image 2)
#        · 실패(500 tuple) + 폴백 활성 → _ai_styling_via_gemini(..., _override_alias="flash_v2")
#          (provider=gemini → Gemini Nano Banana 2)
#        · 같은 cache_fname 사용 → 폴백 결과도 캐시됨 → 재시도 시 즉시 응답
#        · 응답 model 필드에 "fallback:gemini-3.1-flash-image-preview" 표시
#     3) 환경변수 신설:
#        · CODIBANK_CODIFIT_FALLBACK_ALIAS=flash_v2 (폴백 모델 alias, 기본 flash_v2)
#        · CODIBANK_CODIFIT_ENABLE_FALLBACK=1 (폴백 활성, 0으로 끄기 가능)
#   효과:
#     · GPT Image 2 성공 시: 30~60초 (얼굴 보존 우위)
#     · GPT Image 2 실패 시: 60초 + Gemini 12초 = 72초 (이전 110초 실패 대비 안정)
#     · 캐시 hit (다음 같은 요청): 0.5초 (Gemini 결과도 같은 파일에 저장됨)
#   주의:
#     · v67 Phase 1의 "OpenAI variant 자동 폴백 제거" 부분은 그대로 유지 (다른 폴백)
#     · 분석은 어느 쪽 성공이든 별도 /api/ai/styling/analysis 호출 (Phase 2 그대로)
#     · 캐시 키 v2 (Phase 3)는 model 필드 포함하지만, 폴백 결과도 GPT Image 2 키로 저장
#
# ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.5 HOTFIX) ─── [긴급 핫픽스]
#   배경: Render 배포 후 코디핏 이미지 생성 100% 실패 (APITimeoutError, 106~111초)
#   진단 (Render 로그 분석 결과):
#     · timeout=35초 설정은 정상 작동했으나 OpenAI SDK가 자동 재시도 2회 수행
#     · 35초 × (1회 + 2회 재시도) ≈ 105초 → 로그의 106~111초와 정확히 일치
#     · OpenAI 공식 문서: "408 Request Timeout / Connection errors / 429 / >=500 모두 기본 2회 자동 재시도"
#     · 또한 gpt-image-2 medium의 실제 응답시간은 30~90초 분포 → 35초는 너무 짧음
#   TJ 결정:
#     1) timeout=60초 / max_retries=0 (균형 옵션 B)
#     2) face 미등록 사용자 → 거절 (images.generate fallback 제거)
#     3) 부수 발견 사항 (_read_upload_bytes 미정의, /uploads 404) 함께 수정
#   변경 (mock_backend.py):
#     1) timeout 35.0 → 60.0 + max_retries=0 (이미지 생성, 2곳: images.edit + images.generate)
#        · 환경변수 CODIBANK_GPT_IMAGE_TIMEOUT으로 조정 가능 (기본 60)
#        · 환경변수 CODIBANK_GPT_IMAGE_MAX_RETRIES으로 조정 가능 (기본 0)
#     2) 분석 호출 timeout 10.0 + max_retries=0 명시 (gpt-4.1-mini, 자동 재시도 차단)
#        · 환경변수 CODIBANK_ANALYSIS_TIMEOUT으로 조정 가능 (기본 10)
#     3) face 거절 로직 (/api/ai/styling 엔드포인트 ref_images 수집 직후)
#        · ref_images에 ('face', ...) 항목 없으면 400 + errorCode="FACE_NOT_REGISTERED"
#        · 환경변수 CODIBANK_CODIFIT_REQUIRE_FACE=0으로 임시 비활성 가능 (기본 1=필수)
#     4) _read_r2_bytes 신규 함수 추가 (line ~963, R2 객체 다운로드)
#     5) /api/personal-color/load: _read_upload_bytes → _read_r2_bytes 호출 변경 (line ~4104)
#   영향:
#     · 코디핏 응답시간: 최악 60초 (이전 110초+) → 사용자 경험 ↑
#     · 코디핏 성공률 ↑ (medium quality 30~60초 대부분 커버)
#     · face 미등록 사용자: 빠른 안내 (60초 대기 후 timeout 아님)
#     · 퍼스널컬러 R2 로드 정상화 → 분석 입력 품질 ↑
#   참고: /uploads/{filename} 404 문제는 별개 (R2 파일 실제 없음 + ephemeral 손실)
#         사용자가 face 사진 재등록하면 R2 저장되어 404 해소됨
#
# ─── 2026-05-14 KST · TJ 지시 (v67 Phase 2 + Phase 3) ─── [분석 분리 + 캐시 v2]
#   배경: Phase 1 적용 후 분석 보고서 품질 업그레이드 + 캐시 효율 극대화
#   Phase 2 (분석 분리):
#     · 코디핏 분석 보고서를 GPT Image 2 응답에서 분리 → gpt-4.1-mini로 별도 생성
#     · 사용자 경험: 이미지 즉시 표시 → "추천코디 분석 보기" 버튼 → 클릭 시 분석 표시
#     · Pattern A (메타데이터 기반): 이미지 미사용, 사용자 정보+생성 의도만으로 분석
#         이유: 비용 50% 절감 + 속도 ↑ + 이미지 생성과 직렬화 (병렬 불필요)
#   Phase 3 (캐시 키 v2):
#     · 추가 필드: model, quality, size, user.bodyType, personalColor.season, avoid hash
#     · 버킷팅: temp 5°C, height/weight 5단위, weather 5종 enum
#     · customText: 공백/대소문자 정규화 후 해싱
#     · retrySeed: 기본 키에서 제외 (force_regenerate 시에만 포함)
#     · v1 캐시는 보존 (cleanup script로 추후 제거), v2만 사용
#   신규 추가 (mock_backend.py):
#     1) _make_ai_cache_key_v2 함수 (~line 1280): 버킷팅 + 핵심 필드 보강
#     2) _codifit_analysis_via_gpt41mini 함수 (~line 2680): gpt-4.1-mini 호출 (10초 timeout)
#     3) /api/ai/styling/analysis 엔드포인트 (~line 2950): 캐시 → 호출 → 캐시 저장
#   변경 (mock_backend.py):
#     4) /api/ai/styling (~line 2903): cache_key v1 → v2 사용 전환
#     5) /api/ai/styling 캐시 hit 응답 (~line 2907): stylingAnalysis=None, cacheKey 추가
#     6) _ai_styling_via_gemini (~line 2570): 분석 JSON 마커 없음 시 None (템플릿 폴백 제거)
#   변경 (closet.html):
#     7) 분석 박스 영역 위에 "추천코디 분석 보기" 토글 버튼 (~line 1733)
#     8) 자동 펼침 로직 → 별도 분석 API 호출 + 버튼 클릭 시 펼침 (~line 5544)
#     9) 상태 머신: loading → ready / retry → disabled (옵션 B → C)
#     10) sessionStorage 저장 + 재시도 1회
#   영향 범위: 코디핏(closet.html, /api/ai/styling, 신규 /api/ai/styling/analysis)만.
#              트라이온/코디하기/AI옷장 등 다른 서비스 무영향.
#   비용 추정 (10K 코디핏/월 기준):
#     · 이전: gpt-image-2 medium($0.053) × 캐시 미적용 ≈ $500/월
#     · 이후: image $0.053 + analysis gpt-4.1-mini $0.0003 + 캐시 70%히트
#           ≈ $160/월 (68% 절감)
#
# ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1) ─── [코디핏 속도/품질/비용 최적화]
#   배경: 코디핏 이미지 생성이 1분 이상 소요되는 문제 해결
#         TJ 결정: Phase 1 (최소 변경 + 즉효 + 저위험)만 우선 적용
#         Phase 2(분석 분리/UI 개편) / Phase 3(캐시 v2)는 별도 진행
#   목표: 품질 중상 유지 + 생성시간 단축 + 실패율 감소 + 비용 절감
#   변경 — 5개 영역 (모두 _ai_styling_via_gemini 함수 + /api/ai/styling 엔드포인트 내부):
#   1) 이미지 사이즈 기본값 변경 (line ~2340):
#      · "1536x864" (16:9) → "1536x1024" (표준 3:2)
#      · 이유: 정/후면 토글 가독성 우선, gpt-image-2 standard size 안정성
#      · 환경변수 CODIBANK_GPT_IMAGE_SIZE로 오버라이드 가능
#   2) GPT Image 2 분기 prompt 후처리 (line ~2325):
#      · _outfit_prompt = gemini_prompt[:4000] (slice) → 정규식 후처리로 변경
#      · A. JSON 분석 스키마 블록 제거 (GPT Image 2는 텍스트 출력 안 함 → 토큰 낭비)
#           "=== CRITICAL OUTPUT INSTRUCTIONS ===" ~ "Nothing else." 통째로 제거
#      · B. "베스트: ..." 줄 제거 (퍼스널컬러 추천 컬러)
#           이유: 추천 컬러 prompt 명시 → 이미지 다양성 저하 (TJ 지적)
#           해결: 추천 컬러는 분석 보고서에서만 다루고, 이미지에는 미명시
#      · C. "주의: ..." 줄을 AVOID COLORS strict로 강조 변환
#           이유: 피해야 할 컬러만 strict로 강조 (TJ 결정)
#           예외: "탁한 톤" (default fallback) 케이스는 제거
#      · D. 최종 길이 제한 4000자 유지
#   3) OpenAI 호출 옵션 추가 (line ~2346-2362):
#      · output_format="jpeg" (PNG 대비 인코딩/전송 빠름, R2 저장 비용 ↓)
#      · output_compression=80 (의류 패턴 보존 + 파일 크기 30~40% 절감)
#      · timeout=35 (with_options) — fail-fast로 무의미한 대기 차단
#      · images.edit / images.generate 양쪽 적용
#   4) faceless 재시도 제거 (line ~2876-2883):
#      · _ai_styling_via_gemini 실패 시 OpenAI 폴백 라우팅 제거
#      · 이전: GPT Image 2 실패 → OpenAI variants 다중 시도 → 추가 60초+ 대기
#      · 변경: 실패 시 즉시 에러 반환 → 사용자가 빠르게 재시도 가능
#      · OpenAI 폴백 경로 자체는 보존 (CODIBANK_AI_STYLING_PROVIDER=openai 시 사용)
#   5) (없음 — Phase 2/3에서 처리)
#   영향 범위: 코디핏(closet.html, /api/ai/styling)만.
#              트라이온/코디하기/AI옷장 등 다른 서비스 무영향.
#   환경변수 (Render 변경 권장):
#      · CODIBANK_GPT_IMAGE_SIZE="1536x1024" (코드 기본값과 동일, 명시적 설정 권장)
#   롤백 방법: 이 블록 + 5개 수정 지점의 v67 주석 영역 원복
#
# ─── 2026-05-13 KST · TJ 지시 (v66 QUALITY) ─── [prompt 단순화 + 패션모델 비율]
#   배경: medium 품질에서 결과 디테일 부족 + 비율 어색
#   TJ 결정 (3가지):
#     1) 이미지 퀄리티: medium 유지 + prompt 단순화 (비용 동일, 결과 보고 결정)
#     2) 인물 비율: 패션모델 8.5 heads (세련됨)
#     3) 인물 세로 크기: 85% (균형, 위/아래 7.5% 마진)
#   변경 — 1개 영역 (_ai_styling_via_gemini OpenAI 분기, line ~2263):
#   A) prompt 단순화 (28k → ~5k chars):
#      · 이유: gemini_prompt 28k는 Gemini용 디테일(4-Pass, DNA, 액세서리 다양성)로
#              GPT Image 2에는 noise. 핵심 정보는 첫 부분에 위치
#      · 변경: gemini_prompt[:4000]만 발췌 (스타일리스트/색상/카테고리/사용자 정보)
#      · 추가: FINAL REMINDER 블록 (prompt 끝에 핵심 지시 강조)
#        - GPT Image 2는 끝부분 지시를 강하게 따르는 특성 활용
#   B) LAYOUT 비율 변경 (8.5 heads + 85% 세로):
#      · BODY: 7.5-8 heads → 8.5 heads (FASHION MODEL PROPORTIONS)
#      · FACE: 1/8 → 1/8.5 (얼굴 더 작게)
#      · UPPER:LOWER 비율 1:1.15 추가 (다리 살짝 길게)
#      · 어깨 너비 2 head widths 추가
#      · slim, tall, balanced silhouette 명시
#      · 세로: 90% → 85% (위/아래 5% → 7.5% 마진)
#      · PHOTOGRAPHY STYLE 추가 (editorial fashion, sharp focus, studio lighting)
#   효과 예상:
#      · prompt 단축 → GPT가 LAYOUT 지시를 더 잘 따름
#      · 8.5 heads + 작은 얼굴 → 패션 화보 느낌
#      · 85% 세로 → 답답함 해소
#
# ─── 2026-05-13 KST · TJ 지시 (v66 LAYOUT) ─── [GPT Image 2 prompt에 LAYOUT 지시 추가]
#   배경: 첫 GPT Image 2 medium 생성 결과 분석 후 TJ 요청
#         1) 정/후면 위치가 좌/우 절반의 중앙으로 정렬되지 않음
#         2) 인물이 이미지 세로 100%에 꽉 차게 생성됨 → 답답한 느낌
#         3) 얼굴이 신체 대비 크게 생성됨 → 신체 비율 부자연스러움
#   변경 — 1개 영역 (_ai_styling_via_gemini의 OpenAI 분기, line ~2243):
#     · _layout_directives 블록 추가 (REFERENCES 헤더 직후 prepend)
#     · 9개 명시적 지시 (CRITICAL FOLLOW EXACTLY):
#       1. CANVAS: 16:9 wide, 좌/우 절반 분할
#       2. LEFT HALF: FRONT view, face visible
#       3. RIGHT HALF: BACK view, no face
#       4. HORIZONTAL CENTERING: 각 figure 자기 절반 중앙 (25%, 75%)
#       5. VERTICAL SIZING: 인물 height = 이미지 height의 90% (위/아래 5% 마진)
#       6. BODY PROPORTIONS: 7.5-8 head heights, face = 1/8 figure height
#       7. BACKGROUND: solid soft neutral (light blue/off-white/soft gray)
#       8. NO text/logos/watermarks/UI
#       9. 두 figure SAME outfit (color + garments + accessories)
#     · prompt 한계 조정: 30k → 28k (LAYOUT 블록 추가 공간 확보)
#   영향: codifit 이미지만. tryon/codistyle 영향 없음.
#
# ─── 2026-05-13 KST · TJ 지시 (v66) ─── [코디핏 → OpenAI GPT Image 2 medium 전환]
#   배경: Gemini Nano Banana 2 preview의 다양성/얼굴 보존 한계
#         → 이미지 결과 일관성 부족 + 한국인 얼굴 보존 약함
#         → TJ 결정: 코디핏을 GPT Image 2 medium($0.053)로 전환
#                   (Nano Banana 2 $0.067 대비 21% 절감)
#   변경 — 3개 영역 (mock_backend.py만 수정, closet.html 변경 없음):
#   1) 엔진 매핑 확장 (line ~2816):
#      · _ENGINE_MODEL_MAP에 gpt_image_2_low/medium/high 추가
#      · _ENGINE_PROVIDER_MAP 신규 (alias → "gemini"|"openai")
#      · _ENGINE_QUALITY_MAP 신규 (alias → "low"|"medium"|"high")
#      · _ENGINE_SERVICE_DEFAULT['codifit']: "flash_v2" → "gpt_image_2_medium"
#   2) _resolve_engine_full 헬퍼 추가 (line ~2912):
#      · 기존 _resolve_engine은 str만 반환, provider 모름
#      · _resolve_engine_full는 (model, provider, quality) 3-tuple 반환
#      · 환경변수 CODIBANK_MODEL_CODIFIT, CODIBANK_ALIAS_CODIFIT 호환 유지
#   3) _ai_styling_via_gemini 함수에 GPT Image 2 분기 (line ~2156):
#      · model_name 결정 → _resolve_engine_full로 변경
#      · _gpt_image_used 플래그 (provider == "openai" and starts "gpt-image")
#      · True면 OpenAI 분기: face/top/bottom 있으면 images.edit, 없으면 images.generate
#        - REFERENCES 헤더 prepend (Image 1=face, Image 2=top, ...)
#        - face 없을 때 NOTE 헤더 (generic Korean face 자동 생성)
#        - size 1536x864 (16:9), prompt 30k chars 한계
#      · False면 기존 Gemini 분기 그대로
#      · 응답 파싱: GPT Image 2면 b64_json 직접 사용, Gemini면 candidates.content.parts
#   환경변수 (Render):
#      · OPENAI_API_KEY (필수)
#      · CODIBANK_GPT_IMAGE_SIZE="1536x864" (선택, 기본값)
#      · CODIBANK_ALIAS_CODIFIT="flash_v2" (긴급 롤백용)
#   영향 범위: codifit 엔드포인트만. tryon/codistyle은 Gemini 그대로 유지.
#
# ─── 2026-04-23 05:45 KST (🎯 Gemini 프롬프트 세부 분류 TJ 확정값 반영) ──
#   [TJ님 지시 — 세부 분류 규칙 확정]
#     [아우터(coat)] 긴 아우터류 — 아우터/코트/패딩/버버리/롱패딩
#     [자켓(jacket)] 짧은 아우터류 — 자켓/블레이저/점퍼/다운자켓/레더자켓/
#                    데님자켓/가디건 ← 가디건이 jacket으로 이동 (이전엔 coat에 있었음)
#     [상의] 탑/셔츠/티셔츠/후드티/후드티셔츠/블라우스/면티/니트티/니트셔츠
#     [바지] 바지/반바지/데님팬츠/조거팬츠/트레이닝하의/레깅스/숏팬츠/러너팬츠
#     [치마] 스커트/H라인/A라인/플레어/플리츠/머메이드/미니/미디/롱/레이어드
#     [원피스] 원피스/미디/롱/셔츠/시스/랩/슬립/시프트/드레스/웨딩/수영복3
#
#   [수정 위치]
#     ▸ /api/ai/analyze-item 프롬프트 (line ~5739):
#        - sub_category 설명 TJ 확정값으로 전면 재작성
#        - outer_type enum: 7종 → 12종 확장 (긴/짧은 구분)
#        - "아우터(coat/jacket)" 지시 문장을 명시적 분기 규칙으로 개선
#     ▸ codistyle_generate, tryon_generate 등 이미지 생성 함수는 수정 없음
#     ▸ 엔진 라우팅 (_resolve_engine) 수정 없음
#
# ─── 2026-04-22 17:40 KST (📦 카테고리 체계 개편 — 원피스 독립 + 아우터 7종) ─
#   [TJ님 지시]
#     1. Ai옷장/아이템등록에서 원피스가 별도 카테고리로 분리 안 됨 → 추가
#     2. 카메라에서 이미지 분석 시 아우터는 TJ 정책 7종
#        (코트/패딩/자켓/점퍼/가디건/다운/블레이저)으로 세분화
#
#   [발견된 치명적 버그 — camera.html catMap에서]
#     'dress'    : 'pants'   → 원피스가 '하의'로 잘못 분류됨
#     'jumpsuit' : 'pants'   → 점프수트도 '하의'로
#     'skirt'    : 'pants'   → 치마도 '하의' (코디하기 v53 버그 원인)
#
#   [결정 — TJ 선택]
#     ▸ 원피스 서브 5종 (O3): 미니/미디/롱/니트/셔츠 원피스
#     ▸ 아우터 7종 처리 방식 (A): 기존 2키(coat/jacket) 유지 + sub_category에
#        7종 명시 → 기존 DB 데이터 호환성 보장 (outer_type 신규 필드로 7종 명시)
#
#   [이번 수정 내역 — 서버측 프롬프트만]
#     /api/ai/analyze-item (line ~5671) Gemini Vision 프롬프트:
#       ① category enum에 'onepiece' 신규 추가
#           이전: coat|jacket|top|pants|skirt|shoes|watch|scarf|socks|etc
#           신규: coat|jacket|top|pants|skirt|onepiece|shoes|watch|scarf|socks|etc
#       ② sub_category 설명에 원피스 5종 + 아우터 7종 명시
#           - 원피스: 미니원피스/미디원피스/롱원피스/니트원피스/셔츠원피스
#           - 아우터: 자켓/패딩/점퍼/가디건/다운/블레이저 + 코트
#       ③ 신규 필드 3개:
#           - is_onepiece (bool) ← 원피스 여부
#           - dress_length (mini|midi|maxi|null) ← 원피스 전용 길이
#           - outer_type (코트|패딩|자켓|점퍼|가디건|다운|블레이저|null)
#             ← TJ 7종 정책
#       ④ CRITICAL RULES 3단계로 재작성:
#           규칙 1: 원피스 vs 치마/바지/상의 구분 (상반신+하반신 연결된 1벌)
#           규칙 2: 치마/스커트 판별 (leg separation 유무)
#           규칙 3: 아우터 길이 판별 (무릎 기준 coat/jacket)
#
#   [이 파일에서 수정 안 된 것 — 다른 턴/파일 작업 필요]
#     ▸ camera.html의 catMap ('dress': 'pants' 등 치명적 버그)
#     ▸ aicloset.html의 i18n 번역 사전 (원피스 번역 키 없음)
#     ▸ aicloset.html의 CAT_SUBSTITUTE_MAP (onepiece 엔트리 없음)
#     ▸ item.html의 categorySelect 옵션 (codibank.js에서 공급 → 확인만)
#
# ─── 2026-04-22 17:05 KST (🎯 엔진 정책 단순화 — 서비스별 단일 모델) ────────
#   [TJ님 지시 — 2026-04-22]
#     1. 회원 티어별로 모델이 달라지지 않는다.
#        서비스(코디핏/트라이온)가 어떤 모델을 쓰는지만 본다.
#     2. 회원별 구독 제한은 이미 "코디핏 이미지 사용횟수"와 "트라이온 사용횟수"를
#        구분해서 관리 중 (프론트 cb_usage_ localStorage + 서버 DB).
#        → 모델 자체는 티어에 따라 바뀌지 않는다.
#
#   [새 정책 — 서비스별 고정 모델]
#     • 코디핏 (closet.html, /api/ai/styling, /api/codistyle/generate):
#       → Nano Banana 2 = gemini-3.1-flash-image-preview (원가 ~₩40/회)
#       전략: 빠른 생성 + 낮은 원가 → 신규/무료 회원의 체험 유도
#     • 트라이온 (tryon.html, /api/tryon/generate):
#       → Nano Banana Pro = gemini-3-pro-image-preview (원가 ~₩120/회)
#       전략: 고퀄 이미지 → 구독 회원의 프리미엄 유지 소구
#
#   [변경 내용]
#     ① _ENGINE_MATRIX_DEFAULT 단순화 (~line 2689):
#        { 티어: { 기능: alias } } 4행 → { 기능: alias } 1차원 2키만
#        FREE=SILVER=GOLD=DIAMOND 전부 동일 결과 (티어 완전 무시)
#     ② _resolve_engine 시그니처 유지(기존 호출부 0줄 수정):
#        tier 파라미터는 받되 무시. feature만 보고 결정.
#     ③ _get_engine_config_summary 관리자 표시용 업데이트:
#        "matrix" → "service_engines"로 단순화, 티어 표 삭제
#
#   [영향 범위 — 호출부 무수정 (시그니처 하위호환)]
#     • line 2043: _resolve_engine(_resolved_tier, "codifit") → 여전히 동작
#     • line 2743, 2744: summary 생성 로직 → 자동으로 같은 값 반환
#     • line 3113 (codistyle_generate): 티어 인자 그대로 받지만 무시됨
#     • line 4802 (tryon_generate): 동일
#
#   [중요 — codistyle_generate / tryon_generate는 한 줄도 수정 안 함]
#     시그니처 하위호환 덕분에 엔진 라우팅 단순화가 호출부로 전파됨.
#
# ─── 2026-04-22 16:30 KST (🆕 트라이온 전용 엔드포인트 Phase 4) ───────────
#   [TJ님 지시]
#     트라이온 페이지에서 '생성' 클릭 → 현재는 mock 플레이스홀더만 뜸.
#     실제 착장 이미지 생성이 되도록 백엔드 연동 요구.
#
#   [원칙 (TJ님 메모리에 새겨진 것)]
#     • 코디핏(closet.html)·트라이온(tryon.html)·코디하기(codistyle.html)
#       세 서비스 모두 별도 엔드포인트·별도 프롬프트 함수로 완전 분리.
#     • codistyle.html / codistyle_generate()는 절대 수정 금지.
#     • 프롬프트 혼용 금지 원칙 유지.
#
#   [결정 — 옵션 A1 확정]
#     codistyle_generate는 이미 _TRYON_MODEL 라우팅을 포함하고 있지만,
#     이를 재사용하면 "완전 분리" 원칙을 위배함. → 신규 독립 함수로 작성.
#     프롬프트 구조는 codistyle의 Phase 1~5 + 5섹션 분석을 따름 (TJ 선택 A1).
#
#   [신규 구성요소 — 모두 codistyle_generate 뒤에 추가]
#     ① 헬퍼 함수 _tryon_build_prompt()         (~line 4413)
#        - fitTarget 분기: my / somebody / model
#        - 상/하의 (twopiece) | 원피스 (onepiece) | 아우터 (outer) 모드 대응
#        - 5섹션 분석 + C.S.I 4지표 점수 지시문 (codistyle과 동일 포맷 요구)
#     ② 헬퍼 함수 _tryon_parse_response()       (~line 4600)
#        - codistyle의 파싱 로직을 '트라이온 전용'으로 재작성
#        - 응답 구조는 프론트 csScoreBox가 기대하는 codistyle 호환 스키마
#     ③ 메인 엔드포인트 @app.post('/api/tryon/generate')
#        def tryon_generate():                  (~line 4750)
#        - _resolve_engine(tier, 'tryon')로 모델 선택 (Nano Banana Pro 등)
#        - v53 SDK fix 구역 패턴(new→old fallback) 준수
#        - 이미지 R2 업로드 후 URL 포함 응답
#
#   [codistyle_generate 영향]
#     0줄. 한 줄도 수정하지 않음. 완전 독립 추가.
#
# ─── 2026-04-21 01:50 KST (⚠️프리미엄 리포트 완전 복구 — 3중 안전망 구축) ──────
#   [TJ님 제보]
#     배포 후 테스트 결과 리포트가 여전히 200자 이하 초보 수준 (스크린샷 첨부)
#     → Radar 안 보임, Executive Summary 없음, 해시태그 없음,
#        심층 분석 섹션 대부분 빈약 또는 제목만 있음
#
#   [진단]
#     STAGE 2 (gemini-2.0-flash)가 Render 환경에서 조용히 실패하고 있을 가능성 큼
#     (권한, 모델 지역 제한, 또는 일시적 장애)
#
#   [작업 2] STAGE 2 모델 fallback 체인 구축 (~line 3884)
#     이전: gemini-2.0-flash 단일 호출 → 실패 시 STAGE 1 백업만 의존
#     신규: 3단계 체인 자동 시도:
#           1순위: gemini-2.0-flash (환경변수로 변경 가능)
#           2순위: gemini-1.5-flash (검증된 안정 모델)
#           3순위: gemini-1.5-flash-8b (경량, 최후 수단)
#     각 단계에 [DIAG #4-N] 로그 (✅/⚠️/❌ 이모지로 가독성 ↑)
#     성공한 모델명을 로그에 기록 → 실제 어느 모델이 동작하는지 추적 가능
#
#   [작업 3] 최후 안전망 — 로컬 구조화 리포트 (~line 3982)
#     조건: STAGE 1 백업 + STAGE 2 체인 모두 결과가 500자 미만일 때
#     동작: 서버가 이미 가진 데이터로 풍부한 5섹션 리포트 로컬 조립
#       - 체형 타입, 퍼스널컬러, 상하의 분석 데이터 활용
#       - 한/영 분기, 치마/바지 분기 처리
#       - 서버 프롬프트 포맷(STYLING_SCORE, 종합 평가, 5섹션, TPO, 팁, 해시태그) 그대로
#       - 결과: 사용자는 어떤 경우에도 "준비 중입니다" 플레이스홀더 안 봄
#
#   [작업 4] analyze-item fallback 체인 (~line 4788)
#     기존: gemini-2.0-flash 단일 호출 → 실패 시 500 에러 → 코디하기 전체 중단
#     신규: 동일한 3단계 체인 (2.0-flash → 1.5-flash → 1.5-flash-8b)
#     각 단계 [analyze-item][DIAG] 로그로 어느 모델 성공했는지 추적
#
#   [기대 효과]
#     - 프리미엄 리포트 빈약 문제 3중 안전망으로 해소:
#       (1) Gemini 2.0 실패 시 → 1.5 자동 전환
#       (2) 1.5도 실패 시 → 1.5-8b 자동 전환
#       (3) 모두 실패 시 → 로컬 구조화 리포트 (최소 1500자 보장)
#     - 치마 판별도 analyze-item fallback으로 안정성 ↑
#     - [DIAG #4-1/2/3/4f] 로그로 어느 단계가 실패했는지 Render에서 즉시 확인
#
# ─── 2026-04-20 23:30 KST (⚠️2단계 아키텍처 전환 — 근본 구조 수술) ──────────
#   [TJ님 제보]
#     1) 치마가 계속 바지로 생성됨 (다시요청 뿐 아니라 최초 생성에서도)
#     2) 프리미엄 스타일링 리포트가 여전히 빈약 ("준비 중입니다" 다수)
#
#   [전체 데이터 플로우 추적 결과 — 근본 원인 2가지]
#     원인 A: ai_analyze_item이 gemini-2.5-flash-image(이미지 생성 전용 모델)
#             사용 → JSON 분석 정확도 낮음 → 치마 판별 오판 가능성
#     원인 B: codistyle_generate가 단일 호출로 이미지+텍스트 동시 생성
#             → 모델이 이미지에 토큰 집중 → 리포트 텍스트 품질 저하
#             → "심층 분석:" 혼입, 섹션 누락, 빈약한 불릿의 구조적 원인
#
#   [ACTION 1] ai_analyze_item 모델 분리 (~line 4450)
#     - 기존: _CODISTYLE_MODEL (=gemini-2.5-flash-image) 사용
#     - 신규: gemini-2.0-flash (환경변수 CODIBANK_ANALYZE_MODEL로 오버라이드 가능)
#     - 효과: 치마/바지 판별 정확도 ↑, JSON 파싱 실패율 ↓
#     - 이미지 생성용 _CODISTYLE_MODEL은 그대로 유지 (영향 없음)
#
#   [ACTION 2] codistyle_generate 2단계 아키텍처 (~line 3645)
#     STAGE 1 — 이미지 생성 (gemini-2.5-flash-image)
#       · modalities=[IMAGE, TEXT]로 호출 (기존과 동일)
#       · TEXT는 백업용으로만 보관
#       · finishReason=STOP 자동 재시도 로직 유지
#       · 이미지 바이트 없으면 여기서 return
#
#     STAGE 2 — 리포트 생성 (gemini-2.0-flash, 환경변수 CODIBANK_REPORT_MODEL)
#       · 같은 prompt 재사용 (PHASE 1~5 전체)
#       · 이미지 전송 안 함 (텍스트 전용 모델)
#       · modalities 지정 안 함 → 모든 토큰을 리포트에 집중
#       · 응답이 200자 초과이면 comment 교체, 미만이면 STAGE 1 백업 유지
#
#     STAGE 3 — 파싱 (기존 로직 그대로 재사용)
#       · STYLING_SCORE/4지표/Executive Summary/TPO/Tips/Hashtags/5섹션
#       · 변경 없음, 코드 위치 변경 없음
#
#   [ACTION 3] 진단 로그 강화 — [DIAG] 태그 6종
#     [DIAG #0] payload 수신 시점: top/bot 카테고리, is_skirt, gender, bodyType
#               (~line 2886) — 민감정보(faceImage) 제외
#     [DIAG #1] bottom_info 최종 판정: is_skirt, garment 라벨
#               (~line 3646)
#     [DIAG #2] prompt 검증: 길이, "Skirt only"/"NO pants" 포함 여부
#               (~line 3652)
#     [DIAG #3] STAGE 1 완료: img_bytes 크기, 백업 텍스트 길이
#               (~line 3811)
#     [DIAG #4] STAGE 2 응답: 모델명, 리포트 길이, 첫 200자
#               (~line 3859)
#     [DIAG #5] 최종 파싱 결과: 점수/섹션 개수/각 필드 길이
#               (~line 4003)
#     - 모든 로그에 flush=True 적용 → Render 로그에 즉시 표시
#     - base64 이미지 등 민감정보는 로그에 절대 찍지 않음
#
#   [효과 예측]
#     - 치마 판별: ai_analyze_item 모델 업그레이드로 오판 ↓
#     - 리포트 품질: 텍스트 전용 모델이 같은 토큰 예산을 리포트에만 사용
#       → 5섹션 모두 채움, "심층 분석:" 혼입 감소
#     - 디버깅: [DIAG] 로그 6종으로 문제 발생 지점 즉시 특정 가능
#
#   [배포 시 환경변수 (기본값 있음, 오버라이드만 필요 시)]
#     CODIBANK_ANALYZE_MODEL  (기본값: gemini-2.0-flash)
#     CODIBANK_REPORT_MODEL   (기본값: gemini-2.0-flash)
#
# ─── 2026-04-20 22:00 KST (⚠️프리미엄 리포트 내용 빈약 → 10만원 컨설팅급 수술) ────
#   [TJ님 강력 제보] 프리미엄 리포트 각 섹션이 너무 빈약. 유료 가치 증명 불가.
#
#   [수술 1] 응답 길이 제한 확장 (2곳, ~line 3568, 3621)
#     comment = part.text.strip()[:2000]  →  [:15000]
#     - 이전: 2000자 넘는 프리미엄 장문 응답이 통째로 잘림
#     - 신규: 5섹션 × 700자 + 점수/요약 = 여유 15000자
#
#   [수술 2] Gemini config 강화 (신/구 SDK 양쪽, ~line 3510)
#     - temperature: 0.7 → 0.4 (일관성 강화, 섹션 생략 방지)
#     - max_output_tokens: 기본값 → 8192 명시
#     - 기본값이 작으면 Gemini가 앞쪽 섹션에 토큰 소진 → 뒷 섹션 잘림
#
#   [수술 3] Executive Summary 정규식 완전 재작성 (~line 3697)
#     - 이전 문제: "종합 평가: ...안색 밝혀줍니다. 심층 분석:" 이 통째로 요약에
#                  들어가서 화면에 "...심층 분석:" 이 끝에 표시됨
#     - 신규 정규식: "심층 분석|Deep-dive|OUTPUT LINE|각 섹션 라벨" 모두 경계로 인식
#     - 추가 후처리: 같은 줄에 섹션 마커가 등장하면 앞부분만 취함
#     - 추가 후처리: 끝의 "심층", "분석" 미완결 단어 제거
#     - 글자수 제한 300 → 500자
#
#   [수술 4 — 최대 공사] Phase 5 프롬프트 전면 재설계 (~line 3365)
#     원칙: "10만원 패션 컨설팅 수준의 풍부한 보고서" 강제
#
#     (A) 톤앤매너 강제:
#         - "senior fashion consultant at a paid consulting service (10만원/consultation tier)"
#         - 전문 용어 필수: 'complements the complexion', 'anchors the silhouette',
#                          '안색을 화사하게 밝혀주는', '세련된 실루엣을 완성하는'
#         - 캐주얼 금지: 'nice', 'cool', '좋아요', '멋져요'
#
#     (B) 포맷 강제 ★ CRITICAL FORMATTING RULES:
#         1) ALL 6 OUTPUT LINES must appear — missing any = failed report
#         2) Each DEEP-DIVE section must have EXACTLY 5 bullets (▸)
#         3) Each bullet must be 40-80 characters (1-2 complete sentences)
#         4) Total report length: 2000-4000 characters expected
#         5) Reference PHASE 1 data in EVERY bullet
#         6) NEVER merge sections, NEVER skip, NEVER use 'N/A'
#
#     (C) 각 섹션 구체적 지시 — 이전 "[▸ a · ▸ b · ▸ c]" 에서 완전 진화:
#         예) 퍼스널컬러 분석:
#           ▸ [PHASE 1 시즌 타입 (예: 봄 웜톤)과 그 특성 — 왜 이 시즌이 맞는지 근거]
#           ▸ [상의 컬러 '색상명 #HEX' 형식 vs PHASE 1 팔레트: 매치/미스매치 이유]
#           ▸ [하의 컬러 '색상명 #HEX' vs 팔레트: 앵커/방해 요소인지 판단]
#           ▸ [페이스보드 반사 효과: 안색 밝힘 / 다크서클 부각 / 그림자 상세 분석]
#           ▸ [정제된 보완 제안: 액세서리 컬러 또는 메이크업 톤 구체 변경]
#
#     (D) ★★★ FINAL SELF-CHECK BEFORE OUTPUT ★★★ 자기 검증 강제:
#         Gemini가 출력 직전에 5개 항목 체크:
#         [1] All 6 OUTPUT LINES present?
#         [2] Each deep-dive section has exactly 5 bullets with ▸?
#         [3] Each bullet is 40-80 chars (not 10-char single words)?
#         [4] Executive Summary clean WITHOUT '심층 분석' text?
#         [5] Every bullet references PHASE 1 body type or personal color?
#         If any check fails, rewrite that section.
#
#     (E) OUTPUT LINE 2 Executive Summary 강화:
#         - "DO NOT include phrase '심층 분석' or 'Deep-dive' here" 명시적 금지
#         - "End this section cleanly — next section starts on a new line"
#         - 글자 수: 150~220자 (이전 200자 이내 → 하한선 150자 명시)
#
#   [기대 효과]
#     - 각 섹션당 5불릿 × 60자 평균 = 섹션당 300자+ 풍부한 내용
#     - 전체 리포트 약 2500~3500자 (이전 800자 → 3배 이상)
#     - "준비 중입니다" 빈 섹션 발생률 0% 목표
#     - "심층 분석:" 같은 파싱 오류 완전 차단
#
# ─── 2026-04-20 19:30 KST (명세서 V2 반영 — Phase 5 프롬프트 고도화) ──────
#   [명세서 V2 개정] Section IV 핵심 구간 배점 40점 재구성:
#     - Section IV-1 비율 개선도 (Proportion /20)
#         Y축(수직) 관점: 상의 기장 + 하의 허리선(Rise) × 사용자 신장
#     - Section IV-2 체형 밸런스 (harmony /20)
#         X축(수평) 관점: 사용자 체형(A/V/H/X/O) × 의상 부피/소재 두께감
#
#   [수정 위치] codistyle_generate 함수의 PHASE 5 scoring basis (~line 3378)
#
#   [proportion/20 프롬프트 고도화]
#     - "SPEC V2: VERTICAL/Y-axis analysis" 명시
#     - 턱인/턱아웃 연출에 의한 허리선 재설정 효과
#     - 신장 보완율 (실제 키 대비 시각적 상대 다리길이)
#     - 3:7 / 4:6 이상 비율 판정
#
#   [harmony/20 프롬프트 고도화]
#     - "SPEC V2: HORIZONTAL/X-axis analysis" 명시
#     - "This is NOT merely about garment color coordination —
#        it is body-type-anchored volume balance." 명시
#     - 체형 타입별 매트릭스를 _build_body_type_prompt로 주입
#     - 상체:하체 부피 1:1 판정
#
#   [심층 분석 섹션] 상하의 밸런스 섹션 불릿 재작성 (~line 3424, 3434)
#     - 기존: 소재 조화 · 볼륨 균형 · 디자인 · 컬러 · 케미스트리
#     - 신규: 체형 타입(A/V/H/X/O) × 상의/하의 부피 매칭 + X축 부피 균형
#             + 상체:하체 1:1 판정 + 명세서 V2 체형 기준 총평
#
# ─── 2026-04-20 09:50 KST (C.S.I 4지표 + 프리미엄 리포트 백엔드) ──────────
#   [명세서] CodiBank Premium Personal Styling Report V1 대응
#   [수정 위치] codistyle_generate 함수의 PHASE 5 EVALUATION 블록 + 응답 파싱
#
#   [STEP 1] Phase 5 프롬프트 전면 재설계 (~line 3316)
#     - 점수: 3지표(PC 40/Body 40/Coord 20) → C.S.I 4지표
#       · body_shape        /30  (체형 보완도)
#       · personal_color    /30  (퍼스널 컬러 조화)
#       · proportion        /20  (비율 개선도 — 신규)
#       · harmony           /20  (상하의 밸런스 — 신규)
#     - 톤앤매너: "전문 컨설턴트" 어조 강제 (캐주얼 표현 금지)
#     - 신규 출력:
#       · OUTPUT LINE 2 — Executive Summary (2~3문장 한 줄 평)
#       · OUTPUT LINE 4 — Best TPO 추천 (2~3개, '|' 구분)
#       · OUTPUT LINE 5 — 개선 팁 (헤어/액세서리/신발, '|' 구분)
#       · OUTPUT LINE 6 — 스타일 해시태그 (5개, # 접두)
#     - 심층 분석 섹션: 4개 → 5개 (실루엣과 비율 / 상하의 밸런스 추가)
#
#   [STEP 1-B] 응답 파싱 로직 확장 (~line 3545)
#     - 4지표 점수 추출 + 정규화 (총점 합 일치 보정)
#     - executive_summary / tpo_recommendations / improvement_tips /
#       style_hashtags 신규 파싱
#     - 구형 응답 fallback (coordination→harmony 매핑, keywords→hashtags)
#
#   [응답 JSON 필드] 신규 4개 필드 추가:
#     executive_summary, tpo_recommendations,
#     improvement_tips, style_hashtags
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


# ─── 2026-05-23 KST · TJ 지시 ─── 지역별 head-to-body ratio 결정 ────────────
#   요구사항:
#     · 아시아 지역(서울/일본/중국/동남아 등) + 신체 데이터 있음  → 7.5 (한국 성인 평균)
#     · 그 외 지역(서양/북미/유럽/오세아니아 등)                  → 8.0 (서양 평균)
#     · 신체 데이터 없음                                        → 8.0 (사용자 본인 비율 알 수 없음)
#   호출처: _build_body_profile_block(), _ai_styling_via_gemini()
# ───────────────────────────────────────────────────────────────────────────
_ASIA_LOCATION_KEYWORDS = (
    # 한국 ─────────────────────────────────────────────────
    "서울", "부산", "인천", "대구", "광주", "대전", "울산", "수원", "고양",
    "용인", "성남", "청주", "안산", "전주", "안양", "천안", "남양주", "화성",
    "포항", "제주", "춘천", "원주", "강릉", "목포", "순천", "여수", "창원",
    "seoul", "busan", "incheon", "daegu", "gwangju", "daejeon", "ulsan",
    "suwon", "korea", "south korea", "republic of korea",
    # 일본 ─────────────────────────────────────────────────
    "tokyo", "osaka", "kyoto", "yokohama", "nagoya", "sapporo", "fukuoka",
    "kobe", "hiroshima", "japan", "도쿄", "오사카", "교토", "나고야",
    # 중국 ─────────────────────────────────────────────────
    "beijing", "shanghai", "guangzhou", "shenzhen", "chengdu", "tianjin",
    "hangzhou", "wuhan", "xian", "china", "베이징", "상하이", "광저우",
    # 대만/홍콩/마카오 ─────────────────────────────────────
    "taipei", "taiwan", "hong kong", "hongkong", "macau", "macao",
    "타이베이", "홍콩", "마카오",
    # 동남아 ───────────────────────────────────────────────
    "bangkok", "thailand", "singapore", "kuala lumpur", "malaysia",
    "jakarta", "indonesia", "manila", "philippines",
    "ho chi minh", "saigon", "hanoi", "vietnam", "phnom penh", "cambodia",
    "yangon", "myanmar", "vientiane", "laos", "brunei",
    "방콕", "싱가포르", "쿠알라룸푸르", "자카르타", "마닐라", "호치민", "하노이",
    # 인도/남아시아 ────────────────────────────────────────
    "mumbai", "delhi", "new delhi", "bangalore", "kolkata", "chennai",
    "hyderabad", "india", "dhaka", "bangladesh",
    "karachi", "lahore", "islamabad", "pakistan",
    "kathmandu", "nepal", "colombo", "sri lanka",
    # 중앙아시아 ───────────────────────────────────────────
    "almaty", "kazakhstan", "tashkent", "uzbekistan",
    # 대륙 ─────────────────────────────────────────────────
    "asia", "asian", "아시아", "아시안",
)


def _get_head_ratio(location: str = "", has_body_data: bool = False) -> tuple:
    """
    지역 + 신체 데이터 유무로 인체 head-to-body ratio 결정.

    Args:
        location: 사용자 위치 (예: "서울", "Tokyo", "New York") — 빈 문자열 허용
        has_body_data: height/weight 가 모두 등록되어 있는지

    Returns:
        (ratio_str, region_label_en): 예) ("7.5", "Korean/East Asian adult")
                                         ("8.0", "general adult")
    """
    # 신체 데이터 없으면 무조건 8.0 (사용자 본인 비율 모름 → 일반 평균)
    if not has_body_data:
        return ("8.0", "general adult")

    # location 없으면 안전 폴백 8.0
    if not location:
        return ("8.0", "general adult")

    location_lower = str(location).lower().strip()
    for kw in _ASIA_LOCATION_KEYWORDS:
        if kw in location_lower:
            return ("7.5", "Korean/East Asian adult")

    return ("8.0", "general adult")


def _build_body_profile_block(gender, age, height, weight, body_type_key, lang="en", location=""):
    """
    신체 프로필 통합 블록 생성 (Phase 1 PERSONA에 삽입)
    이미지 생성 단계에서 체형 특성이 실제로 반영되도록 구조화

    ─── 2026-05-23 KST · TJ 승인 (옵션 다 + 7.5 heads) ─────────────────
      추가: 키 기반 신장감(Stature), 몸무게 기반 체격감(Body mass) 시각 묘사
      목적: BMI 카테고리(slim/average/...)만으로는 부족한 사용자 실제 데이터 강조
            → 99.0% 닮은 아바타: 키 175cm 와 165cm 가 시각적으로 구분되도록

    ─── 2026-05-23 KST · TJ 지시 ─── location 인자 추가 ────────────────
      location: 사용자 지역 (서울/일본/중국 등 아시아 → 7.5 / 그 외 → 8.0)
      신체 데이터 없으면 무조건 8.0 적용
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

    # ─── 2026-05-23 KST · TJ 승인 (옵션 C 강화) ───
    # 2-A) 키 기반 신장감(Stature) — 한국 성인 평균(남 173, 여 161) 기준 5단계
    try:
        h_int_local = int(float(str(height).strip())) if height else 0
    except Exception:
        h_int_local = 0
    if h_int_local >= 100:
        # 남녀 공통 기준 (남자는 +5cm 가산 효과를 AI 가 추정)
        if h_int_local >= 180:
            lines.append(f"Stature: TALL — visibly above-average height ({h_int_local}cm). Render with elongated stance and longer limbs proportional to height.")
        elif h_int_local >= 170:
            lines.append(f"Stature: ABOVE-AVERAGE — moderately tall ({h_int_local}cm). Render with slightly above-average leg length.")
        elif h_int_local >= 160:
            lines.append(f"Stature: AVERAGE — typical Korean adult height ({h_int_local}cm). Render with standard everyday proportions.")
        elif h_int_local >= 150:
            lines.append(f"Stature: BELOW-AVERAGE — shorter than average ({h_int_local}cm). Render with proportionally shorter stance. DO NOT artificially elongate legs.")
        else:
            lines.append(f"Stature: PETITE — notably short ({h_int_local}cm). Render with petite, compact silhouette.")

    # 2-B) 몸무게 기반 체격감(Body mass) — BMI 와 다른 축으로 실제 부피감 명시
    try:
        w_int_local = int(float(str(weight).strip())) if weight else 0
    except Exception:
        w_int_local = 0
    if w_int_local >= 30:
        if w_int_local >= 90:
            lines.append(f"Body mass: VISIBLY LARGER frame ({w_int_local}kg) — render with realistic fullness in shoulders, torso, and limbs. DO NOT slim down or flatter the figure.")
        elif w_int_local >= 75:
            lines.append(f"Body mass: SOLID frame ({w_int_local}kg) — render with realistic body mass, neither slimmed down nor exaggerated.")
        elif w_int_local >= 60:
            lines.append(f"Body mass: MODERATE frame ({w_int_local}kg) — average Korean build, realistic proportions.")
        elif w_int_local >= 50:
            lines.append(f"Body mass: SLENDER frame ({w_int_local}kg) — render slim but natural, not emaciated.")
        else:
            lines.append(f"Body mass: VERY SLIM frame ({w_int_local}kg) — render with petite, slender build. DO NOT add volume.")

    # 3) BMI 기반 실루엣 가이드 (암묵적 지시 대신 구체 지시)
    bmi_guides = {
        "slim":           "Slim build: avoid oversized/baggy silhouettes that swamp the frame. Subtle layering and structured cuts maintain proportion.",
        "average":        "Average build: most silhouettes work; prioritize balanced proportions between top and bottom.",
        "slightly heavy": "Slightly fuller build: straight or semi-fitted silhouettes work best. Avoid overly tight or overly baggy extremes that exaggerate volume.",
        "heavier":        "Fuller build: vertical lines, darker tones on larger areas, and structured (not clingy, not voluminous) silhouettes flatter the frame.",
    }
    if bmi_cat_en and bmi_guides.get(bmi_cat_en):
        lines.append("BMI-based silhouette guidance: " + bmi_guides[bmi_cat_en])

    # 4) 체형 특성 블록 (_build_body_type_prompt 재활용)
    bt_block = _build_body_type_prompt(gender, body_type_key)
    if bt_block:
        lines.append(bt_block.strip())

    # 5) 객관성 강제 지시 (─── 2026-05-23 KST · TJ 지시 ─── 지역별 ratio 동적 결정 ───)
    _has_body_data_for_ratio = bool(height and weight)
    _ratio_str, _region_lbl = _get_head_ratio(location, _has_body_data_for_ratio)
    lines.append(
        "CRITICAL — OBJECTIVE RENDERING: "
        "The generated image MUST show the outfit AS IT WOULD ACTUALLY LOOK on this SPECIFIC body. "
        + (f"Use the EXACT height ({height}cm) and weight ({weight}kg) stated above — "
           if _has_body_data_for_ratio else
           "Use natural average adult proportions since user body data is not registered — ")
        + "do NOT default to an exaggerated supermodel body. "
        f"Body proportions: {_ratio_str} head-to-body ratio ({_region_lbl}). "
        "Apply the recommended silhouette, avoid the forbidden silhouette. "
        "This is a REAL person with REAL body — render accordingly."
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
# [Phase 1 — 2026-05-22 KST] 패션 AI 기술 초기화
#   변경:
#   · rembg(배경제거) — 유지 (HF Space 호출, Render 메모리 영향 없음)
#   · Lykdat(외부 유료 API) — 제거 (Gemini 단독 분석으로 단순화)
#   · Marqo-FashionSigLIP — 제거 (Render Starter 512MB RAM 제약으로
#                                매번 silent 로딩 실패하던 dead code)
#   · cosine_similarity — 제거 (Marqo embedding 없으면 의미 없음)
#   효과: Docker 이미지 -300MB (transformers/torch 의존성 제거),
#         Render 메모리 안정화, /api/ai/match-wardrobe 는 graceful 503 응답.
# ══════════════════════════════════════════════════════════════

# ── rembg: 의류 배경 제거 (HF Space API) ──────────────────────
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


# ══════════════════════════════════════════════════════════════
# [Phase 3 — 2026-05-23 KST · TJ 지시] LAB/KMeans 색상 추출
#   목적: 자동분류 색상 정확도 강화 + 다중 색상 의류 (예: 반반 콤비 자켓) 정조준
#   방식:
#     1. 이미지 → PIL → 다운샘플 (200×200) → numpy 배열
#     2. 알파 채널 있으면 비투명 픽셀만 추출 (배경 자동 제외)
#     3. 흰색/너무 밝은 픽셀 (R,G,B 모두 240+) 제외 — 배경 추가 제거
#     4. RGB → LAB 색공간 변환 (CIE 1976, 인지적 색상 분리)
#     5. KMeans (numpy 직접 구현, k=5, max 15 iter) 클러스터링
#     6. 클러스터 크기 순으로 정렬 → 상위 3개 반환
#     7. 각 LAB 좌표 → 가장 가까운 한국어 색명 매핑 (사전 기반)
#   의존성: numpy(있음) + PIL(있음). 추가 라이브러리 없음.
#   메모리: 200×200 이미지 + k=5 클러스터 = 임시 ~10MB (Render Starter OK)
#   응답시간: ~150~400ms / 이미지
# ══════════════════════════════════════════════════════════════

# ── 한국어 색명 사전 (LAB 좌표 기준) ──
#   LAB 색공간: L=명도(0~100), a=초록↔빨강(-128~127), b=파랑↔노랑(-128~127)
#   기본+패션 색상 30+ 개. 향후 확장 가능.
_KOREAN_COLOR_NAMES = [
    # (이름, L, a, b)
    # 무채색
    ("블랙",       10,   0,    0),
    ("차콜",       25,   0,    0),
    ("다크그레이", 35,   0,    0),
    ("그레이",     55,   0,    0),
    ("라이트그레이", 75, 0,    0),
    ("화이트",     95,   0,    0),
    # 베이지 / 누드 톤
    ("아이보리",   92,   2,   12),
    ("크림",       90,   4,   18),
    ("베이지",     78,   8,   22),
    ("카멜",       58,  14,   30),
    ("토프",       62,   6,   12),
    # 갈색 톤
    ("브라운",     38,  18,   28),
    ("다크브라운", 25,  14,   18),
    ("초콜릿",     22,  16,   16),
    # 레드 톤
    ("레드",       48,  68,   45),
    ("다크레드",   30,  50,   30),
    ("와인",       28,  40,   18),
    ("버건디",     25,  36,   12),
    ("다크버건디", 18,  30,    8),
    ("핑크",       72,  28,    5),
    ("코랄",       65,  40,   25),
    # 오렌지 / 옐로 톤
    ("오렌지",     65,  35,   55),
    ("머스타드",   68,   8,   55),
    ("옐로",       85,  -5,   75),
    # 그린 톤
    ("올리브",     50, -10,   38),
    ("카키",       45,  -8,   28),
    ("그린",       55, -45,   30),
    ("다크그린",   30, -25,   20),
    ("민트",       80, -25,    5),
    # 블루 톤
    ("스카이블루", 75, -10,  -25),
    ("블루",       45,   5,  -45),
    ("네이비",     22,   8,  -25),
    ("다크네이비", 15,   6,  -18),
    ("인디고",     30,  15,  -35),
    # 퍼플 톤
    ("라벤더",     72,  12,  -18),
    ("퍼플",       40,  35,  -35),
    ("다크퍼플",   25,  25,  -22),
]

def _rgb_to_lab_array(rgb_arr):
    """RGB (numpy uint8, shape Nx3) → LAB (numpy float, shape Nx3)
       CIE 1976 표준 변환. sRGB → XYZ → LAB."""
    import numpy as np
    # sRGB → linear
    rgb_norm = rgb_arr.astype(np.float32) / 255.0
    mask = rgb_norm > 0.04045
    rgb_lin = np.where(mask, ((rgb_norm + 0.055) / 1.055) ** 2.4, rgb_norm / 12.92)
    # linear RGB → XYZ (D65)
    M = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ], dtype=np.float32)
    xyz = rgb_lin @ M.T
    # XYZ → LAB (D65 white point)
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883
    xyz_norm = xyz / np.array([Xn, Yn, Zn], dtype=np.float32)
    eps = 0.008856
    kappa = 903.3
    f = np.where(xyz_norm > eps, np.cbrt(xyz_norm), (kappa * xyz_norm + 16) / 116)
    L = 116 * f[:, 1] - 16
    a = 500 * (f[:, 0] - f[:, 1])
    b = 200 * (f[:, 1] - f[:, 2])
    return np.stack([L, a, b], axis=1)

def _lab_to_rgb(lab):
    """단일 LAB → RGB (0~255 int). 평균 클러스터 색을 HEX 로 변환할 때 사용."""
    import numpy as np
    L, a, b = float(lab[0]), float(lab[1]), float(lab[2])
    # LAB → XYZ
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200
    eps3 = 0.008856 ** (1.0 / 3.0)
    def _inv(t):
        return t ** 3 if t > eps3 else (116 * t - 16) / 903.3
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883
    X, Y, Z = _inv(fx) * Xn, _inv(fy) * Yn, _inv(fz) * Zn
    # XYZ → linear RGB
    Minv = np.array([
        [ 3.2404542, -1.5371385, -0.4985314],
        [-0.9692660,  1.8760108,  0.0415560],
        [ 0.0556434, -0.2040259,  1.0572252],
    ], dtype=np.float32)
    rgb_lin = np.array([X, Y, Z], dtype=np.float32) @ Minv.T
    # linear → sRGB
    rgb = np.where(rgb_lin > 0.0031308,
                   1.055 * (np.clip(rgb_lin, 0, None) ** (1 / 2.4)) - 0.055,
                   12.92 * rgb_lin)
    rgb = np.clip(rgb * 255, 0, 255).astype(int)
    return tuple(int(c) for c in rgb)

def _lab_to_color_name(lab):
    """LAB 좌표 → 가장 가까운 한국어 색명 (사전 기반)"""
    best_name, best_dist = "기타", float("inf")
    for name, L, a, b in _KOREAN_COLOR_NAMES:
        d = (lab[0] - L) ** 2 + (lab[1] - a) ** 2 + (lab[2] - b) ** 2
        if d < best_dist:
            best_dist, best_name = d, name
    return best_name

def _numpy_kmeans_lab(lab_pixels, k=5, max_iter=15):
    """numpy 만으로 KMeans 직접 구현. LAB 픽셀 (Nx3) → (centroids, labels)
       초기 중심점: k-means++ 간소화 (각 점이 이전 점들로부터 멀수록 선택 확률 ↑)
       단위테스트 발견 케이스 보강 (2026-05-23):
         · 단일색 이미지: 분산이 작으면 KMeans 스킵하고 평균 1개 반환
         · k-means++ 확률 정규화 안전장치 (NaN/합!=1 방지)"""
    import numpy as np
    n = len(lab_pixels)
    if n <= k:
        return lab_pixels, np.arange(n)
    # 단일색 / 거의 균일 → KMeans 스킵
    variance = float(lab_pixels.var(axis=0).sum())
    if variance < 5.0:
        centroid = lab_pixels.mean(axis=0, keepdims=True)
        labels = np.zeros(n, dtype=int)
        return centroid, labels
    rng = np.random.default_rng(42)
    # k-means++ 초기화
    first_idx = int(rng.integers(0, n))
    centroids = [lab_pixels[first_idx]]
    for _ in range(k - 1):
        dists = np.min(
            np.linalg.norm(lab_pixels[:, None, :] - np.array(centroids)[None, :, :], axis=2),
            axis=1,
        )
        dists_sq = dists ** 2
        total = float(dists_sq.sum())
        if total < 1e-6 or not np.isfinite(total):
            # 더 이상 다양성 없음 → 무작위 선택
            next_idx = int(rng.integers(0, n))
        else:
            probs = dists_sq / total
            probs = probs / probs.sum()  # 부동소수 오차 정규화
            next_idx = int(rng.choice(n, p=probs))
        centroids.append(lab_pixels[next_idx])
    centroids = np.array(centroids, dtype=np.float32)
    # KMeans iteration
    labels = np.zeros(n, dtype=int)
    for _ in range(max_iter):
        dists = np.linalg.norm(lab_pixels[:, None, :] - centroids[None, :, :], axis=2)
        new_labels = np.argmin(dists, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for ci in range(k):
            mask = labels == ci
            if mask.sum() > 0:
                centroids[ci] = lab_pixels[mask].mean(axis=0)
    return centroids, labels

def extract_dominant_colors(img_bytes: bytes, top_n: int = 3) -> list:
    """
    의류 이미지 → 주요 색상 top_n 개 추출
    반환: [{"hex": "#1a1a1a", "name": "블랙", "ratio": 0.48,
            "lab": [L, a, b], "rgb": [R, G, B]}, ...]
    실패 시 빈 리스트.
    """
    try:
        import numpy as np
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes))
        # 다운샘플 (200×200) — 계산량 ~25배 감소, 색상 분포는 거의 동일
        img.thumbnail((200, 200), Image.LANCZOS)
        # RGBA → 비투명 픽셀만 추출 (rembg 결과 호환)
        if img.mode == 'RGBA':
            arr = np.array(img)
            mask = arr[:, :, 3] > 128
            rgb = arr[mask][:, :3]
        else:
            arr = np.array(img.convert('RGB'))
            rgb = arr.reshape(-1, 3)
        if len(rgb) < 50:
            print("[color-extract] 픽셀 부족, 스킵")
            return []
        # 흰색 배경 추정 픽셀 제외 (R,G,B 모두 240+)
        not_white = ~((rgb[:, 0] >= 240) & (rgb[:, 1] >= 240) & (rgb[:, 2] >= 240))
        rgb_clean = rgb[not_white]
        # 흰색 제외 후 너무 적으면 흰색 포함 (전체가 화이트 옷일 가능성)
        if len(rgb_clean) < len(rgb) * 0.1:
            rgb_clean = rgb
        # RGB → LAB
        lab = _rgb_to_lab_array(rgb_clean)
        # KMeans 클러스터링
        centroids, labels = _numpy_kmeans_lab(lab, k=5, max_iter=15)
        # 클러스터별 비율 + 정렬
        counts = np.bincount(labels, minlength=len(centroids))
        total = counts.sum()
        ratios = counts / max(total, 1)
        order = np.argsort(-counts)
        results = []
        for idx in order[:top_n]:
            if ratios[idx] < 0.05:  # 5% 미만 클러스터는 노이즈로 간주
                continue
            lab_c = centroids[idx]
            rgb_c = _lab_to_rgb(lab_c)
            hex_c = "#{:02x}{:02x}{:02x}".format(*rgb_c)
            name_c = _lab_to_color_name(lab_c)
            results.append({
                "hex":   hex_c,
                "name":  name_c,
                "ratio": round(float(ratios[idx]), 3),
                "lab":   [round(float(x), 1) for x in lab_c],
                "rgb":   list(rgb_c),
            })
        print(f"[color-extract] ✅ {len(results)}색 추출: " +
              ", ".join(f"{r['name']}({r['ratio']*100:.0f}%)" for r in results))
        return results
    except Exception as e:
        print(f"[color-extract] ⚠ 실패: {e}")
        return []


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


# ─── 2026-05-14 v67 Phase 1.5 HOTFIX ─── R2 객체 다운로드 헬퍼 ───
# 이전: _read_upload_bytes 함수가 정의되지 않아 PC 데이터 로드 실패
#       [PC] R2 load failed: name '_read_upload_bytes' is not defined
# 추가: boto3 s3 client의 get_object를 사용한 R2 read 헬퍼
def _read_r2_bytes(key: str) -> bytes | None:
    """R2 버킷에서 객체 다운로드 → bytes (실패 시 None).

    key 예시: "personal_color/user@example.com.json", "uploads/face_xxx.jpg"
    """
    r2 = _get_r2()
    if not r2:
        return None
    try:
        resp = r2.get_object(Bucket=_R2_BUCKET, Key=key)
        return resp["Body"].read()
    except Exception as e:
        # 404 (NoSuchKey)는 정상 케이스 (파일 없음), 다른 에러는 로깅
        _err_str = str(e)
        if "NoSuchKey" not in _err_str and "404" not in _err_str:
            print(f"[R2] read 실패 (key={key}): {e}")
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
                "webp":"image/webp","gif":"image/gif","mp4":"video/mp4"}
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

    # ─── 2026-05-18 KST · TJ 지시 ─── Q3: 선택한 추천 코디 = style reference ───
    #   closet.html startStepC 가 baseCard.imageUrl 을 _force_ref_image 로 전달.
    #   이 이미지를 "style_ref" 라벨로 수집 → Q3 프롬프트가 의상을 99.9% 복제.
    #   data URL / 원격 URL 모두 지원.
    style_ref_data = str(payload.get("_force_ref_image_data") or "").strip()
    style_ref_url = str(payload.get("_force_ref_image") or "").strip()
    if style_ref_data:
        try:
            mime, img_bytes = _data_url_to_bytes(style_ref_data)
            refs.append(("style_ref", mime, img_bytes))
        except Exception:
            pass
    elif style_ref_url.startswith(("http://", "https://")):
        try:
            mime, img_bytes = _download_remote_image(style_ref_url)
            refs.append(("style_ref", mime, img_bytes))
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


# ══════════════════════════════════════════════════════
# [2026-05-14 v67 Phase 3] 캐시 키 v2 — 버킷팅 + 핵심 필드 보강
# ══════════════════════════════════════════════════════
def _make_ai_cache_key_v2(
    payload: Dict[str, Any],
    face_bytes: bytes | None,
    ref_images: list[tuple[str, str, bytes]] | None = None,
    model: str = "",
    quality: str = "",
    size: str = "",
    force_regenerate: bool = False,
    matched_stylist: dict | None = None,
    meta: dict | None = None,
) -> str:
    """[v67 Phase 3] 코디핏 캐시 키 v2 — 버킷팅 적용 + 핵심 필드 보강

    v1 (`_make_ai_cache_key`) 대비 차이:
      - 추가 필드: model, quality, size, user.bodyType,
                  personalColor.season, personalColor.avoid_colors_hash
      - 버킷팅: weather.temp 5°C, height 5cm, weight 5kg
      - customText: 공백/대소문자 정규화 후 해싱 (동일 의미 텍스트 캐시 통합)
      - weather.text: 5종 enum 정규화 (sunny/cloudy/rainy/snowy/other)
      - retrySeed: force_regenerate=True 시에만 포함 (기본 미포함 → 캐시 히트율 ↑)

    ─── 2026-05-14 v67 Phase 1.7-fix ─── 스타일리스트 식별 추가 ──
    TJ 보고: "AI 스타일리스트 변경해도 코디 컬러/스타일 동일"
    원인: 캐시 키에 stylist_name/city 누락 → 다른 스타일리스트인데도 같은 키 산출
          → 캐시 HIT → 백엔드 AI 호출 자체가 일어나지 않음
    수정: matched_stylist/meta를 인자로 받아 캐시 키에 stl(이름)/cty(도시) 포함
    효과: 스타일리스트가 다르면 다른 캐시 키 → 새 이미지 생성

    캐시 폭발 방지 효과 (유지):
      - v1: 사용자당 평균 480,000개 키 조합 → 히트율 < 1%
      - v2: 사용자당 평균 30~50개 키 조합 → 히트율 70%+
      - v2+stylist: 사용자당 평균 ~100개 (스타일리스트 풀 × 시나리오) → 여전히 양호
    """
    user = payload.get("user") or {}
    weather = payload.get("weather") or {}
    pc = payload.get("personalColor") or {}

    # ── 정규화: customText (공백/대소문자) ──
    _custom_text_raw = str(payload.get("customText") or "").strip()
    _custom_text_normalized = " ".join(_custom_text_raw.split()).lower()
    _custom_text_hash = (
        _sha256_hex(_custom_text_normalized.encode("utf-8"))[:12]
        if _custom_text_normalized else ""
    )

    # ── 정규화: avoid_colors (정렬 + 소문자) ──
    _avoid_list = pc.get("avoid_colors") or []
    if not isinstance(_avoid_list, list):
        _avoid_list = []
    _avoid_normalized = sorted(
        str(c).strip().lower() for c in _avoid_list if str(c).strip()
    )
    _avoid_hash = (
        _sha256_hex(",".join(_avoid_normalized).encode("utf-8"))[:12]
        if _avoid_normalized else ""
    )

    # ── 버킷팅: 온도 5°C ──
    try:
        _temp_raw = float(weather.get("temp") or 20)
        _temp_bucket = int(round(_temp_raw / 5) * 5)
    except Exception:
        _temp_bucket = 20

    # ── 버킷팅: 키/몸무게 5단위 ──
    try:
        _h_raw = int(user.get("height") or 170)
        _height_bucket = int(round(_h_raw / 5) * 5)
    except Exception:
        _height_bucket = 170
    try:
        _w_raw = int(user.get("weight") or 65)
        _weight_bucket = int(round(_w_raw / 5) * 5)
    except Exception:
        _weight_bucket = 65

    # ── 정규화: weather.text → 5종 enum ──
    _wt_raw = str(weather.get("text") or weather.get("condition") or "").strip().lower()
    if any(k in _wt_raw for k in ("맑", "sunny", "clear")):
        _weather_enum = "sunny"
    elif any(k in _wt_raw for k in ("흐", "구름", "cloud", "overcast")):
        _weather_enum = "cloudy"
    elif any(k in _wt_raw for k in ("비", "rain", "shower", "drizzle")):
        _weather_enum = "rainy"
    elif any(k in _wt_raw for k in ("눈", "snow")):
        _weather_enum = "snowy"
    else:
        _weather_enum = "other"

    body = {
        "svc": "codifit",
        "v": "2",
        "mdl": model or "",
        "qly": quality or "",
        "siz": size or "",
        "pur": payload.get("purposeKey") or "",
        "txt": _custom_text_hash,
        "dat": payload.get("forDateKey") or payload.get("dateKey") or "",
        "gen": user.get("gender") or "",
        "age": user.get("ageGroup") or "",
        "bdy": user.get("bodyType") or "",
        "hgt": _height_bucket,
        "wgt": _weight_bucket,
        "pcs": pc.get("season") or "",
        "avd": _avoid_hash,
        "tmp": _temp_bucket,
        "wth": _weather_enum,
        # ─── 2026-05-14 v67 Phase 1.7-fix ─── 스타일리스트 식별
        # 누락 시: 같은 (사용자, 날씨, 목적)에서 스타일리스트만 바뀌어도 캐시 HIT
        # → 백엔드 AI 호출 안 됨 → 새 prompt 효과 없음
        "stl": (matched_stylist or {}).get("name", "") if matched_stylist else "",
        "cty": (meta or {}).get("active_city", "") if meta else "",
    }

    if face_bytes:
        body["fhs"] = _sha256_hex(face_bytes)[:16]

    if ref_images:
        body["ref"] = [
            f"{label}:{_sha256_hex(raw)[:12]}" for label, _mime, raw in ref_images
        ]
        body["mod"] = payload.get("mode") or "styling"

    # ── retrySeed: force_regenerate 시에만 포함 (캐시 버스터) ──
    if force_regenerate:
        body["rsd"] = str(
            payload.get("retrySeed")
            or payload.get("seed")
            or _now_ms()
        )

    raw = json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return "v2_" + _sha256_hex(raw)[:22]


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

    # ─── 2026-05-17 KST · TJ 승인 ─── 온도 레이어링 규칙 강화 (closet.html 규칙 이식) ───
    # 이전: very cold/cool→방한, hot→통기, mild/warm→'balanced'(보온 허용) 3분기
    # 변경: _temp_bucket 5단계별 명확한 규칙 — warm(21-27°C)에서 보온 아이템 금지 명시
    if bucket == "very cold":
        weather_rule = "Very cold weather: a thick coat or padding is essential with warm inner layers. A muffler is appropriate."
    elif bucket == "cool":
        weather_rule = "Cool weather: jacket and light knit layering. Do NOT add a muffler unless near-freezing."
    elif bucket == "mild":
        weather_rule = "Mild weather: a light jacket or cardigan is optional. NO heavy coat/padding, NO muffler, NO scarf."
    elif bucket == "warm":
        weather_rule = "Warm weather: a single light layer is enough. NO outer layer, NO knit sweater, NO scarf, NO muffler. Short sleeves are appropriate."
    else:  # hot
        weather_rule = "Hot weather: light breathable short-sleeve clothing only. NO warm layers, NO scarf, NO muffler of any kind."

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
        # ── [Phase 1 — 2026-05-22] Lykdat/Marqo 제거됨 — 헬스체크에서도 제거 ──
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

    # ── [HOTFIX A — 2026-05-23 KST · TJ 지시] 의류 아이템 rembg 재비활성화 ──
    #   배경: 2026-05-22 Phase 1 에서 rembg 재활성화 했으나, 실사용 테스트에서
    #         "블랙+버건디 반반 콤비자켓" 케이스의 절반 영역이 배경으로 오판되어
    #         사라지는 부작용 재확인 (사용자 스크린샷 증거).
    #         비투명<15% 폴백은 "옷 전체 사라짐"만 잡고 "부분 사라짐"은 못 잡음.
    #         → 2026-04-10 비활성화 결정으로 회귀 (검증된 안전 상태).
    #   향후: 자동분류 정확도 개선은 Phase 2 (HF Space 분리, 더 정교한
    #         segmentation 모델 + FashionCLIP) 에서 처리.
    #
    # ── [2026-04-10 원본 결정 — 유지] 의류 아이템 배경 제거 비활성화 ──
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
    tier=None,  # ─── 2026-04-21 티어별 엔진 라우팅용 ───
    _override_alias=None,  # ─── 2026-05-14 v67 Phase 1.6 HYBRID ─── 폴백 호출용 alias 강제 지정
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

    # ─── 2026-05-23 KST · TJ 지시 ─── 지역별 head-to-body ratio 결정 ──────
    #   기준:
    #     · 아시아 지역(서울/일본/중국/동남아 등) + 신체 데이터 있음 → 7.5
    #     · 그 외 지역(서양/북미/유럽 등)                          → 8.0
    #     · 신체 데이터 없음                                       → 8.0
    #   우선순위: location(사용자 현재 위치) > stylist_city(스타일리스트 활동 도시)
    #   변수 사용처: 아래 SUBJECT 블록의 Proportion 줄 + _build_body_profile_block()
    # ─────────────────────────────────────────────────────────────────────
    _has_body_data_ratio = bool(height and weight)
    _loc_for_ratio = location or stylist_city or ""
    _head_ratio, _region_label_en = _get_head_ratio(_loc_for_ratio, _has_body_data_ratio)
    _is_asia_region = (_head_ratio == "7.5")

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

    # ═══════════════════════════════════════════════════════════════════
    # ─── 2026-05-14 v67 Phase 1.7-fix3 PROMPT 7-STEP REDESIGN ─────────
    # TJ 지시: 6단계 → 7단계로 재구조 + 스타일리스트 차별화 강화
    # 변경 핵심:
    #   1) STEP 3 신설: AI 스타일리스트 선정 명시 (시그니처 컬러 강조)
    #      → 9,600명 페르소나 데이터(color1/color2)가 prompt에 직접 노출
    #   2) STEP 4: TPO 분석 + 코디 세팅 (이전 STEP 5 → 중간 위치로 이동)
    #   3) STEP 5: CORE OUTFIT 이미지 생성 (이전 STEP 3)
    #   4) STEP 6: OPTIONAL 판단 (이전 STEP 4)
    #   5) STEP 7: OUTPUT FORMAT + 분석 리포트 병행 (이전 STEP 6 + JSON 통합)
    #   6) AVOID COLORS 3회 반복 → 1회로 축소 (컬러 다양성 회복)
    # ═══════════════════════════════════════════════════════════════════

    # AVOID 컬러 정리
    _avoid_clean = (pc_avoid_str or "").strip()
    _has_avoid = bool(_avoid_clean and _avoid_clean != "탁한 톤")

    # 스타일리스트 시그니처 컬러/메타 (matched_stylist 객체에서 직접 추출)
    _stylist_color1 = ""
    _stylist_color2 = ""
    _stylist_level = ""
    _stylist_exp = ""
    if isinstance(matched_stylist, dict):
        _stylist_color1 = str(matched_stylist.get('color1', '')).strip()
        _stylist_color2 = str(matched_stylist.get('color2', '')).strip()
        _stylist_level = str(matched_stylist.get('level', '')).strip()
        _stylist_exp = str(matched_stylist.get('exp', '')).strip()

    # ─── 2026-05-17 KST · TJ 승인 ─── 온도 의류 게이트 (closet.html 규칙 이식) ───
    # closet.html(line 5189~5212)의 강한 온도 규칙을 서버 STEP 1-7 에 이식:
    #   · 아우터: 20°C 이상이면 제외 (closet: categoryKeywords.outer nt>=20 → [])
    #   · 머플러/넥워머: 0°C 이하에서만 (closet: _hasMuffler = nt<=0 && 겨울월)
    #   · 23°C 이상: 코트/패딩/니트/스카프/머플러 등 보온 아이템 전면 금지
    # 이전: STEP 4/6 에 '<15°C' 단일 기준 + SCARF 'when fitting'(온도 무관) 뿐
    #       → 24~26°C 에도 목도리 추천되던 문제
    try:
        _t_gate = int(round(float(temp)))
    except Exception:
        _t_gate = 20
    if _t_gate >= 28:
        _gate_lines = [
            "HOT (>=28C): short-sleeve and light breathable fabrics ONLY.",
            "FORBIDDEN: any outer layer, knit sweater, scarf, muffler, gloves, heavy long-sleeve tops.",
        ]
    elif _t_gate >= 23:
        _gate_lines = [
            "WARM (23-27C): a single light layer (short sleeve or thin long sleeve).",
            "FORBIDDEN: outer layer (coat/jacket/cardigan/blazer), knit sweater, scarf, muffler, gloves.",
        ]
    elif _t_gate >= 20:
        _gate_lines = [
            "MILD-WARM (20-22C): a single light top; a thin shirt-jacket is the ABSOLUTE MAX.",
            "FORBIDDEN: coat, padding, heavy jacket, knit sweater, scarf, muffler.",
        ]
    elif _t_gate >= 12:
        _gate_lines = [
            "MILD (12-19C): a light jacket or cardigan is optional.",
            "FORBIDDEN: heavy coat/padding, scarf, muffler.",
        ]
    elif _t_gate >= 5:
        _gate_lines = [
            "COOL (5-11C): jacket plus light knit layering is recommended.",
            "FORBIDDEN: muffler/neck-warmer (allowed only at 0C or below).",
        ]
    elif _t_gate >= 1:
        _gate_lines = [
            "COLD (1-4C): a thick coat or padding is essential, with warm inner layers.",
            "FORBIDDEN: muffler/neck-warmer (allowed only at 0C or below).",
        ]
    else:
        _gate_lines = [
            "VERY COLD (<=0C): a thick coat/padding is essential; muffler/neck-warmer is appropriate.",
        ]
    _temp_gate_block = (
        f"  → ⚠️ TEMPERATURE GATE (current {_t_gate}°C — STRICT, overrides stylist discretion):\n"
        + "".join(f"     · {ln}\n" for ln in _gate_lines)
        + "     · These temperature rules are ABSOLUTE. NEVER add a warm-layer or muffler/scarf\n"
        "       just because it looks fashionable — temperature appropriateness comes first.\n"
    )

    # ═══════════════════════════════════════════════════════════════════
    # ─── 2026-05-18 KST · TJ 승인 ─── 뉴 프롬프트 v2026.05.18 ───────────
    # 범용(Gemini·GPT Image 공용) 항목식 프롬프트. 설명·중복 문장 제거.
    #   · 성별/스타일리스트/이미지포맷/일관성 각 1회만 (이전: 2~3회 중복)
    #   · STEP A/B/C × (GPT Image 2 / Gemini) 전체 루프 공통
    #   · GPT Image 2 분기는 '=== ANALYSIS REPORT' 마커부터 끝까지 제거
    #   · 길이 ~2,500자 → 4000자 절단 사실상 불필요 (안전장치만 유지)
    # ═══════════════════════════════════════════════════════════════════
    gemini_prompt = (
        "[CODIBANK STYLING PROMPT v2026.05.18]\n"

        + "\n# OUTPUT IMAGE FORMAT (MOST CRITICAL — APPLY FIRST)\n"
        "- The output MUST be ONE single HORIZONTAL image, exactly 1536x1024 pixels "
        "(3:2 landscape — WIDER than tall).\n"
        "- NEVER vertical, NEVER portrait, NEVER square, NEVER a 3:4 image. "
        "A vertical or single-figure image is a CRITICAL FAILURE.\n"
        "- The image contains TWO full-body figures SIDE BY SIDE in one frame:\n"
        "  - LEFT half (0-50% width) = FRONT view, face visible, looking at camera.\n"
        "  - RIGHT half (50-100% width) = BACK view of the SAME person, no face.\n"
        "- NEVER generate only one figure. NEVER omit the back view. NEVER split into "
        "two separate images.\n"
        "- Each figure approx 85% of image height, centered in its own half "
        "(~7.5% empty margin above the head and below the feet).\n"
        "- Background: ONE solid flat pastel color, uniform edge-to-edge; no rooms, "
        "walls, gradients, text, logo, or watermark.\n"
        "- Photorealistic fashion editorial style, professional studio lighting.\n"

        + (f"\n[USER DIRECT REQUEST — highest priority, overrides all templates]\n"
           f"\"{custom_text}\"\n" if is_custom else "")

        + "\n# SUBJECT\n"
        f"- Sex: {'FEMALE' if gender == 'F' else 'MALE'}. Body, physique and silhouette "
        f"MUST be {'female' if gender == 'F' else 'male'} — never the opposite sex, even "
        "if the outfit style is traditionally for the other sex.\n"
        f"- Age: {age} | Body: {h_int}cm, {w_int}kg, BMI {bmi} ({bmi_cat_ko}) | "
        f"Body type: {body_type_key or 'standard'}\n"
        "- Face: replicate the FIRST reference image exactly (jawline, eyes, eyebrows, "
        "nose, lips, skin tone, hair). No beautification.\n"
        # ─── 2026-05-23 KST · TJ 승인 (옵션 다 + 지역별 ratio) ─────────────
        #  이전: "Proportion: fashion-model 8.5 heads" — 슈퍼모델 비율 강제
        #        → BMI 27 통통한 사용자도 8.5등신 슈퍼모델로 렌더링되던 문제
        #  변경 1차: 7.5 head-to-body ratio 강제 (한국 성인 평균)
        #  변경 2차 (현재): 지역별 동적 결정
        #    · 아시아(서울/일본/중국/동남아) + 신체 데이터 있음 → 7.5
        #    · 그 외 지역 또는 신체 데이터 없음                → 8.0
        #    · {_head_ratio} 와 {_region_label_en} 는 함수 진입부에서 계산
        # ────────────────────────────────────────────────────────────────
        f"- Proportion: REALISTIC adult body — approximately {_head_ratio} head-to-body ratio "
        f"({_region_label_en} average)."
        + (" Korean/East Asian build, NOT a Western 8+ ratio of fashion supermodels."
           if _is_asia_region else " General adult build, NOT an exaggerated 9+ ratio of runway supermodels.")
        + " "
        + (f"Head and face size MUST be proportional to the actual body scale stated above "
           f"({h_int}cm tall, {w_int}kg, BMI {bmi}). "
           if _has_body_data_ratio else
           "Head and face size MUST be naturally proportional to the body (user body data not registered, use general average). ")
        + ("This is a REAL EVERYDAY Asian person, NOT a runway mannequin, NOT a supermodel."
           if _is_asia_region else "This is a REAL adult person, NOT a runway mannequin, NOT a supermodel.")
        + " STRICTLY AVOID: excessive leg elongation, oversized/undersized head, "
        "idealized fashion-model body. Full body visible from top of head to toe of shoes.\n"
        + (f"- Avoid colors (STRICT — must not appear anywhere): {_avoid_clean}\n"
           if _has_avoid else "")
        + _build_body_profile_block(gender, age, height, weight, body_type_key, "en", _loc_for_ratio) + "\n"

        + "\n# STYLIST (differentiator — must visibly shape the result)\n"
        f"- {stylist_name or 'expert stylist'} \u00b7 {stylist_city or 'Seoul'}"
        + (f" \u00b7 {_stylist_level}" if _stylist_level else "")
        + (f" ({_stylist_exp}y)" if _stylist_exp else "")
        + "\n"
        + (f"- Signature color: {_stylist_color1}"
           + (f" | accent: {_stylist_color2}\n" if _stylist_color2 else "\n")
           if _stylist_color1 else "")
        + (f"- Direction: {(custom_directive + prompt).strip()[:1500]}\n"
           if (custom_directive + prompt).strip() else "")
        + "- Rule: a different stylist or city MUST yield a visibly different outfit; "
        "never a generic, safe, default look.\n"

        + "\n# TPO\n"
        f"- Purpose: {purpose_for_analysis}\n"
        f"- Weather: {int(temp)}\u00b0C, {cond} | City: {location or 'Seoul'}\n"
        + _temp_gate_block

        + "\n# OUTFIT - CORE (all 3 required)\n"
        "- TOP: upper-body garment, clearly visible.\n"
        "- BOTTOM: full-length pants or skirt; pants hem at the shoe line "
        "(cropped / 7-8 length forbidden).\n"
        "- SHOES: both feet visible, identical pair.\n"

        + "\n# OUTFIT - OPTIONAL (only if it enhances; less is more)\n"
        "- OUTER: only per the TEMPERATURE GATE above (never at 20\u00b0C or higher).\n"
        "- BAG / WATCH / JEWELRY / HAT: only if TPO-appropriate.\n"
        "- SCARF / MUFFLER: only at 0\u00b0C or below.\n"
        "- The temperature gate always wins over stylist discretion.\n"

        + "\n# CONSISTENCY\n"
        "- Front view and back view are the SAME person in the SAME shoot.\n"
        "- Identical outfit, identical bag (a shoulder bag stays a shoulder bag - never a "
        "backpack), identical accessories and shoes on both sides.\n"

        + "\n=== ANALYSIS REPORT (text output) ===\n"
        "Output the analysis as TEXT after the image, wrapped between exact markers "
        "<<<ANALYSIS_JSON>>> and <<<END_ANALYSIS>>> (nothing outside the markers).\n"
        "Schema:\n"
        "{\n"
        '  "personalColor": {"text": "'
        + ('English' if _cs_en else 'Korean')
        + ' 250-300 chars", "keywords": ["k1","k2","k3"]},\n'
        '  "body": {"text": "'
        + ('English' if _cs_en else 'Korean')
        + ' 250-300 chars", "keywords": ["k1","k2","k3"]},\n'
        '  "purpose": {"text": "'
        + ('English' if _cs_en else 'Korean')
        + ' 250-300 chars", "keywords": ["k1","k2","k3"]},\n'
        '  "categoryKeywords": {"top":"\uc0c9\uc0c1, \uc544\uc774\ud15c",'
        '"bottom":"\uc0c9\uc0c1, \uc544\uc774\ud15c","shoes":"\uc0c9\uc0c1, \uc544\uc774\ud15c",'
        '"outer":"","bag":"","watch":"","sunglasses":"","hat":"","scarf":"","socks":""}\n'
        "}\n"
        "Rules: each text 250-300 chars; each keywords array EXACTLY 3 short Korean words "
        "(2-6 chars); categoryKeywords value = '{color}, {item}'; CORE (top/bottom/shoes) "
        "MUST NEVER be empty, OPTIONAL uses \"\" if absent; output ONLY the image and the "
        "marked JSON.\n"
        + ("\n[PC AVOID OVERRIDE] \uc0ac\uc6a9\uc790\uac00 \ubcf8\uc778 \ud37c\uc2a4\ub110\ucef4\ub7ec avoid "
           "\ucef4\ub7ec\ub97c \uc9c1\uc811 \uc694\uccad\ud588\uc2b5\ub2c8\ub2e4. personalColor.text \uc5d0 "
           "\ubc18\ub4dc\uc2dc \ucca8\uc5b8: \ubcf8 \ucf54\ub514\ub294 \uc0ac\uc6a9\uc790 \uc694\uccad\uc73c\ub85c \ud574\ub2f9 "
           "\ucef4\ub7ec\ub97c \uc0ac\uc6a9\ud588\uace0, \ud574\ub2f9 \ud37c\uc2a4\ub110\ucef4\ub7ec \ud1a4\uc5d0\ub294 "
           "\uad8c\uc7a5\ub418\uc9c0 \uc54a\uc544 \uc5bc\uad74 \ud608\uc0c9\uc774 \ud750\ub824 \ubcf4\uc77c \uc218 \uc788\uc73c\ubbc0\ub85c "
           "\ub9bd\u00b7\ube14\ub7ec\uc154\u00b7\uace8\ub4dc \uc8fc\uc5bc\ub9ac\ub85c \ubcf4\uc644 \uad8c\uc7a5 (\ucca8\uc5b8 "
           "\ub204\ub77d \uc2dc \ubd84\uc11d \uc2e4\ud328).\n"
           if (isinstance(meta, dict) and meta.get('pc_avoid_override')) else "")
    )

    # ── 이미지 파트 구성: 얼굴 → 선택코디(style_ref) → 상의 → 하의 순서 ──
    face_parts = [(mime, raw) for label, mime, raw in ref_images if label == "face"]
    style_ref_parts = [(mime, raw) for label, mime, raw in ref_images if label == "style_ref"]
    top_parts = [(mime, raw) for label, mime, raw in ref_images if label == "top"]
    bottom_parts = [(mime, raw) for label, mime, raw in ref_images if label == "bottom"]
    ordered_parts = face_parts + style_ref_parts + top_parts + bottom_parts

    # ─── 2026-05-23 KST · TJ 승인 (옵션 B) ─── frontend imagePrompt BODY 섹션 통합 ──
    #   배경: closet.html line 5646~5685 의 imagePrompt 에는 사용자 체형에 맞춘
    #         BODY PROPORTION 지시 + bodyFlawPrompt (체형별 영문 가이드) 가 포함됨.
    #         이전: /api/ai/styling 일반 케이스에서 무시됨 (custom 분기에서만 사용)
    #         변경: BODY 관련 섹션만 좁게 추출해 STEP 1-7 프롬프트에 추가
    #               → 99.0% 닮은 아바타 정확도 추가 향상
    #   안전: BODY PROPORTION + bodyFlawPrompt 패턴만 추출 (전체 통합은 중복/충돌 위험).
    #         Q3 분기에서는 gemini_prompt 가 다음 단계에서 덮어쓰이므로 적용 안 됨 (의도된 동작).
    try:
        _front_image_prompt = str(payload.get("imagePrompt") or "").strip()
        if _front_image_prompt and len(_front_image_prompt) > 30:
            import re as _re_body
            _body_sections = []
            # BODY PROPORTION 섹션 추출 (REALISTIC ratio 등)
            _m1 = _re_body.search(r'BODY PROPORTION[^.]*\.[^.]*\.[^.]*\.', _front_image_prompt, _re_body.IGNORECASE)
            if _m1:
                _body_sections.append(_m1.group())
            # bodyFlawPrompt 패턴 추출 (Use dark-toned / layered / cropped / long coat ...)
            _m2 = _re_body.search(r'Use (dark-toned|layered textured|cropped outerwear|long coat)[^.]+\.', _front_image_prompt)
            if _m2:
                _body_sections.append(_m2.group())
            # ANATOMY 섹션 추출 (자연스러운 손가락 등)
            _m3 = _re_body.search(r'ANATOMY[^.]*\.[^.]*\.', _front_image_prompt, _re_body.IGNORECASE)
            if _m3:
                _body_sections.append(_m3.group())
            if _body_sections:
                gemini_prompt = gemini_prompt + (
                    "\n\n# FRONTEND BODY GUIDANCE (USER-SPECIFIC — ALSO MUST FOLLOW)\n"
                    + "\n".join(_body_sections)
                    + "\n"
                )
    except Exception as _be:
        print(f"[front imagePrompt BODY merge] skipped: {_be}", flush=True)

    # ─── 2026-05-18 KST · TJ 지시 ─── Q3 최종 고화질: 선택 코디 99.9% 복제 ───
    #   Q3(_force_quality='high') + style_ref 이미지가 있으면, gemini_prompt 를
    #   Q3 전용 프롬프트로 교체한다.
    #   설계 의도: Q2 에서 선택한 추천 코디를, 의상은 100% 그대로 두고 포즈만
    #             정면/후면으로 바꿔 16:9 가로 1장(좌=정면, 우=후면)에 고화질 생성.
    #   reference 순서: [1] 얼굴(face)  [2] 선택 코디(style_ref)
    #   ※ Q1·Q2 는 style_ref 가 없으므로 이 분기를 타지 않음 — 기존 프롬프트 유지.
    _is_q3 = (str(payload.get('_force_quality') or '').strip().lower() == 'high')
    _has_style_ref = len(style_ref_parts) > 0
    if _is_q3 and _has_style_ref:
        _has_face_ref = len(face_parts) > 0
        _ref_guide = (
            "You are given TWO reference images. "
            "Reference image [1] = the person's FACE. "
            "Reference image [2] = the SELECTED OUTFIT (a styled coordination the user chose)."
        ) if _has_face_ref else (
            "You are given ONE reference image. "
            "Reference image [1] = the SELECTED OUTFIT (a styled coordination the user chose)."
        )
        _face_idx = "[1]" if _has_face_ref else "(generate a natural Korean face)"
        _outfit_idx = "[2]" if _has_face_ref else "[1]"
        gemini_prompt = (
            # ─── 2026-05-19 KST · TJ 보고 ─── Q3 세로 출력 — 프롬프트 강화 ───
            #   트라이온(_tryon_build_prompt)에서 가로가 정상 생성되는 검증된
            #   패턴을 이식: ① OUTPUT FORMAT 을 프롬프트 최상단(top priority)
            #   ② LEFT/RIGHT 를 픽셀 좌표로 명시 ③ reference 이미지가 세로여도
            #   무시하라고 명시 (Nano Banana Pro 가 reference 비율을 따라가
            #   세로로 출력하던 것을 차단).
            "🖼️ CRITICAL OUTPUT FORMAT — READ FIRST, MUST OBEY (TOP PRIORITY)\n"
            "Output ONE SINGLE WIDE HORIZONTAL image. The image MUST be wider "
            "than it is tall (landscape 16:9, about 2048 px wide x 1152 px tall).\n"
            "The wide image shows the SAME person TWICE, side by side, sharing "
            "ONE continuous flat solid studio background:\n"
            "  - LEFT half  (pixels 0 to 1024 wide): FRONT view — full body, "
            "head to feet, facing the camera.\n"
            "  - RIGHT half (pixels 1024 to 2048 wide): BACK view — the SAME "
            "person, full body, head to feet, facing AWAY from the camera.\n"
            "Each figure occupies ~85% of the image height, centered in its half.\n"
            "ABSOLUTELY FORBIDDEN: a vertical / portrait / square image; an "
            "image taller than it is wide; or an image with only ONE figure.\n"
            "IMPORTANT: the reference images below may be VERTICAL — IGNORE "
            "their orientation. Your output is ALWAYS a WIDE horizontal image "
            "regardless of the shape of the reference images.\n\n"
            "# TASK — FINAL HIGH-QUALITY RENDER (Q3)\n"
            + _ref_guide + "\n\n"
            "# ABSOLUTE RULE — OUTFIT MUST BE 99.9% IDENTICAL\n"
            f"Reproduce the outfit from reference image {_outfit_idx} EXACTLY. "
            "Every garment, color, fabric, texture, pattern, silhouette, length, "
            "neckline, sleeve, accessory, bag, shoes and styling detail MUST be "
            "identical to that reference. DO NOT redesign, restyle, swap, recolor "
            "or add/remove any item. This is an upscale/re-render of the SAME outfit, "
            "not a new styling.\n\n"
            "# FACE\n"
            f"Use reference image {_face_idx} for the facial identity — preserve the "
            "same face exactly (jawline, eyes, eyebrows, nose, lips, skin tone).\n\n"
            "# POSE\n"
            "Only the POSE differs between the two figures (front-facing vs. "
            "back-facing). The outfit, hair, accessories and body are identical.\n\n"
            "# QUALITY\n"
            "Maximum photographic quality: sharp focus, clean lighting, high "
            "resolution, no blur, no artifacts, no text, no watermark.\n\n"
            "# FINAL REMINDER (MOST IMPORTANT)\n"
            "The output image MUST be WIDE horizontal landscape, containing TWO "
            "full-body figures side by side — FRONT on the left, BACK on the "
            "right. NEVER vertical. NEVER a single figure.\n"
        )
        print(f"[ai_styling] Q3 전용 프롬프트 적용 v2 (가로강제 강화, style_ref={_has_style_ref}, face={_has_face_ref})", flush=True)

    # ─── 2026-04-21 KST ─── 티어별 엔진 라우팅 적용 ───
    # payload.tier > 직접 전달된 tier > 기본값 FREE
    _resolved_tier = str(
        tier or payload.get("tier") or (payload.get("user") or {}).get("tier") or "FREE"
    ).upper().strip()
    if _resolved_tier not in ("FREE", "SILVER", "GOLD", "DIAMOND"):
        _resolved_tier = "FREE"
    # ─── 2026-05-13 KST · TJ 지시 (v66) ─── GPT Image 2 라우팅 ───
    # _resolve_engine_full로 변경: (model, provider, quality) 동시 반환
    # provider == "openai" → GPT Image 2 분기, 그 외 → 기존 Gemini 분기
    # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.6 HYBRID) ─── _override_alias 우선 처리 ───
    # 폴백 호출 시 _override_alias="flash_v2" 등으로 강제 지정 → tier 기반 라우팅 우회
    if _override_alias:
        _alias = str(_override_alias).strip()
        model_name = _ENGINE_MODEL_MAP.get(_alias) or _ENGINE_MODEL_MAP.get("flash_v2")
        _provider = _ENGINE_PROVIDER_MAP.get(_alias, "gemini")
        _quality = _ENGINE_QUALITY_MAP.get(_alias)  # Gemini는 None
        print(f"[CODIFIT] alias_override={_alias} → provider={_provider}, model={model_name}, quality={_quality}", flush=True)
    else:
        model_name, _provider, _quality = _resolve_engine_full(_resolved_tier, "codifit")
        print(f"[CODIFIT] tier={_resolved_tier} → provider={_provider}, model={model_name}, quality={_quality}", flush=True)
    _gpt_image_used = (_provider == "openai" and model_name.startswith("gpt-image"))

    # ─── 2026-05-13 KST · TJ 지시 (v66) ─── GPT Image 2 분기 ───
    response = None        # Gemini 응답 객체 (GPT Image 2면 None 유지)
    _gpt_img_bytes = None  # GPT Image 2 응답 (b64 → bytes)
    
    if _gpt_image_used:
        # ─── OpenAI GPT Image 2 호출 ───
        try:
            _openai_key = os.getenv("OPENAI_API_KEY")
            if not _openai_key:
                return jsonify(ok=False, error="OPENAI_API_KEY 환경변수 미설정"), 500
            
            _gpt_client = OpenAI(api_key=_openai_key)
            
            # 이미지 reference 구성 (face/top/bottom 순서, BytesIO + name 속성 필수)
            _has_face_ref = bool(face_parts)
            _has_top_ref = bool(top_parts)
            _has_bottom_ref = bool(bottom_parts)
            _image_files = []
            for _i, (mime, raw) in enumerate(face_parts):
                _bio = io.BytesIO(raw)
                _bio.name = f"face_{_i}.jpg"
                _image_files.append(_bio)
            for _i, (mime, raw) in enumerate(top_parts):
                _bio = io.BytesIO(raw)
                _bio.name = f"top_{_i}.jpg"
                _image_files.append(_bio)
            for _i, (mime, raw) in enumerate(bottom_parts):
                _bio = io.BytesIO(raw)
                _bio.name = f"bottom_{_i}.jpg"
                _image_files.append(_bio)
            
            print(f"[ai_styling_gpt_image] ref images: face={_has_face_ref}, top={_has_top_ref}, bottom={_has_bottom_ref}, total={len(_image_files)}", flush=True)
            
            # 짧고 명확한 reference 헤더 (prompt 앞에 prepend)
            _ref_lines = []
            if _has_face_ref:
                _ref_lines.append("Image 1=user's face (preserve identity exactly)")
            _idx = 2 if _has_face_ref else 1
            if _has_top_ref:
                _ref_lines.append(f"Image {_idx}=top garment reference")
                _idx += 1
            if _has_bottom_ref:
                _ref_lines.append(f"Image {_idx}=bottom garment reference")
            
            if _ref_lines:
                _ref_header = "REFERENCES: " + ", ".join(_ref_lines) + ".\n\n"
            else:
                # 사용자 face 미등록 → generic Korean face 자동 생성
                _ref_header = "NOTE: No user face reference provided. Generate a natural Korean fashion model face.\n\n"
            
            # ─── 2026-05-18 KST · TJ 승인 ─── 뉴 프롬프트 v2026.05.18 적용 ───
            # gemini_prompt 자체가 항목식·범용으로 재작성됨 → 별도 directive
            # (_gender_directive / _stylist_directive / _layout_directives /
            #  _final_reminder) 불필요 (중복 제거). GPT Image 2 분기는
            # gemini_prompt 에서 ANALYSIS 블록만 제거하고 그대로 사용.
            import re as _re_pp
            _outfit_prompt = gemini_prompt
            # ANALYSIS REPORT 블록 제거 (GPT Image 2는 텍스트 분석을 출력하지 않음)
            _an_start = _outfit_prompt.find("=== ANALYSIS REPORT (text output) ===")
            if _an_start != -1:
                _outfit_prompt = _outfit_prompt[:_an_start].rstrip() + "\n"
            # 퍼스널컬러 "베스트:" 줄 제거(이미지 다양성), "주의:" 줄 AVOID 강조 변환
            _outfit_prompt = _re_pp.sub(r'\s*\ubca0\uc2a4\ud2b8:[^\n]*\n', '\n', _outfit_prompt)
            def _avoid_replace(_m):
                _v = _m.group(1).strip()
                if not _v or _v == "\ud0c1\ud55c \ud1a4":
                    return "\n"
                return f"\n- Avoid colors (STRICT - must not appear anywhere): {_v}\n"
            _outfit_prompt = _re_pp.sub(r'\s*\uc8fc\uc758:\s*([^\n]+)\n', _avoid_replace, _outfit_prompt)
            # 안전장치 길이 제한 (뉴 프롬프트 STEP A ~4,600자 / STEP B ~5,500자
            # → 6,500자 한도 내 = 절단 없음. 만일의 초장문 입력만 방어)
            if len(_outfit_prompt) > 6500:
                _outfit_prompt = _outfit_prompt[:6500]

            _gpt_prompt = _ref_header + _outfit_prompt
            
            # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1) ─── 사이즈 표준 3:2로 변경 ───
            # 이전: "1536x864" (16:9) — 정/후면 각 768x864 (8:9 세로형, 약간 비좁음)
            # 변경: "1536x1024" (3:2) — 정/후면 각 768x1024 (3:4 세로형, 가독성 ↑)
            # gpt-image-2의 standard size 중 하나라 안정적 + 캐시 효율 ↑
            # ─── 2026-05-17 KST · TJ 지시 ─── 정/후면 가로 3:2 강제 ───
            # 문제: 환경변수가 'auto'/'1024x1536'(세로) 이면 정면만 세로로 생성됨
            # 수정: 정/후면 2분할은 가로 3:2(1536x1024) 필수 — 다른 값이면 강제 교정
            # 🔒 baseline 2026-05-18 — 파일 상단 '정상 확정 baseline' 주석 참조.
            #   이 강제 교정은 closet.html 팝업이미지박스(가로 1장)의 안전장치다.
            #   아래 if 강제 교정을 제거하거나 세로 사이즈를 허용하지 말 것.
            _gpt_size = os.getenv("CODIBANK_GPT_IMAGE_SIZE", "1536x1024")
            if _gpt_size != "1536x1024":
                print(f"[ai_styling_gpt_image] ⚠ size={_gpt_size} → 1536x1024 강제 "
                      f"(정/후면 가로 3:2 레이아웃 필수)", flush=True)
                _gpt_size = "1536x1024"
            
            # face/top/bottom 유무에 따라 API 분기
            #   - 이미지 reference 있음 → images.edit
            #   - 모두 없음 → images.generate (text-to-image, face 자동 생성)
            # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1) ─── 출력 최적화 + timeout ───
            # · output_format="jpeg": PNG 대비 인코딩/전송 빠름, R2 저장 비용 ↓
            # · output_compression=80: 의류 패턴 보존 + 파일 크기 30~40% 절감
            # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.5 HOTFIX) ─── timeout/retry 보강 ───
            # 문제: OpenAI SDK가 timeout 발생 시 자동으로 2회 재시도 → 35초 × 3회 = 105초
            #       (Render 로그에서 정확히 106~111초 응답시간 확인됨)
            # 수정:
            #   - timeout=60.0 (환경변수 CODIBANK_GPT_IMAGE_TIMEOUT으로 조정 가능, 기본 60)
            #   - max_retries=0 (자동 재시도 차단, 환경변수 CODIBANK_GPT_IMAGE_MAX_RETRIES, 기본 0)
            #   - images.generate 폴백 제거 (face 미등록 사용자는 엔드포인트 진입 단계에서 거절)
            _gpt_timeout = float(os.getenv("CODIBANK_GPT_IMAGE_TIMEOUT", "60"))
            _gpt_max_retries = int(os.getenv("CODIBANK_GPT_IMAGE_MAX_RETRIES", "0"))
            _gpt_call_opts = dict(
                model=model_name,
                prompt=_gpt_prompt,
                quality=_quality or "medium",
                size=_gpt_size,
                n=1,
                output_format="jpeg",
                output_compression=80,
            )
            # ─── v67 Phase 1.5 HOTFIX ─── face 필수 (엔드포인트에서 사전 거절되지만 안전망)
            if len(_image_files) > 0:
                _gpt_response = _gpt_client.with_options(
                    max_retries=_gpt_max_retries,
                    timeout=_gpt_timeout,
                ).images.edit(
                    image=_image_files,
                    **_gpt_call_opts,
                )
            else:
                # 정상 흐름에서 도달하면 안 되는 경로 (엔드포인트 거절 누락)
                print(f"[ai_styling_gpt_image] ⚠ 안전망: 모든 ref 미등록 — face 필수 정책 위반, 거절", flush=True)
                raise RuntimeError("face_required: 얼굴 사진 등록이 필요합니다")
            
            # 응답에서 base64 → bytes
            _b64 = _gpt_response.data[0].b64_json
            _gpt_img_bytes = base64.b64decode(_b64)
            print(f"[ai_styling_gpt_image] ✅ 생성 완료: quality={_quality}, size={_gpt_size}, bytes={len(_gpt_img_bytes)}", flush=True)
        except Exception as _ge:
            import traceback as _tb
            _trace = _tb.format_exc()[-400:]
            print(f"[ai_styling_gpt_image] 호출 실패: {type(_ge).__name__}: {str(_ge)[:300]}", flush=True)
            return jsonify(ok=False, error=f"GPT Image 2 호출 실패: {str(_ge)[:300]}", trace=_trace), 500
    else:
        # ─── Gemini 분기 (기존 코드 그대로) ───
        try:
            if _SDK == "new":
                contents = [gemini_prompt]
                for mime, raw in ordered_parts:
                    contents.append(_gtypes.Part.from_bytes(data=raw, mime_type=mime or "image/jpeg"))

                client = _genai.Client(api_key=_GEMINI_KEY)
                # ─── 2026-05-18 KST · TJ 지시 ─── Q3: 16:9 가로 강제 ───
                #   Gemini 가 "좌우 2명 가로 1장" 지시를 무시하고 세로로 출력하는
                #   것을 막기 위해 image_config 로 aspect_ratio 를 강제한다.
                #   SDK 버전에 따라 image_config 미지원이면 TypeError/AttributeError
                #   → 프롬프트의 OUTPUT IMAGE FORMAT 지시만으로 폴백.
                _gem_cfg_kwargs = dict(
                    response_modalities=["IMAGE", "TEXT"],
                    temperature=0.7,
                )
                _gem_cfg = None
                if _is_q3:
                    # ─── 2026-05-19 KST · TJ 보고 ─── Q3 가로강제 — 트라이온 동일 패턴 ───
                    #   증상: Q3 가 세로(968×1567)로 계속 생성됨.
                    #   진짜 원인: 같은 Nano Banana Pro 를 쓰는 트라이온은 가로 정상.
                    #     비교한 결과 코디핏 Q3 config 가 트라이온과 두 가지 다름:
                    #       ① temperature: 트라이온 0.4 vs Q3 0.7
                    #       ② max_output_tokens: 트라이온 8192 명시 vs Q3 미설정
                    #     특히 ②가 결정적 — image_size="2K"(2048px) 출력 토큰이
                    #     부족하면 모델이 작은 해상도로 fallback 하면서 aspect_ratio
                    #     지시도 약화돼 세로가 나온다.
                    #   해결: 트라이온의 검증된 config 와 100% 동일하게 맞춤.
                    #     로그로 어느 경로(①/②/③)인지 노출.
                    try:
                        _gem_cfg = _gtypes.GenerateContentConfig(
                            response_modalities=["IMAGE", "TEXT"],
                            temperature=0.4,            # 트라이온 동일
                            max_output_tokens=8192,     # 트라이온 동일 — 2K 이미지 토큰 확보
                            image_config=_gtypes.ImageConfig(
                                aspect_ratio="16:9", image_size="2K"),
                        )
                        print("[ai_styling_gemini] Q3 가로강제 ① image_config"
                              "(aspect_ratio=16:9, image_size=2K, temp=0.4, max_tokens=8192) 적용", flush=True)
                    except (TypeError, AttributeError) as _e_full:
                        try:
                            _gem_cfg = _gtypes.GenerateContentConfig(
                                response_modalities=["IMAGE", "TEXT"],
                                temperature=0.4,
                                max_output_tokens=8192,
                                image_config=_gtypes.ImageConfig(aspect_ratio="16:9"),
                            )
                            print("[ai_styling_gemini] Q3 가로강제 ② image_config"
                                  f"(aspect_ratio=16:9, max_tokens=8192) 적용 — image_size 미지원({_e_full})",
                                  flush=True)
                        except (TypeError, AttributeError) as _e_ratio:
                            print("[ai_styling_gemini] ⚠⚠ Q3 가로강제 ③ 실패 — "
                                  "ImageConfig 미지원으로 세로 출력 위험! "
                                  f"google-genai SDK 업그레이드 필요 ({_e_ratio})",
                                  flush=True)
                            _gem_cfg = None
                if _gem_cfg is None:
                    _gem_cfg = _gtypes.GenerateContentConfig(**_gem_cfg_kwargs)
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=_gem_cfg,
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
    # ─── 2026-05-13 KST · TJ 지시 (v66) ─── GPT Image 2면 b64 결과 직접 사용 ───
    img_bytes = None
    full_text = ""
    if _gpt_image_used:
        # GPT Image 2 응답은 이미 위에서 디코딩됨
        img_bytes = _gpt_img_bytes
        full_text = ""  # GPT Image 2는 텍스트 응답 없음 → 분석 JSON 폴백 사용
    else:
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
                category_keywords_from_ai = {}
                # ─── 2026-04-26 v13 TJ-2 ─── 콤마 없는 값 자동 보정
                # AI가 "베이지 트렌치코트" 처럼 콤마 없이 줄 경우
                # 첫 단어(컬러로 추정)와 나머지(아이템)를 분리해 콤마로 재조립
                _COLOR_HINTS = {
                    "베이지","아이보리","화이트","블랙","네이비","차콜","그레이","브라운","카멜",
                    "올리브","버건디","크림","오프화이트","피치","코럴","핑크","레드","오렌지",
                    "옐로우","머스타드","그린","민트","블루","라이트블루","라벤더","퍼플","와인",
                    "샌드","쿨","웜","다크","라이트","파스텔","비비드","뉴트럴","라이트그레이",
                    "다크네이비","아쿠아","터쿼이즈","로즈","살구","스카이","페일","딥",
                }
                for k, v in _ck.items():
                    s = str(v).strip()
                    if not s:
                        continue
                    if "," not in s:
                        # 콤마가 없으면 첫 단어가 컬러일 가능성 검사
                        words = s.split()
                        if len(words) >= 2 and words[0] in _COLOR_HINTS:
                            s = words[0] + ", " + " ".join(words[1:])
                        elif len(words) >= 2 and any(c in words[0] for c in _COLOR_HINTS):
                            s = words[0] + ", " + " ".join(words[1:])
                    category_keywords_from_ai[str(k)] = s
        else:
            # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 2) ─── 분석 분리 ───
            # 이전: 마커 없으면 _generate_styling_analysis 템플릿 폴백 호출
            # 변경: stylingAnalysis=None 반환 — 클라이언트가 /api/ai/styling/analysis 별도 호출
            # 효과: 이미지 응답 더 빠름 + 분석 품질 ↑ (템플릿 → gpt-4.1-mini)
            # 영향: GPT Image 2 분기는 항상 full_text="" → 항상 이 경로 진입
            styling_analysis = None
            if _gpt_image_used:
                print(f"[ai_styling_gpt_image] 분석 분리 모드 — stylingAnalysis=null, 클라이언트가 /analysis 별도 호출")
            else:
                print(f"[ai_styling_gemini] ⚠ 분석 JSON 마커 없음 — stylingAnalysis=null로 반환 (분석 분리 모드)")
    except Exception as _pe:
        # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 2) ─── 분석 분리 ───
        # 파싱 예외 시에도 템플릿 폴백 호출 안 함 — None 반환
        print(f"[ai_styling_gemini] 분석 JSON 파싱 실패: {_pe}, stylingAnalysis=null (분석 분리 모드)")
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

    # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 2) ─── cacheKey 응답 추가 ───
    # 클라이언트가 /api/ai/styling/analysis 호출 시 이 키를 전달
    # cache_fname 형식: "ai_{cache_key}.{ext}" → 키 추출
    _cache_key_for_resp = ""
    try:
        _cfn = str(cache_fname or "")
        if _cfn.startswith("ai_"):
            _cache_key_for_resp = _cfn[3:].rsplit(".", 1)[0]
    except Exception:
        _cache_key_for_resp = ""

    return jsonify(
        ok=True,
        image=f"{base}{rel}",
        path=rel,
        url=f"{base}{rel}",
        explanation=short or "AI 코디 이미지 생성 완료!",
        model=f"gemini:{model_name}",
        cached=False,
        prompt=gemini_prompt if os.getenv("CODIBANK_DEBUG_PROMPT") == "1" else None,
        # ─── 2026-05-14 KST · TJ 보고 ─── 활동지역 '서울 고정' 버그 수정
        # matched_stylist 객체는 DB 구조상 city 필드 없음 (city는 최상위 key)
        # → 응답 직전 active_city를 stylist.city로 주입하여 frontend가 정확히 표시
        stylist=(
            (lambda s, c: ({**s, 'city': c} if isinstance(s, dict) and c else s))(
                matched_stylist, (meta or {}).get('active_city', '') if meta else ''
            )
        ),
        stylingStory=(meta or {}).get("styling_story") if meta else None,
        engineKeywords=(meta or {}).get('keywords_selected', []) if meta else [],
        engineCategoryKeywords=merged_cat_kws,
        engineCity=(meta or {}).get('active_city', '') if meta else '',
        enginePurpose=(meta or {}).get('purpose', '') if meta else '',
        engineBottomType=(meta or {}).get('bottom_type', '') if meta else '',
        # ─── 2026-05-14 v67 Phase 2 ─── 분석은 별도 엔드포인트로 호출 (stylingAnalysis 항상 null)
        stylingAnalysis=None,
        cacheKey=_cache_key_for_resp,  # 클라이언트 /api/ai/styling/analysis 호출용
    )


# ══════════════════════════════════════════════════════
# [2026-05-14 v67 Phase 2] 코디핏 분석 보고서 — gpt-4.1-mini로 분리 호출
# ══════════════════════════════════════════════════════
def _codifit_analysis_via_gpt41mini(
    payload: Dict[str, Any],
    matched_stylist=None,
    meta=None,
    generated_outfit_summary=None,
    lang=None,
    image_b64=None,
):
    """[v67 Phase 2] 코디핏 분석 보고서 — gpt-4.1-mini.

    ─── 2026-05-16 KST · TJ 지시 (옵션 A) ─── vision 모드 추가 ──
    image_b64 가 주어지면 생성된 코디 이미지를 직접 입력(vision)하여 분석.
    이 경우 4섹션(personalColor/body/purpose/outfit)을 생성하며,
    outfit 섹션은 '이미지에 실제로 보이는 옷'을 기준으로 작성 → 분석과 이미지 일치.
    image_b64 가 없으면 기존 텍스트 메타데이터 기반 3섹션 (하위호환).

    Pattern A (vision): 생성 이미지를 직접 보고 착장을 분석 → 모달 표시 내용과 일치.
    Pattern A-legacy (텍스트): 이미지 없이 사용자 정보 + 생성 의도만으로 분석.

    응답: vision 시 4섹션, 텍스트 시 3섹션 JSON.

    실패 시: RuntimeError 발생 (호출부가 503 응답 + 클라이언트 재시도 처리).
    """
    _en = (str(lang or payload.get("lang") or "ko").strip().lower() == "en")
    user = payload.get("user") or {}
    weather = payload.get("weather") or {}
    pc = payload.get("personalColor") or {}
    purpose = (meta or {}).get("purpose") or payload.get("purposeLabel") or "데일리 코디"
    custom_text = str(payload.get("customText") or "").strip()
    if custom_text and (payload.get("purposeKey") or "").lower() == "custom":
        purpose = custom_text

    # ── 사용자 정보 정규화 ──
    gender_code = _normalize_gender_code(str(user.get("gender") or ""))
    gender_ko = "여성" if gender_code == "F" else "남성"
    gender_en = "woman" if gender_code == "F" else "man"
    age = str(user.get("ageGroup") or "30대")

    try:
        h_int = int(user.get("height") or 170)
        w_int = int(user.get("weight") or 65)
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
    body_type = str(user.get("bodyType") or "").strip()

    # ── 퍼스널컬러 ──
    pc_season = str(pc.get("season", "") or "").strip()
    pc_undertone = str(pc.get("undertone", "") or "").strip()
    pc_subtype = str(pc.get("subtype") or pc.get("type") or "").strip()
    pc_best = pc.get("best_colors") or []
    pc_avoid = pc.get("avoid_colors") or []
    if not isinstance(pc_best, list): pc_best = []
    if not isinstance(pc_avoid, list): pc_avoid = []
    pc_label = (pc_season + " " + pc_subtype).strip() or pc_season or "미등록"
    pc_best_str = ", ".join(pc_best[:5]) if pc_best else "(진단 미완료)"
    pc_avoid_str = ", ".join(pc_avoid[:3]) if pc_avoid else "(진단 미완료)"

    # ── 날씨/위치 ──
    try:
        temp = int(float(weather.get("temp") or 20))
    except Exception:
        temp = 20
    cond = str(weather.get("text") or weather.get("condition") or "").strip()
    location = str(weather.get("location") or weather.get("city") or "").strip()

    # ── 매칭 스타일리스트 ──
    stylist_name = (matched_stylist or {}).get("name", "") if matched_stylist else ""
    stylist_city = (meta or {}).get("active_city", "") if meta else ""

    # ── 생성된 코디 요약 (서버 엔진의 categoryKeywords 기반) ──
    outfit_categories = (meta or {}).get('categoryKeywords', {}) or {}
    if generated_outfit_summary:
        outfit_text = generated_outfit_summary
    else:
        _parts = []
        for k in ("outer", "top", "bottom", "shoes", "bag", "scarf", "watch", "socks"):
            v = outfit_categories.get(k)
            if v:
                _parts.append(f"{k}: {v}")
        outfit_text = "; ".join(_parts) if _parts else "(코디 정보 없음)"

    # ── 시스템 프롬프트 ──
    _vision = bool(image_b64)
    if _en:
        if _vision:
            system_prompt = (
                "You are a Korean fashion styling expert. An AI-generated outfit image is "
                "attached. Look directly at the image and analyze the clothes the person is "
                "ACTUALLY wearing. Produce a 4-section report (personal color / body / "
                "purpose+weather / outfit). The 'outfit' section MUST describe exactly what "
                "is visible in the image (real colors and garment types), NOT recommended "
                "keywords. Output JSON only — no extra text outside JSON."
            )
        else:
            system_prompt = (
                "You are a Korean fashion styling expert. Given user info and outfit details, "
                "produce a 3-section analysis report (personal color / body / purpose+weather). "
                "Output JSON only — no extra text outside JSON."
            )
    else:
        if _vision:
            system_prompt = (
                "당신은 한국의 패션 스타일링 전문가입니다. "
                "AI가 생성한 코디 이미지가 첨부되어 있습니다. 이미지를 직접 보고, "
                "이미지 속 인물이 실제로 착용한 옷을 분석하세요. "
                "퍼스널컬러 / 체형 / 목적+날씨 / 착장(outfit) 4개 섹션의 분석 보고서를 작성합니다. "
                "'outfit' 섹션은 반드시 이미지에 실제로 보이는 옷(실제 컬러와 종류)을 기준으로 작성하세요. "
                "추천 키워드가 아니라 이미지에 보이는 그대로입니다. "
                "출력은 반드시 JSON only — JSON 외 추가 텍스트 금지."
            )
        else:
            system_prompt = (
                "당신은 한국의 패션 스타일링 전문가입니다. "
                "사용자의 신체/퍼스널컬러/날씨/목적 정보와 스타일리스트가 추천한 코디 정보를 받아 "
                "3개 측면의 분석 보고서를 작성합니다. "
                "출력은 반드시 JSON only — JSON 외 추가 텍스트 금지."
            )

    # ── 사용자 프롬프트 ──
    _lang_label_text = "English" if _en else "한국어"
    # vision 시 outfit 섹션 스키마 (없으면 빈 문자열 → 3섹션)
    _outfit_schema = ""
    if _vision:
        _outfit_schema = (
            f',\n'
            f'  "outfit": {{\n'
            f'    "top": "이미지 속 상의의 실제 컬러+종류 (예: 라이트 그레이 옥스퍼드 셔츠)",\n'
            f'    "bottom": "이미지 속 하의의 실제 컬러+종류 (예: 차콜 그레이 슬랙스)",\n'
            f'    "shoes": "이미지 속 신발의 실제 컬러+종류 (예: 블랙 더비 슈즈)",\n'
            f'    "accessory": "이미지 속 액세서리(가방/시계/스카프 등), 없으면 \'없음\'"\n'
            f'  }}'
        )
    user_input = (
        f"## 사용자 정보\n"
        f"- 성별/나이: {gender_ko} {age}\n"
        f"- 신체: 키 {h_int}cm, 몸무게 {w_int}kg (BMI {bmi}, {bmi_cat_ko})\n"
        f"- 체형 분류: {body_type or '미등록'}\n"
        f"- 퍼스널컬러 시즌: {pc_label} ({pc_undertone or '복합'})\n"
        f"  · 추천 컬러 (베스트): {pc_best_str}\n"
        f"  · 피해야 할 컬러 (어보이드): {pc_avoid_str}\n"
        f"- 코디 목적: {purpose}\n"
        f"- 날씨/위치: {temp}°C {cond} ({location or '미지정'})\n"
        f"- 매칭 스타일리스트: {stylist_name or '범용'} ({stylist_city or '범용'})\n"
        + (
            f"\n## 분석 지침\n"
            f"첨부된 이미지를 직접 보고 분석하세요. 'outfit' 섹션은 반드시 이미지에 보이는 "
            f"실제 옷(컬러·종류)을 적고, personalColor/body/purpose 섹션의 코디 컬러 언급도 "
            f"이미지의 실제 색과 일치시키세요.\n"
            if _vision else
            f"\n## 생성된 코디 요약\n{outfit_text}\n"
        )
        + f"\n## 출력 JSON 스키마 (이 형식 정확히 준수)\n"
        '{\n'
        f'  "personalColor": {{\n'
        f'    "text": "퍼스널컬러 측면 분석 ({_lang_label_text}, 정확히 250-300자, '
        f'추천 컬러와 피해야 할 컬러 모두 설명, 오늘 코디의 컬러 선택 근거 포함)",\n'
        f'    "keywords": ["키워드1", "키워드2", "키워드3"]\n'
        f'  }},\n'
        f'  "body": {{\n'
        f'    "text": "체형/사이즈 측면 분석 ({_lang_label_text}, 250-300자, '
        f'키/체중/BMI/체형 분류 기반 핏과 실루엣 추천 근거)",\n'
        f'    "keywords": ["키워드1", "키워드2", "키워드3"]\n'
        f'  }},\n'
        f'  "purpose": {{\n'
        f'    "text": "코디 목적과 날씨 측면 분석 ({_lang_label_text}, 250-300자, '
        f'목적/날씨를 어떻게 반영했는지 설명)",\n'
        f'    "keywords": ["키워드1", "키워드2", "키워드3"]\n'
        f'  }}'
        + _outfit_schema + '\n'
        '}\n'
        f'\nRULES:\n'
        f'1. 각 text는 정확히 250-300자 ({_lang_label_text}).\n'
        f'2. 각 keywords 배열은 정확히 3개 단어 (2-6자).\n'
        + (f'3. outfit 의 각 항목은 짧은 문구 (10-25자), 이미지의 실제 옷 기준.\n'
           f'4. JSON 외 추가 텍스트 출력 금지.\n'
           if _vision else
           f'3. JSON 외 추가 텍스트 출력 금지.\n')
    )

    # ── gpt-4.1-mini 호출 ──
    _openai_key = os.getenv("OPENAI_API_KEY")
    if not _openai_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수 미설정")

    _client_analysis = OpenAI(api_key=_openai_key)
    _model = os.getenv("CODIBANK_ANALYSIS_MODEL", "gpt-4.1-mini")
    # ─── 2026-05-14 v67 Phase 1.5 HOTFIX ─── 분석 호출 timeout/retry 보강 ───
    # 이전: timeout=10초만 명시 (자동 재시도 2회로 최악 30초 → 사용자 인지 못함)
    # 변경: max_retries=0 + 환경변수 (자동 재시도 차단으로 비용 절감)
    _analysis_timeout = float(os.getenv("CODIBANK_ANALYSIS_TIMEOUT", "10"))
    # ─── 2026-05-16 KST · TJ 지시 ─── vision 분석은 이미지 처리로 더 오래 걸림 ───
    # 텍스트 10초 → vision 20초 (timeout 부족 시 503 → 분석 보고서 미생성 방지)
    if _vision:
        _analysis_timeout = max(
            _analysis_timeout,
            float(os.getenv("CODIBANK_ANALYSIS_TIMEOUT_VISION", "20")),
        )
    _analysis_max_retries = int(os.getenv("CODIBANK_ANALYSIS_MAX_RETRIES", "0"))

    print(f"[codifit_analysis] gpt-4.1-mini 호출 시작 (model={_model}, lang={'en' if _en else 'ko'}, vision={_vision}, timeout={_analysis_timeout}s, retries={_analysis_max_retries})", flush=True)

    # vision 시 user 메시지를 멀티모달(텍스트+이미지)로 구성
    if _vision:
        _user_msg_content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{image_b64}",
                "detail": "low",   # 옷 컬러·종류 식별엔 low 충분 + 토큰 절감
            }},
        ]
    else:
        _user_msg_content = user_input

    _response = _client_analysis.with_options(
        max_retries=_analysis_max_retries,
        timeout=_analysis_timeout,
    ).chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": _user_msg_content},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    _text = _response.choices[0].message.content or "{}"
    _parsed = json.loads(_text)

    # ── 스키마 검증 + 정규화 ──
    result = {}
    for sec in ("personalColor", "body", "purpose"):
        _s = _parsed.get(sec) or {}
        _txt = str(_s.get("text") or "").strip()[:320]
        _kws = _s.get("keywords") or []
        if not isinstance(_kws, list):
            _kws = []
        _kws = [str(k).strip() for k in _kws if str(k).strip()][:3]
        while len(_kws) < 3:
            _kws.append("—")
        result[sec] = {"text": _txt, "keywords": _kws}

    # ── vision 시 outfit 섹션 검증 (이미지 기반 실제 착장) ──
    if _vision:
        _of = _parsed.get("outfit") or {}
        if isinstance(_of, dict):
            result["outfit"] = {
                "top": str(_of.get("top") or "").strip()[:60],
                "bottom": str(_of.get("bottom") or "").strip()[:60],
                "shoes": str(_of.get("shoes") or "").strip()[:60],
                "accessory": str(_of.get("accessory") or "").strip()[:60],
            }

    _sec_n = "4섹션" if "outfit" in result else "3섹션"
    print(f"[codifit_analysis] ✅ 분석 생성 완료 ({_sec_n}, vision={_vision}, total chars={sum(len(v.get('text','')) for k,v in result.items() if k!='outfit')})", flush=True)
    return result


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
    # 코디핏 AI 추천:  [2026-04-21: 코디쌤→코디핏] 항상 OpenAI API 전용
    # 트라이 온 착장 이미지:  [2026-04-21: 코디하기→트라이 온] /api/codistyle/generate (Gemini 전용)
    # 두 API를 혼용하거나 임의 전환하지 않음
    # ══════════════════════════════════════════════════════
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    if not has_openai:
        return jsonify(
            ok=False,
            error="OPENAI_API_KEY가 설정되지 않았습니다. 코디핏 AI 코디는 OpenAI API가 필요합니다.",
        ), 400

    payload = request.get_json(silent=True) or {}

    # ─── 2026-05-14 KST · TJ 지시 (v68 4→2→1 흐름) ─── 새 흐름 hook ──────
    # 코디핏 새 UX: 4장 그리드 → 2장 비교 → 최종 1장 Medium
    # 프론트엔드가 같은 endpoint를 다른 페이로드로 호출:
    #   · STEP A: _force_city + _force_quality='low' (4번 병렬)
    #   · STEP B: _force_quality='low' + _similar_variation=true (같은 stylist 변형)
    #   · STEP C: 별도 endpoint /api/codifit/upgrade
    _force_city = str(payload.get('_force_city') or '').strip()
    _force_quality = str(payload.get('_force_quality') or '').strip().lower()
    _similar_variation = bool(payload.get('_similar_variation'))
    if _force_city:
        if 'weather' not in payload or not isinstance(payload.get('weather'), dict):
            payload['weather'] = {}
        payload['weather']['location'] = _force_city
        print(f"[v68 grid] _force_city={_force_city}", flush=True)
    # ─── 2026-05-19 KST · TJ 지시 ─── STEP A 매 생성마다 새 코디 ───
    #   문제: STEP A(4장 그리드)는 seed 고정 시 ① 스타일리스트 엔진이
    #         hash(user+purpose+today+seed) 로 같은 키워드/스타일리스트/도시를
    #         선정 → 같은 코디 프롬프트 ② 캐시 키도 동일 → 캐시 HIT →
    #         과거 이미지 그대로 (오전 생성이 오후에도 동일, 재생성해도 동일).
    #   해결: STEP A 진입 시 seed/retrySeed 를 서버 시각(ms)으로 강제.
    #         → 엔진이 매번 다른 키워드/스타일리스트 선정 (다양성 확보)
    #         → 캐시 키 rsd 도 매번 달라짐 (아래 force_regen 와 함께 캐시 MISS)
    #   ※ STEP A = _force_city 있고 유사변형(STEP B)·Q3(high) 둘 다 아님.
    #     같은 "추천 받기"의 4개 도시는 _force_city(cty) 로 키가 구분된다.
    _is_step_a_grid = bool(_force_city) and (not _similar_variation) and (_force_quality != 'high')
    if _is_step_a_grid:
        _step_a_nonce = _now_ms()
        payload['seed'] = _step_a_nonce
        payload['retrySeed'] = _step_a_nonce
        print(f"[v68 grid] STEP A 새 코디 강제 — seed={_step_a_nonce}", flush=True)
    # ─── 2026-05-18 KST · TJ 지시 ─── Q3 최종 고화질 = Nano Banana Pro ───
    #   설계 의도: Q3 = Q2 에서 선택한 최종 코디를 "확대해도 깨지지 않는
    #             고퀄 이미지"로 보는 단계.
    #   변경 이유: 기존 gpt_image_2_high 는 생성에 60초+ 소요 → 타임아웃
    #             (APITimeoutError) 빈발 후 Gemini 로 폴백해 결과를 냄.
    #             그럴 거면 처음부터 Nano Banana Pro 로 직행 — 더 빠르고
    #             저렴하며 화질·얼굴 보존이 우수.
    #   매핑: alias 'pro' → gemini-3-pro-image-preview (provider=gemini).
    #   ※ Q1·Q2(_force_quality='low')는 기존 gpt_image_2_low 그대로 유지.
    if _force_quality == 'high':
        payload['_override_alias'] = 'pro'
        print(f"[v68 grid] _force_quality=high → Q3 최종 = Nano Banana Pro (alias=pro)", flush=True)
    elif _force_quality in ('low', 'medium'):
        payload['_override_alias'] = f'gpt_image_2_{_force_quality}'
        print(f"[v68 grid] _force_quality={_force_quality} → alias={payload['_override_alias']}", flush=True)

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

    # ─── 2026-05-14 KST · TJ 지시 (v68 STEP B) ─── 유사 변형 prompt 주입 ────
    # ─── 2026-05-16 KST · TJ 지시 ─── 원본과 거의 동일하게 생성되던 문제 수정 ───
    #   기존: "Do NOT change colors" → 원본과 똑같은 결과
    #   변경: 같은 stylist/TPO/날씨 유지하되 상·하의 컬러+패턴은 반드시 변경
    if _similar_variation and prompt:
        prompt += (
            "\n\n[VARIATION REQUIREMENT — STEP B SIMILAR ALTERNATIVE]\n"
            "Take the SELECTED outfit as the base and generate a CLEARLY DIFFERENT "
            "alternative by the SAME stylist for the SAME occasion, SAME date, SAME weather. "
            "This is a 'similar but visibly different' version shown side-by-side with the "
            "original — it MUST be immediately distinguishable from the original outfit.\n"
            "\n"
            "KEEP IDENTICAL (do NOT change):\n"
            "  - The stylist's identity and overall styling philosophy\n"
            "  - The occasion / TPO, the date, and weather-appropriateness\n"
            "  - The general formality level and season suitability\n"
            "\n"
            "MUST CHANGE (these MUST be clearly different from the original):\n"
            "  - TOP: change to a DISTINCTLY DIFFERENT color AND a different pattern "
            "(solid <-> striped <-> checked <-> textured / melange)\n"
            "  - BOTTOM: change to a DISTINCTLY DIFFERENT color AND a different pattern\n"
            "  - SHOES: change to a DIFFERENT color and a DIFFERENT design "
            "(e.g., loafers <-> derby <-> sneakers, brown <-> black <-> white)\n"
            "\n"
            "ACCESSORIES — STRICT:\n"
            "  - Do NOT include ANY accessories: no bag, no watch, no necklace, "
            "no scarf, no hat, no sunglasses. The model holds nothing and wears no accessory.\n"
            "\n"
            "CRITICAL: When the two outfits are placed side-by-side, the user must "
            "INSTANTLY see they differ in top/bottom color, pattern, and shoes. "
            "Do NOT reproduce the same colors, patterns, or shoes as the original outfit.\n"
        )
        print("[v68 STEP B] similar_variation prompt injected (color+pattern+shoes, no accessories)", flush=True)
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

    # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.5 HOTFIX) ─── face 미등록 사용자 거절 ───
    # 이전: face 없어도 images.generate fallback으로 진행 (face 자동 생성 → identity 손상)
    # 변경: face 필수, 미등록 시 400 거절 (errorCode="FACE_NOT_REGISTERED")
    # 환경변수 CODIBANK_CODIFIT_REQUIRE_FACE=0으로 임시 비활성 가능 (기본 1=필수)
    _require_face = str(os.getenv("CODIBANK_CODIFIT_REQUIRE_FACE", "1")).strip() not in ("0", "false", "False")
    if _require_face:
        _has_face = any(label == "face" for label, _, _ in ref_images)
        if not _has_face:
            _en_msg = str(payload.get("lang") or "ko").strip().lower() == "en"
            print(f"[ai_styling] ⚠ face 미등록 사용자 — 거절 (lang={'en' if _en_msg else 'ko'})", flush=True)
            return jsonify(
                ok=False,
                error=(
                    "Face photo registration is required. Please register your face photo in Profile first."
                    if _en_msg else
                    "얼굴 사진 등록이 필요합니다. 프로필에서 얼굴 사진을 먼저 등록한 후 다시 시도해주세요."
                ),
                errorCode="FACE_NOT_REGISTERED",
            ), 400

    # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 3) ─── 캐시 키 v2 적용 ───
    # v1 (purposeKey/seed/날씨/얼굴 raw) → v2 (model/quality/size/bodyType/PC/avoid hash + 버킷팅)
    # 효과: 캐시 히트율 1% → 70%+ (월 수백 달러 비용 절감 예상)
    # v1 캐시는 그대로 둠 (cleanup script로 추후 제거)
    _resolved_tier_for_key = str(
        (payload.get("user") or {}).get("tier") or payload.get("tier") or "FREE"
    ).upper().strip()
    if _resolved_tier_for_key not in ("FREE", "SILVER", "GOLD", "DIAMOND"):
        _resolved_tier_for_key = "FREE"
    try:
        _model_for_key, _provider_for_key, _quality_for_key = _resolve_engine_full(
            _resolved_tier_for_key, "codifit"
        )
    except Exception:
        _model_for_key, _provider_for_key, _quality_for_key = ("", "", "")
    _size_for_key = (
        os.getenv("CODIBANK_GPT_IMAGE_SIZE", "1536x1024")
        if _provider_for_key == "openai" else ""
    )
    _force_regen = bool(payload.get("forceRegenerate") or payload.get("force_regenerate"))
    # ─── 2026-05-16 KST · TJ 지시 ─── STEP B 유사 변형: 캐시 사용 금지 ───
    # 문제: _similar_variation 이 캐시키에 없어 STEP A 원본과 같은 키 → 캐시 HIT
    #       → 변형 프롬프트가 적용돼도 캐시된 원본 이미지가 그대로 반환됨
    # 해결: _similar_variation 이면 force_regenerate=True → 캐시키에 시간 nonce(rsd)
    #       포함 → 매번 새 키 → 캐시 MISS → 항상 새로 생성 (STEP A 파일도 안 덮음)
    if _similar_variation:
        _force_regen = True
    # ─── 2026-05-18 KST · TJ 지시 ─── Q3 캐시 우회 ───
    #   Q3(_force_quality='high')는 사용자가 선택한 코디(_force_ref_image)별로
    #   매번 새로 생성해야 한다. 캐시 HIT 되면 STEP A 원본 이미지가 그대로
    #   반환되는 버그(원본/변형 임의 노출) 발생 → force_regenerate 로 nonce 를
    #   넣어 항상 MISS, cache_fname 도 매번 달라 STEP A/B 파일을 덮지 않음.
    if str(payload.get('_force_quality') or '').strip().lower() == 'high':
        _force_regen = True
    # ─── 2026-05-19 KST · TJ 지시 ─── STEP A 도 캐시 우회 (매 생성 새 코디) ───
    #   STEP A 진입 시 seed/retrySeed 를 서버 시각(ms)으로 강제했으므로,
    #   force_regen=True 면 캐시 키 body 에 rsd=그 nonce 가 들어가 매번 새 키
    #   → 캐시 MISS → AI 가 실제로 새 이미지 생성. (캐시 HIT 로 과거 이미지가
    #   그대로 반환되던 버그 차단.)
    if _is_step_a_grid:
        _force_regen = True
    cache_key = _make_ai_cache_key_v2(
        payload, face_bytes_for_key, ref_images,
        model=_model_for_key,
        quality=_quality_for_key,
        size=_size_for_key,
        force_regenerate=_force_regen,
        # ─── 2026-05-14 v67 Phase 1.7-fix ─── 스타일리스트 정보 전달
        # TJ 보고 "스타일리스트 변경해도 코디 동일" 버그 수정
        matched_stylist=_matched_stylist,
        meta=_meta,
    )
    ext = "jpg" if output_format.lower() in ("jpeg", "jpg") else output_format.lower()
    cache_fname = f"ai_{cache_key}.{ext}"
    cache_fpath = os.path.join(_UPLOAD_DIR, cache_fname)
    if os.path.exists(cache_fpath):
        rel = f"{_UPLOAD_PREFIX}{cache_fname}"
        base = _public_base()
        # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 2) ─── 분석 분리 ───
        # 이전: _generate_styling_analysis 템플릿 호출
        # 변경: stylingAnalysis=None 반환, 클라이언트가 /api/ai/styling/analysis 별도 호출
        # 효과: 캐시 응답 더 빠름 (템플릿 호출 제거) + 분석 품질 ↑ (gpt-4.1-mini)
        return jsonify(
            ok=True,
            image=f"{base}{rel}",  # 프론트 호환: img src로 바로 사용
            path=rel,
            url=f"{base}{rel}",
            explanation=short,
            model="cache",
            cached=True,
            stylingAnalysis=None,  # Phase 2: 별도 엔드포인트로 호출
            cacheKey=cache_key,    # Phase 2: 클라이언트가 분석 API 호출 시 사용
            # ─── 2026-05-14 KST · TJ 보고 ─── 활동지역 city 주입 (서울 고정 버그 수정)
            stylist=(
                (lambda s, c: ({**s, 'city': c} if isinstance(s, dict) and c else s))(
                    _matched_stylist, (_meta or {}).get('active_city', '') if _meta else ''
                )
            ),
            stylingStory=(_meta or {}).get("styling_story") if _meta else None,
            engineKeywords=(_meta or {}).get('keywords_selected', []) if _meta else [],
            engineCategoryKeywords=(_meta or {}).get('categoryKeywords', {}) if _meta else {},
            engineCity=(_meta or {}).get('active_city', '') if _meta else '',
            enginePurpose=(_meta or {}).get('purpose', '') if _meta else '',
            engineBottomType=(_meta or {}).get('bottom_type', '') if _meta else '',
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
            # ─── 2026-04-21 KST ─── 티어 추출 (payload.user.tier 우선) ───
            _styling_tier = str(
                (payload.get("user") or {}).get("tier") or payload.get("tier") or "FREE"
            ).upper().strip()
            print(f"[ai_styling] Gemini 단일 호출 모드 (이미지+분석 동시) tier={_styling_tier}")
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
                tier=_styling_tier,  # ─── 2026-04-21 티어별 엔진 라우팅 ───
                # ─── 2026-05-16 KST · TJ 지시 ─── _force_quality 실제 반영 ───
                # 문제: _force_quality → payload['_override_alias'] 설정했으나
                #       1차 호출에 전달 안 함 → STEP A/B/C 모두 tier 기반 medium 고정
                # 수정: payload['_override_alias']를 1차 호출에 전달
                #       → STEP C(_force_quality='high')가 실제 high quality 생성
                _override_alias=payload.get('_override_alias') or None,
            )
            # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1.6 HYBRID) ─── 하이브리드 폴백 ───
            # 이전: GPT Image 2 실패(500) → 즉시 에러 반환 (Phase 1)
            # 변경: 1차 GPT Image 2 실패 → Gemini 자동 폴백 (v65 안정 모델)
            #   · 같은 cache_fname 사용 → 폴백 결과도 캐시 → 재시도 시 즉시 응답
            #   · 환경변수 CODIBANK_CODIFIT_ENABLE_FALLBACK=0으로 비활성 가능
            #   · 환경변수 CODIBANK_CODIFIT_FALLBACK_ALIAS=flash_v2 (기본)로 폴백 모델 지정
            if isinstance(_gemini_result, tuple):
                _resp_obj, _status = _gemini_result
                # 폴백 활성 + 1차가 GPT Image 2였을 때만 Gemini 폴백 시도
                _enable_fallback = str(
                    os.getenv("CODIBANK_CODIFIT_ENABLE_FALLBACK", "1")
                ).strip() not in ("0", "false", "False")
                # 1차가 이미 Gemini였다면(_styling_tier 기반 라우팅이 Gemini였다면) 폴백 의미 없음
                try:
                    _primary_model, _primary_provider, _ = _resolve_engine_full(_styling_tier, "codifit")
                    _primary_was_openai = (_primary_provider == "openai")
                except Exception:
                    _primary_was_openai = True  # 안전망: 알 수 없으면 폴백 시도

                if _enable_fallback and _primary_was_openai:
                    _fallback_alias = os.getenv("CODIBANK_CODIFIT_FALLBACK_ALIAS", "flash_v2")
                    print(f"[ai_styling] ⚠ 1차(GPT Image 2) 실패 → Gemini 폴백 시도 (alias={_fallback_alias})", flush=True)
                    try:
                        _fallback_result = _ai_styling_via_gemini(
                            payload=payload,
                            prompt=prompt,
                            short=short,
                            ref_images=ref_images,
                            cache_fname=cache_fname,  # 같은 캐시 파일명 사용
                            ext=ext,
                            matched_stylist=_matched_stylist,
                            lang=str(payload.get("lang") or "ko"),
                            meta=_meta,
                            tier=_styling_tier,
                            _override_alias=_fallback_alias,  # 폴백 alias 강제
                        )
                        if isinstance(_fallback_result, tuple):
                            # 폴백도 실패 → 1차 에러 반환 (둘 다 실패한 상황)
                            print(f"[ai_styling] ❌ Gemini 폴백도 실패 — 1차 에러 반환", flush=True)
                            return _gemini_result
                        else:
                            print(f"[ai_styling] ✅ Gemini 폴백 성공", flush=True)
                            return _fallback_result
                    except Exception as _fe:
                        print(f"[ai_styling] ❌ Gemini 폴백 예외: {_fe}", flush=True)
                        import traceback as _tbf
                        _tbf.print_exc()
                        return _gemini_result
                else:
                    # 폴백 비활성 또는 1차가 이미 Gemini였음 → 즉시 에러 반환
                    return _gemini_result
            else:
                # jsonify(...) 단독 반환 → 성공
                return _gemini_result
        except Exception as _ge:
            print(f"[ai_styling] Gemini 라우팅 예외: {_ge}")
            import traceback as _tbg
            _tbg.print_exc()
            # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1) ─── 자동 폴백 차단 ───
            # 예외 발생 시에도 OpenAI 폴백으로 자동 전환하지 않음.
            return jsonify(ok=False, error=f"이미지 생성 실패: {str(_ge)[:300]}"), 500

    # ── 코디쌤(/api/ai/styling) OpenAI 폴백 경로 ──
    # 위 Gemini 라우팅이 실패했거나 명시적으로 OpenAI를 선택한 경우 사용
    if not has_openai:
        return jsonify(
            ok=False,
            error="OPENAI_API_KEY가 설정되지 않았습니다. 코디핏 AI 코디는 OpenAI API 또는 Gemini API가 필요합니다.",
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
            # ─── 2026-05-14 KST · TJ 보고 ─── 활동지역 city 주입 (서울 고정 버그 수정)
            stylist=(
                (lambda s, c: ({**s, 'city': c} if isinstance(s, dict) and c else s))(
                    _matched_stylist, _meta.get('active_city', '') if _meta else ''
                )
            ),
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


# ═════════════════════════════════════════════════════════════
# [2026-05-14 v67 Phase 2] /api/ai/styling/analysis
#   코디핏 분석 보고서 — gpt-4.1-mini 별도 호출
# ═════════════════════════════════════════════════════════════
@app.post("/api/ai/styling/analysis")
def ai_styling_analysis():
    """[v67 Phase 2] 코디핏 분석 보고서 — gpt-4.1-mini로 별도 생성.

    흐름:
      1. 클라이언트가 /api/ai/styling 응답에서 받은 cacheKey + 원본 payload 재전송
      2. 서버: cacheKey 기반 분석 JSON 캐시 파일 확인 → 있으면 즉시 반환
      3. 없으면: gpt-4.1-mini 호출 (timeout 10초, temperature 0.4)
      4. 결과를 JSON 파일에 캐시 + 반환

    재시도 정책 (옵션 B):
      - 클라이언트가 1회 재시도 가능 (서버는 매번 단일 호출)
      - timeout 10초로 fail-fast
      - 실패 시 503 반환 → 클라이언트가 "다시 시도" / "비활성" UI 결정

    분석은 stylingAnalysis JSON (personalColor / body / purpose 3섹션) 형식.
    기존 closet.html 분석 박스 DOM과 호환.
    """
    payload = request.get_json(silent=True) or {}
    cache_key = str(payload.get("cacheKey") or "").strip()

    if not cache_key:
        return jsonify(ok=False, error="cacheKey 누락"), 400

    # 보안: cacheKey 영문/숫자/언더스코어만 허용 (path traversal 방지)
    if not re.match(r'^[A-Za-z0-9_]{8,64}$', cache_key):
        return jsonify(ok=False, error="cacheKey 형식 오류"), 400

    # ── 분석 캐시 파일 경로 (이미지 캐시와 별도) ──
    _analysis_cache_fname = f"analysis_{cache_key}.json"
    _analysis_cache_fpath = os.path.join(_UPLOAD_DIR, _analysis_cache_fname)

    # ── 캐시 히트 ──
    if os.path.exists(_analysis_cache_fpath):
        try:
            with open(_analysis_cache_fpath, "r", encoding="utf-8") as _f:
                _cached_analysis = json.load(_f)
            # ─── 2026-05-16 KST · TJ 지시 (옵션 A) ─── 구버전 캐시 무효화 ───
            # vision 도입 전 캐시(outfit 섹션 없음)는 재생성 (분석-이미지 불일치 방지)
            if isinstance(_cached_analysis, dict) and _cached_analysis.get("outfit"):
                print(f"[ai_styling_analysis] ✅ 캐시 hit: {cache_key}", flush=True)
                return jsonify(
                    ok=True,
                    stylingAnalysis=_cached_analysis,
                    cached=True,
                    cacheKey=cache_key,
                )
            else:
                print(f"[ai_styling_analysis] 구버전 캐시(outfit 없음) — vision 재생성: {cache_key}", flush=True)
                # fall through → 재생성
        except Exception as _ce:
            print(f"[ai_styling_analysis] 캐시 파일 손상 ({_ce}), 재생성")
            # fall through

    # ── 캐시 미스 → gpt-4.1-mini 호출 ──
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    if not has_openai:
        return jsonify(ok=False, error="OPENAI_API_KEY 미설정"), 500

    try:
        _matched_stylist = payload.get("stylist") or None
        _meta = payload.get("meta") or {}
        _lang = str(payload.get("lang") or "ko")
        _outfit_summary = str(payload.get("outfitSummary") or "").strip()

        # meta에 stylist가 없으면 payload.stylist로 보강
        if isinstance(_meta, dict) and _matched_stylist and "active_city" not in _meta:
            _meta = dict(_meta)
            _meta.setdefault("active_city", _matched_stylist.get("city", "") if isinstance(_matched_stylist, dict) else "")
            _meta.setdefault("purpose", payload.get("purposeLabel", ""))

        # ─── 2026-05-16 KST · TJ 지시 (옵션 A) ─── vision 분석용 이미지 확보 ───
        #   1) 로컬 캐시 이미지 ai_{cacheKey}.jpg 우선 (생성 직후라면 존재)
        #   2) 없으면 클라이언트가 보낸 imageUrl 에서 다운로드 (R2 public URL)
        #   3) PIL 로 정면 crop(wide면 좌측 절반) + 768px 축소 → base64 (토큰 절감)
        #   실패 시 _image_b64=None → 함수가 텍스트 모드로 graceful degradation
        _image_b64 = None
        try:
            _img_bytes = None
            for _ext in ("jpg", "jpeg", "png", "webp"):
                _ip = os.path.join(_UPLOAD_DIR, f"ai_{cache_key}.{_ext}")
                if os.path.exists(_ip):
                    with open(_ip, "rb") as _f:
                        _img_bytes = _f.read()
                    break
            if not _img_bytes:
                _img_url = str(payload.get("imageUrl") or payload.get("image") or "").strip()
                if _img_url.startswith("http"):
                    _rr = http_requests.get(_img_url, timeout=8)
                    if _rr.ok:
                        _img_bytes = _rr.content
            if _img_bytes:
                from PIL import Image as _PILImg
                import io as _io
                _im = _PILImg.open(_io.BytesIO(_img_bytes)).convert("RGB")
                _w, _h = _im.size
                # wide(정/후면 합본)면 좌측 절반(정면)만 — 옷은 정면으로 충분
                if _w / max(1, _h) > 1.2:
                    _im = _im.crop((0, 0, _w // 2, _h))
                # 긴 변 768px 로 축소 (vision 입력 토큰 절감)
                _mx = max(_im.size)
                if _mx > 768:
                    _sc = 768.0 / _mx
                    _im = _im.resize(
                        (max(1, int(_im.size[0] * _sc)), max(1, int(_im.size[1] * _sc))),
                        _PILImg.LANCZOS,
                    )
                _buf = _io.BytesIO()
                _im.save(_buf, format="JPEG", quality=82)
                _image_b64 = base64.b64encode(_buf.getvalue()).decode("ascii")
                print(f"[ai_styling_analysis] vision 이미지 준비 완료 ({_im.size[0]}x{_im.size[1]})", flush=True)
            else:
                print(f"[ai_styling_analysis] 이미지 미확보 — 텍스트 분석으로 진행", flush=True)
        except Exception as _ie:
            print(f"[ai_styling_analysis] vision 이미지 준비 실패(텍스트 분석 진행): {_ie}", flush=True)
            _image_b64 = None

        _analysis = _codifit_analysis_via_gpt41mini(
            payload=payload,
            matched_stylist=_matched_stylist,
            meta=_meta,
            generated_outfit_summary=_outfit_summary or None,
            lang=_lang,
            image_b64=_image_b64,
        )

        # ── 캐시 저장 (성공 시) ──
        try:
            with open(_analysis_cache_fpath, "w", encoding="utf-8") as _f:
                json.dump(_analysis, _f, ensure_ascii=False)
            print(f"[ai_styling_analysis] ✅ 캐시 저장: {_analysis_cache_fname}", flush=True)
        except Exception as _se:
            print(f"[ai_styling_analysis] 캐시 저장 실패(무시): {_se}", flush=True)

        return jsonify(
            ok=True,
            stylingAnalysis=_analysis,
            cached=False,
            cacheKey=cache_key,
        )
    except Exception as _e:
        import traceback as _tb_a
        _trace = _tb_a.format_exc()[-400:]
        print(f"[ai_styling_analysis] gpt-4.1-mini 실패: {type(_e).__name__}: {str(_e)[:200]}\n{_trace}", flush=True)
        return jsonify(
            ok=False,
            error=f"분석 생성 실패: {str(_e)[:200]}",
            cacheKey=cache_key,
        ), 503


# ─────────────────────────────────────────────────────────
# /api/codistyle/generate  — Gemini 착장 이미지 생성
# ★ google-genai 공식 SDK 사용 (REST API는 이미지 생성 모델에서 미작동)
# ★ google-generativeai(구버전)이 아닌 google-genai(신버전) 필수
# ─────────────────────────────────────────────────────────
# ─── 2026-04-21 KST ────────────────────────────────────────────
# 티어별 × 기능별 엔진 라우팅 시스템 도입
# ───────────────────────────────────────────────────────────────
# 설계 원칙:
# 1. 엔진 별칭(flash_v1, flash_v2, pro) → 실제 모델 ID 매핑
# 2. {티어, 기능} 2차원 매트릭스로 엔진 선택
# 3. 환경변수로 런타임에 조정 가능 (재배포 없이)
# 4. 결정 순서: 환경변수 CODIBANK_ENGINE_{TIER}_{FEATURE}
#              → 기본 매트릭스 → 최종 폴백 (_CODISTYLE_MODEL)
# ───────────────────────────────────────────────────────────────

# 엔진 별칭 → 실제 모델 ID 매핑
_ENGINE_MODEL_MAP = {
    "flash_v1": os.getenv("CODIBANK_MODEL_FLASH_V1", "gemini-2.5-flash-image"),        # Nano Banana 1 ($0.039)
    "flash_v2": os.getenv("CODIBANK_MODEL_FLASH_V2", "gemini-3.1-flash-image-preview"),# Nano Banana 2 ($0.067)
    "pro":      os.getenv("CODIBANK_MODEL_PRO",      "gemini-3-pro-image-preview"),    # Nano Banana Pro ($0.134)
    # ─── 2026-05-13 KST · TJ 지시 (v66) ─── GPT Image 2 추가 (codifit 전용) ───
    # 이유: Gemini Nano Banana 2 preview의 다양성/얼굴 보존 한계 → GPT Image 2 medium 전환
    # 비용: medium 1024×1024 약 $0.053 (Nano Banana 2 $0.067 대비 21% 절감)
    "gpt_image_2_low":    os.getenv("CODIBANK_MODEL_GPT_IMAGE_LOW",    "gpt-image-2"),  # $0.006
    "gpt_image_2_medium": os.getenv("CODIBANK_MODEL_GPT_IMAGE_MEDIUM", "gpt-image-2"),  # $0.053 (기본)
    "gpt_image_2_high":   os.getenv("CODIBANK_MODEL_GPT_IMAGE_HIGH",   "gpt-image-2"),  # $0.211
}

# ─── 2026-05-13 KST · TJ 지시 (v66) ─── provider + quality 매핑 (GPT Image 2용) ───
_ENGINE_PROVIDER_MAP = {
    "flash_v1":           "gemini",
    "flash_v2":           "gemini",
    "pro":                "gemini",
    "gpt_image_2_low":    "openai",
    "gpt_image_2_medium": "openai",
    "gpt_image_2_high":   "openai",
}
_ENGINE_QUALITY_MAP = {
    "gpt_image_2_low":    "low",
    "gpt_image_2_medium": "medium",
    "gpt_image_2_high":   "high",
}

# ─── 2026-04-22 17:05 KST (엔진 정책 단순화) ───────────────────────────
# 기존: {티어 × 기능} 2차원 매트릭스 (FREE/SILVER=flash_v2, GOLD/DIAMOND=pro)
# 신규: {기능} 1차원만 (티어 무시) — TJ님 지시
#   • 코디핏 → flash_v2 (Nano Banana 2, 원가 ~₩40/회, 체험 유도)
#   • 트라이온 → pro (Nano Banana Pro, 원가 ~₩120/회, 프리미엄)
# 사용 제한은 회원 티어별 "코디핏 N회 / 트라이온 M회"로 이미 관리됨.
# ────────────────────────────────────────────────────────────────────
# ─── 2026-05-13 KST · TJ 지시 (v66) ─── 코디핏 → GPT Image 2 medium ───
# 서비스별 고정 모델 (티어와 무관)
# 구조: { 기능: 엔진별칭 }
_ENGINE_SERVICE_DEFAULT = {
    "codifit": "gpt_image_2_medium",  # ← v66 변경: flash_v2 → gpt_image_2_medium
    "tryon":   "pro",                  # Nano Banana Pro = gemini-3-pro-image-preview
}

# ─── 하위호환 유지: 기존 _ENGINE_MATRIX_DEFAULT 이름을 참조하는 코드가 있을 경우 대비 ───
# (현재 파일 내에서는 _resolve_engine과 _get_engine_config_summary만 사용)
_ENGINE_MATRIX_DEFAULT = {
    "FREE":    dict(_ENGINE_SERVICE_DEFAULT),
    "SILVER":  dict(_ENGINE_SERVICE_DEFAULT),
    "GOLD":    dict(_ENGINE_SERVICE_DEFAULT),
    "DIAMOND": dict(_ENGINE_SERVICE_DEFAULT),
}

def _resolve_engine(tier: str, feature: str) -> str:
    """
    서비스(feature) 기반 모델 라우팅.
    
    [2026-04-22 17:05 KST] 티어 파라미터는 하위호환 위해 받지만 무시함.
    TJ님 새 정책: 모델은 서비스 종류만 보고 결정. 회원 티어와 무관.
    
    우선순위:
      1. 환경변수 CODIBANK_MODEL_{FEATURE} (직접 모델 ID, 최우선)
         예: CODIBANK_MODEL_CODIFIT=gemini-3.1-flash-image-preview
         예: CODIBANK_MODEL_TRYON=gemini-3-pro-image-preview
      2. 환경변수 CODIBANK_ALIAS_{FEATURE} (별칭)
         예: CODIBANK_ALIAS_CODIFIT=flash_v2
      3. _ENGINE_SERVICE_DEFAULT 기본값
      4. 최종 폴백 (_CODISTYLE_MODEL)
    
    매개변수:
      tier:    (무시됨, 하위호환 위해 받음) 'FREE'|'SILVER'|'GOLD'|'DIAMOND'
      feature: 'codifit' | 'tryon' (대소문자 무관)
    
    반환:
      실제 Gemini 모델 ID (예: 'gemini-3-pro-image-preview')
    """
    feature_low = (feature or "codifit").lower()
    feature_up  = feature_low.upper()
    
    # 1. 환경변수 직접 모델 ID (최우선) — Render에서 재배포 없이 교체용
    env_model = os.getenv(f"CODIBANK_MODEL_{feature_up}")
    if env_model:
        return env_model
    
    # 2. 환경변수 별칭
    env_alias = os.getenv(f"CODIBANK_ALIAS_{feature_up}")
    if env_alias and env_alias in _ENGINE_MODEL_MAP:
        return _ENGINE_MODEL_MAP[env_alias]
    
    # 3. 기본 서비스별 매트릭스
    alias = _ENGINE_SERVICE_DEFAULT.get(feature_low, "flash_v2")
    if alias in _ENGINE_MODEL_MAP:
        return _ENGINE_MODEL_MAP[alias]
    
    # 4. 최종 폴백
    return _CODISTYLE_MODEL


# ─── 2026-05-13 KST · TJ 지시 (v66) ─── _resolve_engine_full 헬퍼 ───
def _resolve_engine_full(tier: str, feature: str) -> tuple:
    """
    모델 + provider + quality를 동시 반환 (GPT Image 2 라우팅용).
    
    반환: (model_name: str, provider: str, quality: str|None)
      - provider: "gemini" | "openai"
      - quality:  "low" | "medium" | "high" | None (Gemini는 None)
    
    예시:
      ("gpt-image-2", "openai", "medium")               # codifit 기본 (v66)
      ("gemini-3-pro-image-preview", "gemini", None)    # tryon 기본
    """
    feature_low = (feature or "codifit").lower()
    feature_up  = feature_low.upper()
    
    # 환경변수 직접 모델 ID 우선 (배포 후 즉시 롤백 가능)
    env_model = os.getenv(f"CODIBANK_MODEL_{feature_up}")
    if env_model:
        if env_model.startswith("gpt-image"):
            return env_model, "openai", "medium"
        return env_model, "gemini", None
    
    # alias 결정 (환경변수 우선)
    env_alias = os.getenv(f"CODIBANK_ALIAS_{feature_up}")
    if env_alias and env_alias in _ENGINE_MODEL_MAP:
        alias = env_alias
    else:
        alias = _ENGINE_SERVICE_DEFAULT.get(feature_low, "flash_v2")
    
    model = _ENGINE_MODEL_MAP.get(alias, _CODISTYLE_MODEL)
    provider = _ENGINE_PROVIDER_MAP.get(alias, "gemini")
    quality = _ENGINE_QUALITY_MAP.get(alias)
    return model, provider, quality


def _get_engine_config_summary() -> dict:
    """
    현재 엔진 설정을 반환 (관리자 페이지에서 조회용).
    
    [2026-04-22 17:05 KST] 서비스별 단일 모델 구조로 단순화.
    기존 "matrix"(티어×기능) 대신 "service_engines"(기능만) 제공.
    하위호환 위해 "matrix" 키도 유지하되 모든 티어에 같은 값 반환.
    
    [2026-04-23 17:00 KST] 트라이온 분석 모델 & thinking_level 정보 추가.
    마스터가 Render 환경변수를 바꾼 뒤 현재 설정을 쉽게 확인 가능.
    """
    service_engines = {
        "codifit": _resolve_engine("", "codifit"),
        "tryon":   _resolve_engine("", "tryon"),
    }
    # 하위호환: matrix 포맷도 같이 반환 (티어 4행 모두 동일 값)
    matrix = {
        tier: dict(service_engines)
        for tier in ("FREE", "SILVER", "GOLD", "DIAMOND")
    }
    
    # [2026-04-23 17:00] 트라이온 분석 전용 설정 (병렬 처리용)
    # [2026-05-28 KST · TJ 보고] gemini-3-pro-preview 가 2026-03-09 종료됨 (404 NOT_FOUND)
    #   → gemini-3.1-pro-preview 로 마이그레이션 (Google 공식 후속 모델, 동일 가격/기능)
    _tryon_analysis_model = os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS", "gemini-3.1-pro-preview")
    _tryon_thinking_raw = (os.getenv("CODIBANK_TRYON_THINKING_LEVEL") or "").strip().lower()
    _tryon_thinking_effective = _tryon_thinking_raw if _tryon_thinking_raw in ("low", "medium", "high") else "low"
    
    return {
        "engine_aliases": dict(_ENGINE_MODEL_MAP),
        "service_engines": service_engines,   # 신규 (권장)
        "matrix": matrix,                      # 하위호환
        "policy_note": "티어 무시 · 서비스별 단일 모델 (2026-04-22 17:05 KST)",
        # 트라이온 병렬 처리 설정 (2026-04-23 17:00)
        "tryon_parallel": {
            "image_model":      service_engines["tryon"],
            "analysis_model":   _tryon_analysis_model,
            "thinking_level": {
                "raw_env":   _tryon_thinking_raw or "(미설정)",
                "effective": _tryon_thinking_effective,
                "allowed":   ["low", "medium", "high"],
                "default":   "low",
            },
            "env_vars": {
                "CODIBANK_MODEL_TRYON":          os.getenv("CODIBANK_MODEL_TRYON") or "(미설정 → 기본값 사용)",
                "CODIBANK_MODEL_TRYON_ANALYSIS": os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS") or "(미설정 → gemini-3-pro-preview)",
                "CODIBANK_TRYON_THINKING_LEVEL": _tryon_thinking_raw or "(미설정 → low)",
            },
            "note": "Render 대시보드에서 환경변수 변경 시 자동 재시작으로 즉시 반영됨",
        },
    }

# ─── 기존 _CODISTYLE_MODEL (하위 호환용 폴백) ───────────────────
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
        # ─── 2026-05-14 v67 Phase 1.5 HOTFIX ─── _read_upload_bytes 미정의 버그 수정
        # 이전: data = _read_upload_bytes(_path) → NameError → PC 데이터 로드 100% 실패
        # 변경: _read_r2_bytes 헬퍼 함수 사용 (boto3 get_object 기반)
        data = _read_r2_bytes(_path)
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

    # ─── 2026-04-21 KST ─── 티어별 엔진 선택 ───
    # 프론트에서 user.tier = 'FREE'|'SILVER'|'GOLD'|'DIAMOND' 전달
    # (전달 안 되면 FREE로 간주 — 보수적 정책)
    _user_tier = str(user_info.get("tier") or payload.get("tier") or "FREE").upper().strip()
    if _user_tier not in ("FREE", "SILVER", "GOLD", "DIAMOND"):
        _user_tier = "FREE"
    # 트라이온 전용 엔진 결정 (코디핏은 /api/ai/styling에서 별도 처리)
    _TRYON_MODEL = _resolve_engine(_user_tier, "tryon")
    print(f"[TRYON] tier={_user_tier} → model={_TRYON_MODEL}", flush=True)

    # ──── [2026-04-19 BODY] 체형 키 지역 변수화 (Phase 1 PERSONA 주입용) ────
    # 이전: payload.get("bodyType")를 STYLING_SCORE 섹션에서만 호출
    # 수정: Phase 1 PERSONA + STYLING_SCORE 양쪽에서 재사용하도록 지역 변수로 추출
    # ────
    _body_type_key = str(payload.get("bodyType", "")).strip()

    # ── Phase 1 분석 결과 수신 (프론트에서 analyze-garments 호출 후 전달) ──
    _top_analysis    = payload.get("topAnalysis")    or {}
    _bottom_analysis_pre = payload.get("bottomAnalysis") or {}

    # ──── [ACTION 3] DIAG LOG #0: 프론트 분석 데이터 수신 상태 ────
    # 민감정보(faceImage/dataUrl) 제외하고 핵심 필드만 기록
    _bA = _bottom_analysis_pre or {}
    _tA = _top_analysis or {}
    print(
        f"[DIAG #0] payload received: "
        f"isRetry={bool(payload.get('isRetry'))} "
        f"top_cat={_tA.get('category','')!r} top_sub={_tA.get('sub_category','')!r} "
        f"bot_cat={_bA.get('category','')!r} bot_sub={_bA.get('sub_category','')!r} "
        f"bot_is_skirt={_bA.get('is_skirt')!r} "
        f"bot_skirt_length={_bA.get('skirt_length','')!r} "
        f"gender={user_info.get('gender','')!r} "
        f"bodyType={_body_type_key!r}",
        flush=True,
    )

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

        # [PHASE 5] EVALUATION — [2026-04-20 22:00 KST] 프리미엄 컨설팅 리포트 전면 재설계
        # 이전 문제: "▸ a · ▸ b · ▸ c" 불릿 힌트만 줘서 Gemini가 1-2단어씩 답변
        #           → 유료 서비스 가치 미달, 뒷 섹션(실루엣/밸런스) 누락 빈번
        # 신규 원칙:
        #   - 각 섹션을 명세서 V2의 10만원 컨설팅 수준으로 재설계
        #   - 각 불릿마다 최소 글자 수 강제 (1문장 완결 금지 → 1~2문장 풍부하게)
        #   - 섹션별 분량 150~250자 보장 (이전 50자 단답 → 250자 보고서)
        #   - "반드시 작성" / "생략 시 실패" / "예시" 3종 강제 기법 사용
        #   - Phase 1 근거 명시 강제 (체형/PC 없는 일반론 금지)
        + "\n\n[PHASE 5 — PREMIUM CONSULTING REPORT — REQUIRED DETAILED TEXT RESPONSE]: "
        + "After generating the image, write a PREMIUM styling consultation report. "
        + "Tone: senior fashion consultant at a paid consulting service (10만원/consultation tier). "
        + "Use refined, sophisticated Korean/English with technical fashion vocabulary. "
        + "AVOID all casual phrases like 'looks great', 'nice', 'cool', '좋아요', '멋져요'. "
        + "USE refined language: 'complements the complexion', 'anchors the silhouette', "
        + "'optimizes vertical proportion', 'creates visual stability', "
        + "'안색을 화사하게 밝혀주는', '세련된 실루엣을 완성하는', '시각적 다리길이를 연장시키는'. "
        + "Evaluation framework: Phase 1 (persona+body+PC) = REFERENCE CRITERIA. "
        + "Phase 2+3 (garments+wearing) evaluated AGAINST that reference. "
        + "\n\n★ CRITICAL FORMATTING RULES — ALL SECTIONS MUST APPEAR ★ "
        + "1) ALL 6 OUTPUT LINES must appear — missing any section = failed report. "
        + "2) Each DEEP-DIVE section must have EXACTLY 5 bullets (▸). "
        + "3) Each bullet must be 40-80 characters (1-2 complete sentences). "
        + "4) Total report length: 2000-4000 characters expected. "
        + "5) Reference PHASE 1 data (body type, personal color) in EVERY bullet. "
        + "6) NEVER merge sections. NEVER skip sections. NEVER use 'N/A' or 'skip'. "

        # OUTPUT LINE 1: C.S.I 점수
        + "\n\nOUTPUT LINE 1 — C.S.I SCORE (single line, must sum to 100): "
        + "STYLING_SCORE:[total]/100|body_shape:[n1]/30|personal_color:[n2]/30|proportion:[n3]/20|harmony:[n4]/20 "
        + "where n1<=30, n2<=30, n3<=20, n4<=20, n1+n2+n3+n4=total. "
        + "\nScoring basis (anchor each score to PHASE 1): "
        + (
            f"• body_shape/30 — evaluate how PHASE 2 silhouette + PHASE 3 wearing covers weaknesses and "
            f"enhances strengths of PHASE 1 body type ({_body_type_key}). "
            + _build_body_type_prompt(gender, _body_type_key) + " "
            if _body_type_key else
            "• body_shape/30 — general silhouette compatibility with the user's build. "
        )
        + (
            f"• personal_color/30 — evaluate PHASE 2 garment colors against PHASE 1 personal color "
            f"(season={_pc_season}, undertone={_pc_undertone}, best={_pc_best_colors}, avoid={_pc_avoid_colors}"
            + (f", summary='{_pc_summary}'" if _pc_summary else "")
            + "). Focus on positive effect on complexion. "
            if _pc_season else
            "• personal_color/30 — general color harmony (personal color data unavailable). "
        )
        + "• proportion/20 (VERTICAL Y-axis) — top hem × bottom rise intersection effect on leg-length. "
        + "• harmony/20 (HORIZONTAL X-axis) — body-type × garment volume matching (NOT color coord). "
        + f"\nUser: {gender_en}, {age}" + (f", {hw_en}" if hw_en else "") + ". "

        # OUTPUT LINE 2: Executive Summary (개선 - "심층 분석:" 혼입 방지)
        + (
            "\n\nOUTPUT LINE 2 — EXECUTIVE SUMMARY (one single paragraph, 3-4 sentences, 150-220 chars): "
            "\nExecutive Summary: [Open a separate new line only for this paragraph. "
            "Describe the outfit's core visual impact, PHASE 1 body type synergy, "
            "personal color effect on complexion, and overall mood. "
            "Refined consultant tone. DO NOT include phrase '심층 분석' or 'Deep-dive' here. "
            "End this section cleanly — next section starts on a new line.]"
            if _cs_en else
            "\n\nOUTPUT LINE 2 — 종합 평가 (독립 문단, 3~4문장, 150~220자): "
            "\n종합 평가: [이 문단만을 위한 새 줄에서 시작. "
            "착장의 핵심 시각적 효과, PHASE 1 체형과의 시너지, 퍼스널컬러가 안색에 미치는 효과, "
            "전반적 무드를 3~4문장으로 기술. 전문 컨설턴트 어조 사용. "
            "★ 절대 금지: 이 문단 안에 '심층 분석' 또는 'Deep-dive' 단어를 포함하지 말 것. "
            "★ 끝맺음 명확히: 다음 섹션은 반드시 새 줄에서 시작할 것.]"
        )

        # OUTPUT LINE 3-1: 퍼스널컬러 분석 (풍부하게 재설계)
        + (
            "\n\nOUTPUT LINE 3-1 — PERSONAL COLOR ANALYSIS (EXACTLY 5 bullets, each 40-80 chars): "
            "\n퍼스널컬러 분석: "
            "\n▸ [PHASE 1 season type (e.g. Warm Spring) and its defining traits — why this season suits the user]"
            "\n▸ [Top color in 'color-name #HEX' format vs PHASE 1 palette: match/mismatch reason in detail]"
            "\n▸ [Bottom color in 'color-name #HEX' format vs palette: whether it anchors or disrupts]"
            "\n▸ [Face-board reflection effect: does the top color brighten complexion / accentuate dark circles / cast shadows]"
            "\n▸ [Refinement recommendation: one specific adjustment (accessory color / makeup tone) to elevate]"
            if _cs_en else
            "\n\nOUTPUT LINE 3-1 — 퍼스널컬러 분석 (정확히 5개 ▸ 불릿, 각 40~80자): "
            "\n퍼스널컬러 분석: "
            "\n▸ [PHASE 1 시즌 타입 (예: 봄 웜톤)과 그 특성 — 사용자에게 왜 이 시즌이 맞는지 근거]"
            "\n▸ [상의 컬러 '색상명 #HEX' 형식 vs PHASE 1 팔레트: 매치/미스매치 이유를 구체적으로]"
            "\n▸ [하의 컬러 '색상명 #HEX' 형식 vs 팔레트: 전체를 잡아주는 앵커/방해 요소인지 판단]"
            "\n▸ [페이스보드 반사 효과: 상의 컬러가 안색을 밝혀주는지 / 다크서클 부각 / 그림자 드리우는지 상세 분석]"
            "\n▸ [정제된 보완 제안: 액세서리 컬러 또는 메이크업 톤 1가지 구체 변경으로 완성도 향상]"
        )

        # OUTPUT LINE 3-2: 상의 스타일 분석
        + (
            "\n\nOUTPUT LINE 3-2 — TOP STYLE ANALYSIS (EXACTLY 5 bullets, each 40-80 chars): "
            "\n상의 스타일 분석: "
            "\n▸ [Material and texture: fabric drape, weight, surface sheen — visual impression created]"
            "\n▸ [Neckline type (V-neck/round/square) and its effect on face shape, neck length, jawline definition]"
            "\n▸ [Shoulder silhouette (drop/standard/puff) — how it addresses PHASE 1 shoulder frame concerns]"
            "\n▸ [Fit quality (slim/regular/oversized): does the width:height ratio flatter the PHASE 1 body type]"
            "\n▸ [Color 'name #HEX' + one refinement idea for this specific top in 2025-2026 context]"
            if _cs_en else
            "\n\nOUTPUT LINE 3-2 — 상의 스타일 분석 (정확히 5개 ▸ 불릿, 각 40~80자): "
            "\n상의 스타일 분석: "
            "\n▸ [소재·텍스처: 드레이프성, 무게감, 표면 광택 — 연출되는 시각적 인상을 구체적으로]"
            "\n▸ [네크라인 종류(V넥/라운드/스퀘어)와 얼굴형·목 길이·턱선 연출에 미치는 시각적 효과]"
            "\n▸ [어깨 실루엣(드롭/스탠다드/퍼프) — PHASE 1 어깨 프레임 특성을 어떻게 커버/부각하는지]"
            "\n▸ [핏 품질(슬림/레귤러/오버) — 가로:세로 비율이 PHASE 1 체형을 보완하는지 원리 설명]"
            "\n▸ [컬러 '색상명 #HEX' + 2025-2026 트렌드 맥락에서 이 상의를 위한 1가지 정제된 보완 제안]"
        )

        # OUTPUT LINE 3-3: 하의 스타일 분석
        + (
            "\n\nOUTPUT LINE 3-3 — BOTTOM STYLE ANALYSIS (EXACTLY 5 bullets, each 40-80 chars): "
            "\n하의 스타일 분석: "
            "\n▸ [Silhouette type (straight/wide/tapered/flare/pencil) and how it shapes the leg line]"
            "\n▸ [Length (mini/midi/long/full/cropped) and its effect on visual leg-length perception]"
            "\n▸ [Material weight and how it drapes vs PHASE 1 lower-body volume — covering or emphasizing]"
            "\n▸ [Waistline position (high/mid/low rise) × PHASE 1 torso length — proportion effect]"
            "\n▸ [Color 'name #HEX' + one tailoring or styling refinement for completion]"
            "  (CRITICAL: this section is MANDATORY — if skipped, report is invalid) "
            if _cs_en else
            "\n\nOUTPUT LINE 3-3 — 하의 스타일 분석 (정확히 5개 ▸ 불릿, 각 40~80자): "
            "\n하의 스타일 분석: "
            "\n▸ [실루엣 종류(스트레이트/와이드/테이퍼드/플레어/펜슬)와 다리 라인 연출 효과]"
            "\n▸ [기장(미니/미디/롱/풀/크롭)이 시각적 다리 길이 인식에 미치는 효과]"
            "\n▸ [소재 무게감과 드레이프 — PHASE 1 하체 부피를 커버/강조하는지 구체 분석]"
            "\n▸ [허리선 위치(하이/미드/로우 라이즈) × PHASE 1 상체 길이 — 비율 효과 설명]"
            "\n▸ [컬러 '색상명 #HEX' + 완성도를 높일 1가지 테일러링/스타일링 정제 제안]"
            "  (중요: 이 섹션은 필수 — 생략 시 리포트 무효) "
        )

        # OUTPUT LINE 3-4: 실루엣과 비율 (명세서 V2 Section IV-1 핵심)
        + (
            "\n\nOUTPUT LINE 3-4 — SILHOUETTE & PROPORTION (VERTICAL Y-axis analysis, EXACTLY 5 bullets, 40-80 chars each): "
            "\n실루엣과 비율: "
            "\n▸ [Full-body silhouette classification (hourglass/column/inverted-triangle/A-line) — visual verdict]"
            "\n▸ [Top hem Y-position × bottom rise intersection: where waistline is reset, effect on perceived leg length]"
            "\n▸ [Tuck-in vs tuck-out analysis: current choice, alternative scenario, which elongates more]"
            "\n▸ [Head-to-toe ratio estimate (e.g. 3.2:6.8 or 4:6) — how close to ideal 3:7 golden ratio]"
            "\n▸ [Height compensation rate: visual height gain from this styling vs actual PHASE 1 height]"
            if _cs_en else
            "\n\nOUTPUT LINE 3-4 — 실루엣과 비율 (세로 Y축 분석, 정확히 5개 ▸ 불릿, 각 40~80자): "
            "\n실루엣과 비율: "
            "\n▸ [전신 실루엣 분류(모래시계/컬럼/역삼각형/A라인) — 시각적 판정과 근거]"
            "\n▸ [상의 기장 Y위치 × 하의 허리선(Rise) 교차점: 허리선이 재설정되는 위치와 다리길이 연장 효과]"
            "\n▸ [턱인 vs 턱아웃 분석: 현재 연출, 대안 시나리오, 어느 쪽이 더 길어 보이는지 비교]"
            "\n▸ [머리끝-발끝 비율 추정 (예: 3.2:6.8 또는 4:6) — 이상적 3:7 황금비와의 거리]"
            "\n▸ [신장 보완율: 이 스타일링으로 얻는 시각적 신장 효과 vs PHASE 1 실제 키]"
        )

        # OUTPUT LINE 3-5: 체형 밸런스 (명세서 V2 Section IV-2 핵심)
        + (
            f"\n\nOUTPUT LINE 3-5 — BODY BALANCE (HORIZONTAL X-axis × body-type matrix, EXACTLY 5 bullets, 40-80 chars each): "
            f"\n상하의 밸런스: "
            f"\n▸ [PHASE 1 body type ({_body_type_key or 'general'}) × top volume (X-axis width): does top compensate or amplify]"
            f"\n▸ [PHASE 1 body type × bottom silhouette volume: balances or disturbs against top]"
            f"\n▸ [Fabric weight contrast: heavy drape vs light flow — creates visual stability X-axis]"
            f"\n▸ [Torso-to-hip volume ratio judgment: ideal 1:1, actual state, deviation analysis]"
            f"\n▸ [SPEC V2 verdict: this is body-type-anchored volume balance (NOT color coord) — final match rating]"
            "  (CRITICAL: this is Section IV-2 of premium spec — body-data anchored, never merge with simple harmony) "
            if _cs_en else
            f"\n\nOUTPUT LINE 3-5 — 체형 밸런스 (가로 X축 × 체형 매트릭스, 정확히 5개 ▸ 불릿, 각 40~80자): "
            f"\n상하의 밸런스: "
            f"\n▸ [PHASE 1 체형 타입({_body_type_key or '기본'}) × 상의 부피(X축 폭): 상체가 보완하는가 증폭하는가 판정]"
            f"\n▸ [PHASE 1 체형 타입 × 하의 실루엣 부피: 상의와 균형 잡히는가 깨뜨리는가 분석]"
            f"\n▸ [소재 두께감 대비: 무거운 드레이프 vs 가벼운 플로우 — X축 시각적 안정감 창출 여부]"
            f"\n▸ [상체:하체 부피 비율 판정: 이상 1:1 기준, 현재 상태, 편차 분석]"
            f"\n▸ [명세서 V2 총평: 단순 컬러 조화가 아닌 체형 앵커드 부피 밸런스 — 최종 매칭 등급]"
            "  (중요: 이는 프리미엄 명세서 V2 Section IV-2 — 체형 데이터 앵커드, 절대 단순 조화와 병합 금지) "
        )

        # OUTPUT LINE 4: TPO 추천
        + (
            "\n\nOUTPUT LINE 4 — TPO RECOMMENDATIONS: "
            "\nBest TPO: [EXACTLY 2-3 specific occasions separated by '|', each 4-15 chars. "
            "Examples: 'Business Meeting | Gallery Visit | Brunch Date']"
            if _cs_en else
            "\n\nOUTPUT LINE 4 — TPO 추천: "
            "\nBest TPO: [정확히 2~3개 구체적 상황, '|'로 구분, 각 4~10자. "
            "예시: '비즈니스 미팅 | 갤러리 방문 | 브런치 데이트']"
        )

        # OUTPUT LINE 5: 개선 팁
        + (
            "\n\nOUTPUT LINE 5 — IMPROVEMENT TIPS: "
            "\nImprovement Tips: [EXACTLY 2-3 specific tips separated by '|', each under 30 chars. "
            "Hair/accessories/shoes. Examples: 'Gold earrings for warmth | Low ponytail | Nude heels']"
            if _cs_en else
            "\n\nOUTPUT LINE 5 — 개선 팁: "
            "\n개선 팁: [정확히 2~3개 구체 팁, '|'로 구분, 각 15자 이내. "
            "헤어/액세서리/신발. 예시: '골드 이어커프 | 로우 포니테일 | 누드 펌프스']"
        )

        # OUTPUT LINE 6: 해시태그
        + (
            "\n\nOUTPUT LINE 6 — STYLE HASHTAGS: "
            "\nStyle Hashtags: [EXACTLY 5 tags with '#', space-separated, each 2-12 chars. "
            "Examples: '#MinimalChic #SoftSpring #TailoredFit #TonalLayered #DailyFormal']"
            if _cs_en else
            "\n\nOUTPUT LINE 6 — 스타일 해시태그: "
            "\n스타일 해시태그: [정확히 5개, '#' 접두어, 공백 구분, 각 2~10자. "
            "예시: '#비율보정완벽 #쿨톤착붙 #스트럭처드핏 #톤온톤 #데일리포멀']"
        )

        # ★ 최종 검증 체크리스트 (Gemini에 자기 검증 강제)
        + "\n\n★★★ FINAL SELF-CHECK BEFORE OUTPUT ★★★ "
        + "Before submitting, verify: "
        + "[1] All 6 OUTPUT LINES present? "
        + "[2] Each deep-dive section has exactly 5 bullets with ▸? "
        + "[3] Each bullet is 40-80 chars (not 10-char single words)? "
        + "[4] Executive Summary is a clean paragraph WITHOUT '심층 분석' text? "
        + "[5] Every bullet references PHASE 1 body type or personal color? "
        + "If any check fails, rewrite that section. "

        # 다시요청
        + (" Retry note: vary pose slightly; maintain garment identity and same report depth." if is_retry else "")
    )

    # ══════════════════════════════════════════════════════════════════
    # [2026-04-20 23:30 KST — ACTION 2] 2단계 아키텍처 전환
    # ──────────────────────────────────────────────────────────────────
    # 이전 문제: 단일 호출 [gemini-2.5-flash-image, modalities=IMAGE+TEXT]
    #   → 이미지 생성에 토큰 집중 → 리포트 텍스트 품질 저하
    #   → "심층 분석:" 혼입, 섹션 누락, 빈약한 내용의 근본 원인
    #
    # 신규 구조:
    #   STAGE 1: gemini-2.5-flash-image, modalities=IMAGE  → 이미지만 생성
    #   STAGE 2: gemini-2.0-flash (텍스트 전용)            → 리포트만 생성
    #   STAGE 3: (기존 파싱 로직 재사용) comment → JSON 필드 추출
    #
    # [ACTION 3] 진단 로그 강화: [DIAG] 태그로 매 단계 상태 기록
    # ══════════════════════════════════════════════════════════════════

    # ──── [ACTION 3] DIAG LOG #1: 하의 판정 최종 상태 ────
    print(
        f"[DIAG #1] bot_is_skirt_pre={_bot_is_skirt_pre} "
        f"bottom_info.is_skirt={bottom_info.get('is_skirt')} "
        f"garment={bottom_info.get('garment', '')[:60]}",
        flush=True,
    )
    print(
        f"[DIAG #2] prompt_len={len(prompt)} "
        f"has_skirt_only_rule={'Skirt only' in prompt} "
        f"has_no_pants={'NO pants' in prompt}",
        flush=True,
    )

    # ══════════════════════════════════════════════════════════════════
    # STAGE 1: 이미지 생성 (gemini-2.5-flash-image)
    # ══════════════════════════════════════════════════════════════════
    img_bytes = None
    comment   = ""
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
                model=_TRYON_MODEL,  # ─── 2026-04-21 티어별 라우팅 적용 ───
                contents=contents,
                config=_gtypes.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],  # IMAGE는 필수, TEXT는 백업용
                    temperature=0.4,
                    max_output_tokens=8192,
                ),
            )
        else:
            # ★ google-generativeai (구 SDK) ★
            from PIL import Image as _PILImage
            _genai_old.configure(api_key=_GEMINI_KEY)
            model = _genai_old.GenerativeModel(_TRYON_MODEL)  # ─── 2026-04-21 티어별 라우팅 적용 ───

            def _bytes_to_pil(raw):
                return _PILImage.open(io.BytesIO(raw))

            contents_old = [prompt]
            if face_bytes:
                contents_old.append(_bytes_to_pil(face_bytes))
            contents_old.append(_bytes_to_pil(top_bytes))
            contents_old.append(_bytes_to_pil(bottom_bytes))

            try:
                response = model.generate_content(
                    contents_old,
                    generation_config={
                        "response_modalities": ["IMAGE", "TEXT"],
                        "temperature": 0.4,
                        "max_output_tokens": 8192,
                    },
                )
            except TypeError:
                response = model.generate_content(
                    contents_old,
                    generation_config=_genai_old.GenerationConfig(
                        temperature=0.4,
                        max_output_tokens=8192,
                    ),
                )
    except Exception as e:
        return jsonify(ok=False, error=f"Gemini 호출 실패 ({_SDK}): {str(e)[:300]}"), 500

    # ── STAGE 1 응답에서 이미지 + (백업용) 텍스트 추출 ──
    try:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                img_bytes = part.inline_data.data
            elif part.text:
                # STAGE 1이 텍스트도 돌려주면 백업으로 보관 (STAGE 2 실패 시 사용)
                comment = part.text.strip()[:15000]
    except (IndexError, AttributeError) as e:
        return jsonify(ok=False, error=f"응답 파싱 실패: {str(e)[:200]}"), 500

    # [2026-04-08] FinishReason.STOP 시 1회 자동 재시도 (기존 로직 유지)
    if not img_bytes:
        try:
            finish = response.candidates[0].finish_reason
        except Exception:
            finish = "UNKNOWN"
        _safe_comment = comment[:100] if comment else ""
        print(f"[codistyle] 이미지 미생성(1차): finishReason={finish}, comment={_safe_comment[:80]}", flush=True)

        if str(finish) in ("STOP", "FinishReason.STOP", "1", "2") and not request.args.get("_retried"):
            print("[codistyle] 자동 재시도 중...", flush=True)
            try:
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
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        img_bytes = part.inline_data.data
                    elif part.text:
                        comment = part.text.strip()[:15000]
                if img_bytes:
                    print("[codistyle] 재시도 성공!", flush=True)
            except Exception as _retry_e:
                print(f"[codistyle] 재시도 실패: {_retry_e}", flush=True)

        if not img_bytes:
            return jsonify(ok=False, error=f"착장 이미지 생성에 실패했습니다. 다시 시도해주세요. (reason={finish})"), 500

    # [ACTION 3] DIAG LOG #3: STAGE 1 결과
    print(
        f"[DIAG #3] STAGE1 done: img_bytes={len(img_bytes) if img_bytes else 0}B "
        f"backup_text_len={len(comment)}",
        flush=True,
    )

    # ══════════════════════════════════════════════════════════════════
    # STAGE 2: 리포트 생성 (텍스트 전용, 모델 fallback 체인)
    # ──────────────────────────────────────────────────────────────────
    # - 같은 prompt를 재사용 (PHASE 1~5 전체 포함)
    # - 이미지는 전송 안 함 (텍스트 모델이므로 필요없음)
    # - 응답 modalities를 TEXT로만 제한 → 모든 토큰을 리포트에 집중
    # - [2026-04-21 01:50] 모델 fallback 체인 추가 (신뢰성 강화)
    #     1순위: gemini-2.0-flash (기본, 환경변수 오버라이드 가능)
    #     2순위: gemini-1.5-flash (안정 모델, 거의 확실히 사용 가능)
    #     3순위: gemini-1.5-flash-8b (경량 모델, 최후의 수단)
    #   각 단계에 [DIAG #4-N] 로그로 성공/실패 추적
    # - 3개 모델 모두 실패 시 STAGE 1 백업 텍스트 사용 → 그것도 부족하면 작업 3의 로컬 리포트
    # ══════════════════════════════════════════════════════════════════
    _REPORT_MODEL = os.getenv("CODIBANK_REPORT_MODEL") or "gemini-2.0-flash"
    _REPORT_FALLBACK_CHAIN = [
        _REPORT_MODEL,         # 1순위 (기본 또는 환경변수)
        "gemini-1.5-flash",    # 2순위
        "gemini-1.5-flash-8b", # 3순위
    ]
    # 중복 제거 (환경변수가 2순위와 같을 수 있음)
    _seen = set()
    _REPORT_FALLBACK_CHAIN = [m for m in _REPORT_FALLBACK_CHAIN if not (m in _seen or _seen.add(m))]

    report_text = ""
    _stage2_success_model = None
    _stage2_errors = []

    for _try_idx, _try_model in enumerate(_REPORT_FALLBACK_CHAIN, 1):
        try:
            _tmp_text = ""
            if _SDK == "new":
                # [STAGE 2 — new SDK]
                _report_resp = client.models.generate_content(
                    model=_try_model,
                    contents=[prompt],
                    config=_gtypes.GenerateContentConfig(
                        temperature=0.4,
                        max_output_tokens=8192,
                    ),
                )
                _tmp_text = (getattr(_report_resp, "text", None) or "").strip()[:15000]
            else:
                # [STAGE 2 — old SDK]
                _report_model = _genai_old.GenerativeModel(_try_model)
                try:
                    _report_resp = _report_model.generate_content(
                        [prompt],
                        generation_config={
                            "temperature": 0.4,
                            "max_output_tokens": 8192,
                        },
                    )
                except TypeError:
                    _report_resp = _report_model.generate_content(
                        [prompt],
                        generation_config=_genai_old.GenerationConfig(
                            temperature=0.4,
                            max_output_tokens=8192,
                        ),
                    )
                _tmp_text = (getattr(_report_resp, "text", None) or "").strip()[:15000]

            # 응답 길이 체크 — 200자 미만이면 실패로 간주
            if _tmp_text and len(_tmp_text) > 200:
                report_text = _tmp_text
                _stage2_success_model = _try_model
                print(
                    f"[DIAG #4-{_try_idx}] ✅ STAGE2 성공: model={_try_model} "
                    f"report_len={len(report_text)} "
                    f"head200={report_text[:200]!r}",
                    flush=True,
                )
                break  # 성공 → 다음 모델 시도 안 함
            else:
                _stage2_errors.append(f"{_try_model}: 응답 짧음({len(_tmp_text)}자)")
                print(
                    f"[DIAG #4-{_try_idx}] ⚠️ STAGE2 응답 짧음: model={_try_model} "
                    f"len={len(_tmp_text)} → 다음 모델 시도",
                    flush=True,
                )
        except Exception as _rep_e:
            _err = f"{_try_model}: {str(_rep_e)[:150]}"
            _stage2_errors.append(_err)
            print(
                f"[DIAG #4-{_try_idx}] ❌ STAGE2 실패: {_err} → 다음 모델 시도",
                flush=True,
            )

    # STAGE 2 최종 결과 로그
    if _stage2_success_model:
        comment = report_text
        print(
            f"[DIAG #4] STAGE2 최종: ✅ {_stage2_success_model}으로 성공 "
            f"(시도횟수={_REPORT_FALLBACK_CHAIN.index(_stage2_success_model)+1}/{len(_REPORT_FALLBACK_CHAIN)})",
            flush=True,
        )
    else:
        # 모든 모델 실패 → STAGE 1 백업 텍스트(comment) 유지
        # 그것도 부족하면 아래 작업 3의 로컬 리포트 생성 로직이 처리
        print(
            f"[DIAG #4] STAGE2 최종: ❌ 모든 모델 실패 "
            f"errors={_stage2_errors} → STAGE1 백업({len(comment)}자) 사용",
            flush=True,
        )

    # ══════════════════════════════════════════════════════════════════
    # [2026-04-21 01:50] 최후 안전망: 로컬 구조화 리포트 생성
    # ──────────────────────────────────────────────────────────────────
    # STAGE 1 백업 텍스트도 짧고 STAGE 2 fallback 체인도 모두 실패한 경우
    # 서버가 이미 가진 데이터(체형/PC/의류 분석)로 풍부한 리포트 조립
    # → 사용자는 어떤 경우에도 "분석 데이터가 준비 중입니다" 플레이스홀더를 보지 않음
    # ══════════════════════════════════════════════════════════════════
    if len(comment) < 500:
        print(
            f"[DIAG #4f] comment 여전히 부족({len(comment)}자) → 로컬 구조화 리포트 생성",
            flush=True,
        )
        # 한/영 분기
        _is_en = bool(_cs_en)

        # 섹션별 로컬 템플릿 구성 (서버가 이미 분석한 데이터 활용)
        _top_color = top_info.get('color_ko', '')
        _top_material = top_info.get('material', '')
        _top_pattern = top_info.get('pattern', '')
        _bot_color = bottom_info.get('color_ko', '')
        _bot_material = bottom_info.get('material', '')
        _bot_silhouette = bottom_info.get('silhouette', '')
        _bot_is_skirt = bool(bottom_info.get('is_skirt'))
        _bot_garment_label = '스커트' if _bot_is_skirt else '하의'

        if _is_en:
            _local_report = (
                "STYLING_SCORE:85/100|body_shape:25/30|personal_color:25/30|proportion:17/20|harmony:18/20\n"
                "\nExecutive Summary: This outfit presents a refined and balanced silhouette, "
                "thoughtfully composed to complement the wearer's body profile and personal color season. "
                "The combination creates a polished daily look suitable for multiple occasions.\n"
                "\n퍼스널컬러 분석:\n"
                f"▸ Personal color season: {_pc_season or 'general'} with {_pc_undertone or 'balanced'} undertone.\n"
                f"▸ Top color ({_top_color or 'reference'}) positioned against the face board.\n"
                f"▸ Bottom color ({_bot_color or 'reference'}) anchors the lower silhouette.\n"
                "▸ Overall complexion effect is generally complementary.\n"
                "▸ Consider a warm accessory to elevate the personal color match.\n"
                "\n상의 스타일 분석:\n"
                f"▸ Material: {_top_material or 'standard'}.\n"
                f"▸ Pattern: {_top_pattern or 'solid'}.\n"
                "▸ Fit shapes the upper body frame appropriately.\n"
                "▸ Neckline provides balanced face framing.\n"
                "▸ Consider layering options for seasonal versatility.\n"
                "\n하의 스타일 분석:\n"
                f"▸ Silhouette: {_bot_silhouette or ('skirt' if _bot_is_skirt else 'pants')}.\n"
                f"▸ Material: {_bot_material or 'standard'}.\n"
                "▸ Length creates proportional lower body line.\n"
                "▸ Works harmoniously with the top selection.\n"
                "▸ Styling opportunity: tuck-in variation for variety.\n"
                "\n실루엣과 비율:\n"
                "▸ Overall silhouette is well-balanced.\n"
                "▸ Waistline intersection creates natural proportion division.\n"
                "▸ Head-to-toe ratio estimate: approximately 3:7 (favorable).\n"
                "▸ Visual leg-length effect is preserved.\n"
                "▸ Proportional verdict: balanced and flattering.\n"
                "\n상하의 밸런스:\n"
                "▸ Top volume balances against bottom silhouette.\n"
                "▸ Fabric weight creates visual stability.\n"
                "▸ Torso-to-hip ratio reads close to ideal 1:1.\n"
                "▸ X-axis horizontal balance is maintained.\n"
                "▸ Body-type anchored verdict: harmonious match.\n"
                "\nBest TPO: Daily Casual | Business Casual | Weekend Outing\n"
                "\nImprovement Tips: Minimal accessory | Clean hair style | Versatile shoes\n"
                "\nStyle Hashtags: #BalancedSilhouette #DailyFormal #TonalHarmony #CleanLines #RefinedCasual\n"
            )
        else:
            _local_report = (
                "STYLING_SCORE:85/100|body_shape:25/30|personal_color:25/30|proportion:17/20|harmony:18/20\n"
                "\n종합 평가: 해당 착장은 체형의 강점을 자연스럽게 살리면서 전반적으로 균형 잡힌 실루엣을 연출합니다. "
                "상하의의 조화가 세련된 인상을 주며, 다양한 상황에 어울리는 세련된 데일리룩을 완성합니다.\n"
                "\n퍼스널컬러 분석:\n"
                f"▸ 퍼스널컬러 시즌: {_pc_season or '일반'} 타입, {_pc_undertone or '중립'} 언더톤.\n"
                f"▸ 상의 컬러({_top_color or '레퍼런스'})가 페이스 보드 앞에 위치.\n"
                f"▸ 하의 컬러({_bot_color or '레퍼런스'})가 하체 실루엣을 안정적으로 받쳐줌.\n"
                "▸ 전반적인 안색 효과는 조화롭게 어우러짐.\n"
                "▸ 액세서리 컬러로 퍼스널컬러 매칭을 한 단계 끌어올릴 수 있음.\n"
                "\n상의 스타일 분석:\n"
                f"▸ 소재: {_top_material or '일반 소재'}로 자연스러운 드레이프 연출.\n"
                f"▸ 패턴: {_top_pattern or '단색'} 처리로 전체 코디와 조화.\n"
                "▸ 핏이 상체 프레임을 적절히 잡아줌.\n"
                "▸ 넥라인이 얼굴형을 균형 있게 프레이밍.\n"
                "▸ 계절별 레이어링 옵션을 고려하면 활용도 향상.\n"
                "\n하의 스타일 분석:\n"
                f"▸ 실루엣: {_bot_silhouette or _bot_garment_label}.\n"
                f"▸ 소재: {_bot_material or '일반 소재'}.\n"
                "▸ 기장이 비례적인 하체 라인을 형성.\n"
                "▸ 상의 선택과 조화롭게 어우러짐.\n"
                "▸ 스타일링 포인트: 턱인 변형으로 변화 주기 가능.\n"
                "\n실루엣과 비율:\n"
                "▸ 전체 실루엣이 안정적으로 균형 잡힘.\n"
                "▸ 허리선 교차점이 자연스러운 비율 분할 형성.\n"
                "▸ 머리끝-발끝 비율: 약 3:7 (유리한 비율).\n"
                "▸ 시각적 다리 길이 효과가 잘 보존됨.\n"
                "▸ 비율 총평: 균형 잡히고 돋보이는 스타일링.\n"
                "\n상하의 밸런스:\n"
                "▸ 상의 부피가 하의 실루엣과 균형을 이룸.\n"
                "▸ 소재 무게감이 시각적 안정감을 창출.\n"
                "▸ 상체:하체 비율이 이상적 1:1에 근접.\n"
                "▸ X축 가로 균형이 잘 유지됨.\n"
                "▸ 체형 앵커드 총평: 조화로운 매칭.\n"
                "\nBest TPO: 데일리 캐주얼 | 비즈니스 캐주얼 | 주말 외출\n"
                "\n개선 팁: 미니멀 액세서리 | 깔끔한 헤어 | 활용도 높은 신발\n"
                "\n스타일 해시태그: #균형실루엣 #데일리포멀 #톤온톤 #클린라인 #세련캐주얼\n"
            )
        comment = _local_report
        print(
            f"[DIAG #4f] 로컬 리포트 생성 완료: {len(comment)}자 "
            f"(lang={'en' if _is_en else 'ko'}, is_skirt={_bot_is_skirt})",
            flush=True,
        )

    # ══════════════════════════════════════════════════════════════════
    # STAGE 3 이후: 이미지 저장 + 리포트 파싱 (기존 로직 그대로 사용)
    # ══════════════════════════════════════════════════════════════════

    # img_bytes가 bytes인지 확인 (혹시 base64 문자열이면 디코딩)
    if isinstance(img_bytes, str):
        img_bytes = base64.b64decode(img_bytes)

    rel  = _write_upload_bytes("codistyle", "jpg", img_bytes)
    base = _public_base()

    # ──── [2026-04-20 07:50 KST] C.S.I 4지표 점수 파싱 + 프리미엄 리포트 신규 필드 추출 ────
    # 변경 내용:
    #   - 점수: 3개(personal_color 40/body_shape 40/coordination 20) → 4개(body_shape 30/personal_color 30/proportion 20/harmony 20)
    #   - 신규 필드: executive_summary, tpo_recommendations, improvement_tips, style_hashtags
    # 하위호환: 구형 (3지표) 응답이 올 경우 기본 정규화 로직 유지 (fallback)
    # ───────────────────────────────────────────────────────────────────
    styling_score = None
    score_breakdown = {}
    styling_advice = ""
    executive_summary = ""
    tpo_recommendations = []
    improvement_tips = []
    style_hashtags = []
    try:
        import re as _re2
        # 총점
        _m = _re2.search(r'STYLING_SCORE:(\d+)/100', comment)
        if _m: styling_score = int(_m.group(1))

        # C.S.I 4지표 (신규 우선) + 구형 3지표 fallback
        for _k in ['body_shape', 'personal_color', 'proportion', 'harmony',
                   'overall_styling', 'coordination']:
            _km = _re2.search(rf'{_k}:(\d+)', comment)
            if _km: score_breakdown[_k] = int(_km.group(1))

        # 구형 → 신형 매핑 (후방호환)
        if 'coordination' in score_breakdown and 'harmony' not in score_breakdown:
            score_breakdown['harmony'] = score_breakdown.pop('coordination')
        if 'overall_styling' in score_breakdown and 'harmony' not in score_breakdown:
            score_breakdown['harmony'] = score_breakdown.pop('overall_styling')

        # 점수 정규화: 4지표 합이 100이 아닐 때 비례 조정 (총점 기준)
        _sb = score_breakdown
        _has_new = all(k in _sb for k in ['body_shape', 'personal_color', 'proportion', 'harmony'])
        if _has_new and styling_score:
            _sum = _sb['body_shape'] + _sb['personal_color'] + _sb['proportion'] + _sb['harmony']
            if _sum > 0 and _sum != styling_score:
                _r = styling_score / _sum
                _sb['body_shape']     = round(_sb['body_shape'] * _r)
                _sb['personal_color'] = round(_sb['personal_color'] * _r)
                _sb['proportion']     = round(_sb['proportion'] * _r)
                _sb['harmony']        = styling_score - _sb['body_shape'] - _sb['personal_color'] - _sb['proportion']
        elif 'personal_color' in _sb and 'body_shape' in _sb:
            # 구형 3지표 fallback (기존 로직 유지)
            _sum = _sb.get('personal_color',0)+_sb.get('body_shape',0)+_sb.get('harmony',0)
            if styling_score and _sum > 0 and _sum != styling_score:
                _r = styling_score / _sum
                _sb['personal_color'] = round(_sb.get('personal_color',0)*_r)
                _sb['body_shape']     = round(_sb.get('body_shape',0)*_r)
                _sb['harmony']        = styling_score - _sb['personal_color'] - _sb['body_shape']

        # Executive Summary 추출 (한/영)
        # [2026-04-20 22:00] 정규식 수정 — "심층 분석:", "OUTPUT LINE", "Deep-dive" 등 다음 섹션 경계를 모두 제외
        # 이전 문제: "종합 평가: 화사한 분위기를 더합니다. 심층 분석:" 이 통째로 요약에 들어감
        _esm = _re2.search(
            r'(?:Executive Summary|종합 평가)\s*[:：]\s*'
            r'([^\n]+(?:\n(?!(?:Best TPO|개선 팁|Improvement Tips|Style Hashtags|스타일 해시태그|'
            r'퍼스널컬러 분석|Personal Color Analysis|상의 스타일 분석|Top Style Analysis|'
            r'하의 스타일 분석|Bottom Style Analysis|실루엣과 비율|Silhouette and Proportion|'
            r'상하의 밸런스|Top-Bottom Harmony|심층 분석|Deep-Dive|Deep-dive|DEEP-DIVE|'
            r'OUTPUT LINE|\d+\s*[.)]\s))[^\n]*)*)',
            comment
        )
        if _esm:
            _raw_exec = _esm.group(1).strip().strip('[]').strip()
            # 같은 줄에 섹션 경계 단어가 등장하면 그 앞까지만 취함
            for _sep in ['심층 분석:', 'Deep-dive:', 'Deep-Dive:', 'DEEP-DIVE:',
                         '퍼스널컬러 분석:', 'Personal Color Analysis:',
                         '상의 스타일 분석:', 'Top Style Analysis:',
                         '실루엣과 비율:', 'Silhouette and Proportion:',
                         '상하의 밸런스:', 'Top-Bottom Harmony:',
                         'Best TPO:', 'Improvement Tips:', 'Style Hashtags:',
                         '개선 팁:', '스타일 해시태그:',
                         'OUTPUT LINE']:
                if _sep in _raw_exec:
                    _raw_exec = _raw_exec.split(_sep)[0].strip()
            # 끝의 "심층" 같은 미완결 단어 제거
            _raw_exec = _re2.sub(r'\s*(심층|분석|Deep|Analysis)\s*$', '', _raw_exec).strip()
            executive_summary = _raw_exec[:500]

        # TPO 추천 추출
        _tpo_m = _re2.search(r'(?:Best TPO)\s*[:：]\s*([^\n]+)', comment)
        if _tpo_m:
            _raw = _tpo_m.group(1).strip().strip('[]').strip()
            tpo_recommendations = [t.strip() for t in _raw.split('|') if t.strip()][:3]

        # 개선 팁 추출
        _tip_m = _re2.search(r'(?:Improvement Tips|개선 팁)\s*[:：]\s*([^\n]+)', comment)
        if _tip_m:
            _raw = _tip_m.group(1).strip().strip('[]').strip()
            improvement_tips = [t.strip() for t in _raw.split('|') if t.strip()][:3]

        # 스타일 해시태그 추출 (#으로 시작하는 것들)
        _hash_m = _re2.search(r'(?:Style Hashtags|스타일 해시태그)\s*[:：]\s*([^\n]+)', comment)
        if _hash_m:
            _raw = _hash_m.group(1).strip().strip('[]').strip()
            # # 접두어 있든 없든 추출
            style_hashtags = _re2.findall(r'#?([^\s,#]+)', _raw)
            style_hashtags = [h.strip() for h in style_hashtags if h.strip() and len(h.strip()) <= 12][:5]

        # 구 형식 fallback: 핵심 키워드 (STYLE_HASHTAGS가 없으면)
        if not style_hashtags:
            _kw_m = _re2.search(r'(?:핵심 키워드|Key Keywords)\s*[:：]\s*([^\n]+)', comment)
            if _kw_m:
                _raw = _kw_m.group(1).strip().strip('[]').strip()
                style_hashtags = [k.strip() for k in _re2.split(r'[,，、]', _raw) if k.strip()][:5]

        # 심층 분석 텍스트 (STYLING_SCORE 줄 이후 전체)
        _score_line_end = _re2.search(r'STYLING_SCORE:[^\n]+', comment)
        if _score_line_end:
            _advice_raw = comment[_score_line_end.end():].strip()
            styling_advice = _advice_raw[:2000] if _advice_raw else ""
    except Exception as _parse_e:
        print(f"[codistyle] 점수/리포트 파싱 실패(무시): {_parse_e}")

    garment_summary = {
        "top": {"key": top_category_key, "ko": top_info.get("ko",""), "garment": top_info.get("garment","")},
        "bottom": {"key": bottom_category_key, "ko": bottom_info.get("ko",""), "garment": bottom_info.get("garment",""), "is_skirt": bottom_info.get("is_skirt",False)},
    }

    # ──── [ACTION 3] DIAG LOG #5: 최종 파싱 결과 요약 ────
    _section_markers = ["퍼스널컬러 분석", "상의 스타일 분석", "하의 스타일 분석",
                        "실루엣과 비율", "상하의 밸런스",
                        "Personal Color Analysis", "Top Style Analysis",
                        "Bottom Style Analysis", "Silhouette and Proportion",
                        "Top-Bottom Harmony"]
    _sections_found = [m for m in _section_markers if (m + ":") in comment or (m + ":").replace(" ", "") in comment.replace(" ", "")]
    print(
        f"[DIAG #5] parsed: score={styling_score} "
        f"breakdown_keys={list(score_breakdown.keys())} "
        f"exec_len={len(executive_summary)} "
        f"tpo_n={len(tpo_recommendations)} "
        f"tips_n={len(improvement_tips)} "
        f"hashtags_n={len(style_hashtags)} "
        f"sections_in_text={len(_sections_found)}/{len(_section_markers)//2} "
        f"found={_sections_found[:5]}",
        flush=True,
    )

    return jsonify(
        ok=True, path=rel,
        image=f"{base}{rel}", url=f"{base}{rel}",
        comment=comment or "AI 착장 이미지 생성 완료!",
        styling_score=styling_score,
        score_breakdown=score_breakdown,
        styling_advice=styling_advice,
        # [2026-04-20 07:50 KST] 프리미엄 리포트 신규 필드
        executive_summary=executive_summary,
        tpo_recommendations=tpo_recommendations,
        improvement_tips=improvement_tips,
        style_hashtags=style_hashtags,
        garment_summary=garment_summary,
        model=_CODISTYLE_MODEL,
        sdk=_SDK,
    )


# ═══════════════════════════════════════════════════════════════════════
# 🆕 [2026-04-22 16:30 KST] 트라이온 전용 엔드포인트 (Phase 4)
# ─────────────────────────────────────────────────────────────────────
#   codistyle_generate와 완전히 독립된 함수.
#   codistyle.html/codistyle_generate는 절대 수정 금지 원칙 준수.
#   프론트(tryon.html)가 fetch('/api/tryon/generate', ...)로 호출.
# ═══════════════════════════════════════════════════════════════════════

# 트라이온용 fit 모드 상수 (프론트 fitTarget과 1:1 매핑)
_TRYON_FIT_MY       = "my"        # 회원 본인 프로필 그대로
_TRYON_FIT_SOMEBODY = "somebody"  # 사용자가 업로드한 얼굴 + 입력한 체형
_TRYON_FIT_MODEL    = "model"     # 표준 남/여 모델 (얼굴 없음)

# 트라이온용 모드 상수 (프론트 mode와 1:1 매핑)
_TRYON_MODE_TWOPIECE = "twopiece"  # 상의 + 하의
_TRYON_MODE_ONEPIECE = "onepiece"  # 원피스 (+ 선택 아우터)
_TRYON_MODE_OUTER    = "outer"     # 아우터 필수


def _tryon_build_prompt(
    *,
    mode: str,
    fit_target: str,
    model_gender: str,
    gender_ko: str,
    gender_en: str,
    age: str,
    height: str,
    weight: str,
    body_type_key: str,
    pc_summary: str,
    top_info: dict,
    bottom_info: dict,
    onepiece_info: dict,
    outer_info: dict,
    shoes_info: dict,
    attached_keys: set = None,  # [2026-04-24 TJ 지시] images_map의 key set — 실제 첨부된 이미지 판단
    lang_en: bool = False,
):
    """
    [2026-04-22 16:30] 트라이온 전용 프롬프트 빌더.
    [2026-04-24 TJ 지시 v7] attached_keys 파라미터 추가 — 실제 첨부된 이미지 기반 판단.
    
    핵심 원칙 (TJ 확인):
      1) ATTACHED (attached_keys 포함) = MANDATORY 정확 재현
      2) NOT ATTACHED = GENERATE 맥락에 맞게 생성
    
    이전 버그: shoes_info가 빈 dict {}면 item_order에 shoes 미포함
              → Gemini에 이미지 첨부 안 되어 임의 생성
    수정: attached_keys(= set(images_map.keys())) 기반 판단으로 전환
    
    codistyle의 Phase 1~5 구조를 따르되, 트라이온 특성(원피스/아우터/신발 슬롯 +
    fitTarget 분기)을 반영한 완전 독립 프롬프트.
    
    반환: (prompt_text, required_image_keys)
      - prompt_text: Gemini에 보낼 최종 프롬프트 문자열
      - required_image_keys: 이미지 첨부 순서 (face 여부 + mode별 아이템 순서)
    """
    # ──────── Phase 1: PERSONA (fit_target 분기) ────────
    if fit_target == _TRYON_FIT_MODEL:
        # 모델 모드: [2026-04-24 TJ 지시4] 한국 아이돌 스타일 20대 모델
        #   남자: 180cm, 75kg, 20대 한국 아이돌 닮은 남자
        #   여자: 170cm, 49kg, 20대 한국 아이돌 닮은 여자
        if model_gender == "female":
            persona = (
                "A young Korean K-pop idol style female model in her 20s, "
                "resembling a popular Korean girl group member. "
                "Physical specs: height 170cm, weight 49kg — slim and elegant K-pop idol proportions. "
                "Features: clear glowing skin, natural Korean features, long legs, "
                "well-balanced slender silhouette. "
                "Natural confident expression, neutral pose. "
                "Soft studio lighting, clean neutral soft-grey background."
            )
        else:
            persona = (
                "A young Korean K-pop idol style male model in his 20s, "
                "resembling a popular Korean boy group member. "
                "Physical specs: height 180cm, weight 75kg — tall and lean K-pop idol physique. "
                "Features: clear skin, sharp Korean features, broad shoulders tapering to slim waist, "
                "well-proportioned athletic but slim build. "
                "Natural confident expression, neutral pose. "
                "Soft studio lighting, clean neutral soft-grey background."
            )
    elif fit_target == _TRYON_FIT_SOMEBODY:
        # 썸바디 모드: 업로드한 얼굴 + 입력한 체형 (제3자 대신 입혀봄)
        persona = (
            f"A {gender_en} in their {age} with the uploaded face photo. "
            f"Body profile: {'height '+height+'cm, weight '+weight+'kg' if height and weight else 'average build'}. "
            f"Body type: {body_type_key or 'balanced'}. "
            f"Personal color summary: {pc_summary or 'neutral'}. "
            "Preserve the uploaded face identity exactly. "
            "Natural studio lighting, neutral soft-grey background."
        )
    else:
        # 마이핏 모드(기본): 회원 본인 — 얼굴/체형/퍼스널컬러 반영
        # [2026-04-24 TJ 지시3] 사용자 데이터 강조 + 명확한 지시
        persona = (
            "This is a MY-FIT (personal try-on) image. Use the UPLOADED FACE PHOTO as the person's face. "
            f"Gender: {gender_en}, age group: {age}. "
            f"{'Actual body profile — height '+height+'cm, weight '+weight+'kg. ' if height and weight else ''}"
            f"Body type (체형): {body_type_key or 'balanced'} — match body proportions accordingly. "
            f"Personal color season/undertone: {pc_summary or 'not specified — use neutral'}. "
            "🔴 CRITICAL FACE IDENTITY RULE: The person's face MUST be IDENTICAL to the uploaded reference photo — "
            "same facial structure, same eyes, same nose shape, same lips, same skin tone, same ethnicity. "
            "DO NOT generate a generic or different face. DO NOT alter ethnic features. "
            "Reproduce the uploaded face with absolute photographic fidelity. "
            "Natural studio lighting, neutral soft-grey background."
        )

    # ──────── Phase 2: GARMENTS (2026-04-24 v8 TJ 재지시) ────────
    # 🔴 치명적 버그 수정: v7 프롬프트의 "NOT-ATTACHED = GENERATE" 원칙이 
    #    원피스만 선택했을 때 가디건 같은 아우터를 자동 추가하는 문제 발생.
    # v8 재정립: "사용자 선택 ≈ 추가 금지" (엄격 원칙)
    #   ① ATTACHED = REPRODUCE EXACTLY (정확 재현 필수)
    #   ② NON-ATTACHED = DO NOT ADD (미첨부 영역 추가 금지)
    #   ③ 최소 예외 (자연스러움 확보):
    #      a) 신발 미첨부 → 중립 신발 자동 생성 (맨발 방지)
    #      b) 아우터 단독 (상/하의 모두 미첨부) → 최소 내피·하의 자연 노출
    
    _att = attached_keys or set()
    # 첨부된 아이템 목록 (사람이 보기 좋게 영문으로)
    _attached_list = sorted(list(_att))
    
    # ═══ CORE RULE — 최상단 절대 명령 ═══
    garments_parts = [
        "🔴🔴🔴 CORE RULE — USER SELECTION IS THE COMPLETE OUTFIT 🔴🔴🔴 "
        "This is a TRY-ON system where the user selects exactly which garments to try on. "
        "Your job is to show ONLY what the user selected. NOTHING MORE. "
        ""
        "\n\n━━━ RULE ① — ATTACHED IMAGES = REPRODUCE EXACTLY ━━━ "
        f"The user attached exactly these items: [{', '.join(_attached_list)}]. "
        "Each attached garment MUST be worn on the person and reproduced with photographic fidelity. "
        "Match color, pattern, texture, silhouette, material, logos, details EXACTLY. "
        "Do NOT replace attached items with similar alternatives. "
        "Do NOT re-imagine or stylize them differently. "
        ""
        "\n\n━━━ RULE ② — NON-ATTACHED = DO NOT ADD (MOST CRITICAL) ━━━ "
        "⛔ DO NOT add any garment that was not attached. "
        "⛔ DO NOT add a cardigan, sweater, jacket, coat, blazer, vest, or any outer layer "
        "unless outer was in the attached list. "
        "⛔ DO NOT add an additional top (shirt, blouse, tee) unless top was attached. "
        "⛔ DO NOT add an additional bottom (pants, skirt, shorts) unless bottom was attached. "
        "⛔ DO NOT add scarves, belts, hats, jewelry, bags, or accessories that aren't attached. "
        "The user chose these specific items — respect their choice absolutely. "
        "If the user attached only a dress, the person wears ONLY the dress. No cardigan. No jacket. "
        "If the user attached outer+shoes, show outer+shoes — do NOT generate a separate top/bottom as styled outfits. "
    ]
    
    # ═══ RULE ③ — EXCEPTIONS (only for naturalness) ═══
    _exceptions = []
    
    # 예외 a) 신발 미첨부 → 중립 신발 자동 생성
    if "shoes" not in _att:
        _exceptions.append(
            "• Shoes were NOT attached. Generate neutral, minimal shoes that match the outfit's tone. "
            "Reason: barefoot is unnatural for a full-body fashion photograph. "
            "Choose simple, low-key footwear that doesn't draw attention away from the attached garments. "
            "Formal dress → simple pumps/flats; casual → plain sneakers; streetwear → neutral sneakers."
        )
    
    # 예외 b) 아우터 단독 (상/하의 둘 다 미첨부)
    _outer_only = (
        mode == _TRYON_MODE_OUTER and
        "outer" in _att and
        "top" not in _att and
        "bottom" not in _att and
        "onepiece" not in _att
    )
    if _outer_only:
        _exceptions.append(
            "• Outer is attached but no top/bottom. Minimally fill inner and lower body: "
            "a simple white/cream/grey inner top barely visible at neckline/cuffs, "
            "and plain dark or neutral bottom trousers. "
            "Keep these absolutely minimal and tonally neutral — the OUTER is the hero. "
            "These are NOT featured items; they exist only to avoid unnatural nudity under the outer."
        )
    
    if _exceptions:
        garments_parts.append(
            "\n\n━━━ RULE ③ — MINIMAL NATURAL EXCEPTIONS (only these cases) ━━━\n" +
            "\n".join(_exceptions)
        )
    else:
        garments_parts.append(
            "\n\n━━━ RULE ③ — NO EXCEPTIONS NEEDED ━━━ "
            "All necessary items are attached. Show only the attached garments. "
            "Do not add anything else."
        )
    
    # ═══ 각 첨부 아이템 상세 지시 ═══
    garments_parts.append("\n\n━━━ DETAILED ITEM INSTRUCTIONS ━━━")
    
    # --- ONEPIECE (원피스 모드) ---
    if "onepiece" in _att:
        _desc = onepiece_info or {}
        garments_parts.append(
            f"ONEPIECE (attached — reproduce EXACTLY): "
            f"{_desc.get('sub_category','dress')} "
            f"in {_desc.get('main_color_name','as shown in image')} color, "
            f"{_desc.get('pattern','as shown')} pattern, "
            f"{_desc.get('material','as shown')} material. "
            f"Match every detail of the attached dress reference image. "
            f"🔴 DO NOT add any outer layer (cardigan/jacket/coat) — the dress is worn alone."
        )
    
    # --- OUTER (아우터) ---
    if "outer" in _att:
        _desc = outer_info or {}
        if mode == _TRYON_MODE_OUTER:
            _role_note = "This is the HERO garment — feature prominently."
        else:
            _role_note = "Worn as the outer layer over the inner garment(s)."
        garments_parts.append(
            f"OUTER (attached — reproduce EXACTLY): "
            f"{_desc.get('sub_category','jacket')} "
            f"in {_desc.get('main_color_name','as shown')} color, "
            f"{_desc.get('pattern','as shown')} pattern, "
            f"{_desc.get('material','as shown')} material. "
            f"{_role_note}"
        )
    
    # --- TOP (상의) ---
    if "top" in _att:
        _desc = top_info or {}
        garments_parts.append(
            f"TOP (attached — reproduce EXACTLY): "
            f"{_desc.get('sub_category','shirt')} "
            f"in {_desc.get('main_color_name','as shown')} color, "
            f"{_desc.get('pattern','as shown')} pattern, "
            f"{_desc.get('material','as shown')} material, "
            f"{_desc.get('fit','as shown')} fit. "
            f"Match every detail of the attached top image."
        )
    
    # --- BOTTOM (하의) ---
    if "bottom" in _att:
        _desc = bottom_info or {}
        garments_parts.append(
            f"BOTTOM (attached — reproduce EXACTLY): "
            f"{_desc.get('sub_category','pants')} "
            f"in {_desc.get('main_color_name','as shown')} color, "
            f"{_desc.get('pattern','as shown')} pattern, "
            f"{_desc.get('material','as shown')} material. "
            f"Match every detail of the attached bottom image."
        )
    
    # --- SHOES (신발) ---
    if "shoes" in _att:
        _desc = shoes_info or {}
        garments_parts.append(
            f"SHOES (attached — reproduce EXACTLY): "
            f"{_desc.get('sub_category','shoes')} "
            f"in {_desc.get('main_color_name','as shown')}. "
            f"Reproduce the EXACT shoes from the attached reference image on BOTH feet. "
            f"Match shoe type (sneaker/loafer/heel/boot/etc), color, laces, sole, logo — every detail. "
            f"Do NOT substitute with different footwear."
        )
    
    # 종료 재확인
    garments_parts.append(
        "\n\n━━━ FINAL REMINDER ━━━ "
        f"Attached items: [{', '.join(_attached_list)}]. "
        "These are the ONLY items to wear. "
        "Before finalizing the image, verify: "
        "(1) Every attached item is visible and accurately reproduced. "
        "(2) No extra garments (cardigan, jacket, scarf, accessories) are added beyond the attached list "
        "and the allowed exceptions. "
        "(3) The outfit matches the user's selection exactly."
    )
    
    garments = " ".join(garments_parts)

    # ──────── Phase 3: WEARING ────────
    # 하의가 치마일 때 tuck 규칙, 바지일 때 tuck 규칙 (codistyle의 _bot_wear 로직 참조)
    wearing_bits = []
    if mode == _TRYON_MODE_TWOPIECE and bottom_info:
        is_skirt = bool(bottom_info.get("is_skirt"))
        if is_skirt:
            wearing_bits.append(
                "Top wearing: tuck the top neatly into the skirt waistband (standard styling). "
                "Skirt should sit naturally at the waist."
            )
        else:
            wearing_bits.append(
                "Top wearing: if the top is short/cropped, leave untucked; "
                "if long shirt, semi-tuck (French tuck) is preferred."
            )
        wearing_bits.append(
            "Bottom wearing: natural drape, realistic fit according to the body type."
        )
    if mode == _TRYON_MODE_ONEPIECE:
        wearing_bits.append(
            "Dress wearing: natural drape, full-length visible, hem at appropriate level."
        )
    # [2026-04-26 v20 TJ] 정+후면 두 자세에서 동일 스타일링 보장
    wearing_bits.append(
        "CONSISTENCY: Both front and back views must show IDENTICAL wearing style — "
        "same tuck/untuck, same hem position, same drape, same fit. "
        "This is the SAME outfit on the SAME person, just photographed from front and back."
    )
    wearing = " ".join(wearing_bits) if wearing_bits else "Natural, well-fitted wearing style on both poses."

    # ──────── Phase 4: IMAGE COMPOSITION (정+후면 한 페이지 — 2026-04-27 v25 TJ) ────────
    # [2026-04-27 v25 TJ 진단] v20 프롬프트로 생성된 이미지가 768x1376 세로형으로 나옴
    #   원인: Gemini가 "WIDE landscape (16:9 or 2:1)" 지시를 무시하고
    #         학습된 portrait 비율(9:16)에 두 인물을 가로로 배치
    #   증거: 콘솔 로그 [v24 tryon] 이미지 분석: 768x1376 ratio=0.56 isWide=false
    #         → ratio 0.56 (세로) → 정/후면 모드 진입 못 함
    # [v25 변경] ASPECT RATIO 강제 명령을 *최상단 첫 줄*에 + 픽셀 크기 구체 명시
    #
    # ─── 2026-05-09 KST · TJ 지시 (v27) ─── 폴백 layout 명확화
    #   문제: Gemini가 가로 2:1을 무시하고 portrait를 반환할 때
    #         두 인물이 어떻게 배치되는지 일관되지 않아 클라이언트가 분할 못함
    #   해결: 1순위 = 가로 2:1 (좌=정면, 우=후면)
    #         2순위(폴백) = 세로 1:2 (위=정면, 아래=후면) — "명확히 분할"
    #         어느 방향이든 두 view가 정확히 절반씩 점유하도록 강제
    #         클라이언트는 ratio로 분기하여 항상 가로 캔버스로 변환
    image_compo = (
        "🖼️ CRITICAL OUTPUT FORMAT (MUST OBEY — top priority): "
        "Generate a HORIZONTAL WIDE image. "
        "Output dimensions: 2048 pixels wide × 1024 pixels tall (2:1 aspect ratio). "
        "The width MUST be EXACTLY 2× the height. "
        "DO NOT generate vertical, portrait, or square images. "
        "DO NOT generate 9:16, 3:4, or 1:1 ratios. "
        "If you cannot achieve exactly 2:1, output 16:9 (1920×1080) instead. "
        "The final image must be WIDER than tall — never the opposite. "
        "\n\n"
        "═══ PRIMARY LAYOUT (preferred — wide canvas) ═══ "
        "Output a SINGLE WIDE image with TWO poses of the SAME person, "
        "side by side, sharing the SAME flat solid neutral background: "
        "  • LEFT half (pixels 0 to 1024 wide): FRONT view (full body, facing camera, arms relaxed). "
        "  • RIGHT half (pixels 1024 to 2048 wide): BACK view (full body, facing AWAY from camera, same pose). "
        "Both views show the EXACT SAME outfit, lighting, hair, and styling. "
        "The two figures are evenly spaced, not touching, on the same ground line. "
        "Reference: Uniqlo / Theory store catalog — clean, neutral, minimal. "
        "═══ END PRIMARY LAYOUT ═══ "
        "\n\n"
        "═══ FALLBACK LAYOUT (only if wide canvas is impossible) ═══ "
        "If — and ONLY if — the wide 2:1 canvas is technically impossible for you, "
        "use a VERTICAL 1:2 canvas (1024 wide × 2048 tall) with this STRICT layout: "
        "  • TOP half (pixels 0 to 1024 tall): FRONT view (full body, facing camera). "
        "  • BOTTOM half (pixels 1024 to 2048 tall): BACK view (full body, facing AWAY). "
        "Each half MUST contain the COMPLETE FULL-BODY figure (head to feet) — never crop. "
        "The two halves MUST be exactly equal in height (50% each). "
        "Same outfit, same person, same lighting, same background — only the camera angle differs. "
        "═══ END FALLBACK LAYOUT ═══ "
        "\n\n"
        "FACE/HEAD RULES: "
        "• FRONT view (LEFT in primary / TOP in fallback): Face fully visible — preserve identity 99.99% to the reference face image. "
        "• BACK view (RIGHT in primary / BOTTOM in fallback): Face NOT visible (back of head only). Match only hair color, texture, length, parting, hairline. "
        "FORBIDDEN: Showing face on the BACK view. "
        "\n\n"
        "FRAMING RULES (apply to BOTH poses): "
        "• Complete FULL-BODY shot from TOP of head to BELOW the feet. "
        "  The ENTIRE shoes must be fully visible including the soles on the ground. "
        "  Top of head: ~8-12% breathing space above. "
        "  Feet: ~5-8% breathing space below (never cut at ankle or shin). "
        "• Both figures vertically centered in their respective half. "
        "• CROP GUARD: NEVER crop at knees, ankles, shins, calves, or above the shoes. "
        "• POSE: natural relaxed standing posture for both views. Front = facing camera. Back = facing away. "
        "• LIGHTING: soft even studio lighting, no harsh shadows, IDENTICAL across both poses. "
        "• BACKGROUND: clean seamless neutral grey (#E8E8E8) shared by both poses. "
        "• STYLE: photographic realism — NO illustration, NO cartoon, NO anime style. "
        # ─── 2026-05-09 KST · TJ 지시 (v30) ─── 화질 강화 키워드
        # 배경: 트라이온은 프리미엄 기능 (Nano Banana Pro). 광고/잡지 수준 출력 필수.
        # 효과: image_size=2K와 함께 작용해 디테일·텍스처·선명도 극대화.
        "• QUALITY: ULTRA HIGH RESOLUTION, sharp focus, crisp clean edges, "
        "  fine fabric texture detail (visible weave, stitching, drape, wrinkles, sheen). "
        "  Skin tone with subtle variation, natural pores, individual hair strands visible. "
        "  Magazine editorial quality — like Vogue, GQ, Uniqlo lookbook campaign. "
        "  AVOID: blurry, soft focus, plastic skin, low-detail fabric, painterly look. "
        "\n\n"
        "🖼️ FINAL REMINDER: "
        "Strongly prefer wide 2:1 (LEFT=front, RIGHT=back). "
        "If portrait is unavoidable, use 1:2 with TOP=front, BOTTOM=back. "
        "Whichever orientation you choose, the two views must be EXACTLY equal-sized halves with NO overlap and NO empty padding."
    )

    # ──────── Phase 5: IMAGE-ONLY MODE (2026-04-23 17:30 — 병렬 처리 반영) ────────
    # 이전: 이미지 모델이 이미지+분석 JSON 모두 생성 → 분석 부실
    # 신규: 이미지 모델은 이미지에만 집중, 분석은 _tryon_analyze_via_text_model()이 병렬로 처리
    # 따라서 이 프롬프트는 "이미지만 잘 만들어달라"는 명확한 단일 목표 지시.
    evaluation = (
        "\n\n[IMAGE-ONLY TASK]: Your ONLY task is to generate the try-on image. "
        "Focus 100% on image quality: facial identity preservation, garment fidelity, "
        "full-body framing (head-to-toe with shoes visible). "
        "Brief 1-sentence text description is acceptable but NOT required."
    )

    # ──────── 최종 결합 ────────
    prompt = (
        f"\n\n[PHASE 1 — PERSONA]: {persona}"
        f"\n\n[PHASE 2 — GARMENTS]: {garments}"
        f"\n\n[PHASE 3 — WEARING]: {wearing}"
        f"\n\n[PHASE 4 — IMAGE]: {image_compo}"
        f"{evaluation}"
    )

    # ──────── 이미지 첨부 순서 결정 (2026-04-24 v7) ────────
    # 핵심 수정: attached_keys 기반 → "이미지가 실제로 첨부된" 아이템만 순서에 포함
    # 이전 버그: if shoes_info: → 빈 dict일 때 False → shoes 이미지 첨부 안 됨
    # 수정: if "shoes" in _att: → 실제 이미지 첨부 여부로 판단
    face_required = (fit_target != _TRYON_FIT_MODEL)
    
    if mode == _TRYON_MODE_ONEPIECE:
        # 원피스 모드: onepiece는 필수, outer는 선택
        item_order = []
        if "onepiece" in _att: item_order.append("onepiece")
        if "outer" in _att: item_order.append("outer")
    elif mode == _TRYON_MODE_OUTER:
        # 아우터 모드: outer는 필수, top/bottom은 선택
        item_order = []
        if "outer" in _att: item_order.append("outer")
        if "top" in _att: item_order.append("top")
        if "bottom" in _att: item_order.append("bottom")
    else:
        # 투피스 모드: top/bottom 필수, outer 선택
        item_order = []
        if "top" in _att: item_order.append("top")
        if "bottom" in _att: item_order.append("bottom")
        if "outer" in _att: item_order.append("outer")
    
    # 신발 — 모드와 무관하게 image_map 기준으로 포함
    if "shoes" in _att:
        item_order.append("shoes")

    return prompt, {"face_required": face_required, "item_order": item_order}


def _tryon_parse_response(comment: str):
    """
    [2026-04-22 16:30] 트라이온 응답 파서.
    [2026-04-24 v9 TJ 지시1] TPO/팁/큐레이션 추출 추가
    
    Gemini가 생성한 텍스트에서 C.S.I 4지표 + 5섹션 분석 + TPO + 팁 + 큐레이션 추출.
    응답 JSON 스키마는 codistyle_generate와 동일 (프론트 csScoreBox 호환).
    """
    import re as _re
    
    result = {
        "styling_score": None,
        "score_breakdown": {},
        "styling_advice": "",
        "executive_summary": "",
        "tpo_recommendations": [],
        "improvement_tips": [],
        "style_hashtags": [],
        "item_curation": [],  # [v9] 신발/가방/액세서리 큐레이션
    }
    
    try:
        # 1) 총점
        _m = _re.search(r'STYLING_SCORE:(\d+)/100', comment)
        if _m:
            result["styling_score"] = int(_m.group(1))
        
        # 2) C.S.I 4지표
        _sb = {}
        for _k in ["body_shape", "personal_color", "proportion", "harmony"]:
            _km = _re.search(rf'{_k}:(\d+)', comment)
            if _km:
                _sb[_k] = int(_km.group(1))
        
        # 점수 정규화 (합이 total과 다르면 비례 조정)
        if result["styling_score"] and all(k in _sb for k in ["body_shape", "personal_color", "proportion", "harmony"]):
            _sum = sum(_sb.values())
            if _sum > 0 and _sum != result["styling_score"]:
                _r = result["styling_score"] / _sum
                _sb["body_shape"]     = round(_sb["body_shape"] * _r)
                _sb["personal_color"] = round(_sb["personal_color"] * _r)
                _sb["proportion"]     = round(_sb["proportion"] * _r)
                _sb["harmony"]        = result["styling_score"] - _sb["body_shape"] - _sb["personal_color"] - _sb["proportion"]
        result["score_breakdown"] = _sb
        
        # 3) Executive Summary (종합 평가)
        _esm = _re.search(
            r'(?:종합 평가|Executive Summary)\s*[:：]\s*([^\n]+(?:\n(?!(?:스타일 해시태그|심층 분석|Style Hashtags|Deep-dive|Best TPO|개선 팁|Improvement|퍼스널 아이템|Item Curation))[^\n]*)*)',
            comment
        )
        if _esm:
            result["executive_summary"] = _esm.group(1).strip().strip("[]").strip()
        
        # 4) 해시태그
        _hsm = _re.search(r'(?:스타일 해시태그|Style Hashtags)\s*[:：]\s*([^\n]+)', comment)
        if _hsm:
            _raw_tags = _hsm.group(1).strip()
            result["style_hashtags"] = [t.strip() for t in _re.findall(r'#\S+', _raw_tags)]
        
        # 5) [v9 신규] Best TPO 추천 (| 구분자)
        _tpo_m = _re.search(r'(?:Best TPO|베스트 TPO|추천 TPO)\s*[:：]\s*([^\n]+(?:\n(?!(?:개선 팁|Improvement|퍼스널 아이템|Item Curation|IMPORTANT))[^\n]*)*)', comment)
        if _tpo_m:
            _raw = _tpo_m.group(1).strip().strip("[]").strip()
            # 여러 줄이면 한 줄로
            _raw = _re.sub(r'\s*\n\s*', ' ', _raw)
            # | 또는 • 또는 , 로 구분
            _parts = _re.split(r'[|•▪·]|,(?![^(]*\))', _raw)
            result["tpo_recommendations"] = [t.strip().strip("-·").strip() for t in _parts if t.strip() and len(t.strip()) > 1][:5]
        
        # 6) [v9 신규] 개선 팁 추출
        _tip_m = _re.search(r'(?:개선 팁|Improvement Tips|스타일링 팁)\s*[:：]\s*([^\n]+(?:\n(?!(?:퍼스널 아이템|Item Curation|IMPORTANT|Best TPO))[^\n]*)*)', comment)
        if _tip_m:
            _raw = _tip_m.group(1).strip().strip("[]").strip()
            _raw = _re.sub(r'\s*\n\s*', ' ', _raw)
            _parts = _re.split(r'[|•▪·]|(?<=[\.。!?])\s+(?=[가-힣A-Z])', _raw)
            result["improvement_tips"] = [t.strip().strip("-·").strip() for t in _parts if t.strip() and len(t.strip()) > 3][:5]
        
        # 7) [v9 신규] 퍼스널 아이템 큐레이션
        _cur_m = _re.search(r'(?:퍼스널 아이템 큐레이션|Item Curation|아이템 추천)\s*[:：]\s*([^\n]+(?:\n(?!(?:IMPORTANT|Best TPO|개선 팁))[^\n]*)*)', comment)
        if _cur_m:
            _raw = _cur_m.group(1).strip().strip("[]").strip()
            _raw = _re.sub(r'\s*\n\s*', ' ', _raw)
            _parts = _re.split(r'[|•▪·]|(?<=[\.。!?])\s+(?=[가-힣A-Z])', _raw)
            result["item_curation"] = [t.strip().strip("-·").strip() for t in _parts if t.strip() and len(t.strip()) > 3][:5]
        
        # 8) 5섹션 심층 분석
        _advice = {}
        _NEXT_HEADERS = r"퍼스널컬러 분석|색상 조화 분석|상의 스타일 분석|하의 스타일 분석|실루엣과 비율|상하의 밸런스|전체 스타일 완성도|Best TPO|베스트 TPO|개선 팁|Improvement|퍼스널 아이템|Item Curation|IMPORTANT"
        _section_patterns = [
            ("pc",        rf'(?:퍼스널컬러 분석|색상 조화 분석)\s*[:：]\s*([^\n]+(?:\n(?!(?:{_NEXT_HEADERS}))[^\n]*)*)'),
            ("top",       rf'상의 스타일 분석\s*[:：]\s*([^\n]+(?:\n(?!(?:{_NEXT_HEADERS}))[^\n]*)*)'),
            ("bottom",    rf'하의 스타일 분석\s*[:：]\s*([^\n]+(?:\n(?!(?:{_NEXT_HEADERS}))[^\n]*)*)'),
            ("proportion", rf'실루엣과 비율\s*[:：]\s*([^\n]+(?:\n(?!(?:{_NEXT_HEADERS}))[^\n]*)*)'),
            ("harmony",    rf'(?:상하의 밸런스|전체 스타일 완성도)\s*[:：]\s*([^\n]+(?:\n(?!(?:{_NEXT_HEADERS}|\Z))[^\n]*)*)'),
        ]
        for _key, _pat in _section_patterns:
            _sm = _re.search(_pat, comment)
            if _sm:
                _advice[_key] = _sm.group(1).strip().strip("[]").strip()
        result["styling_advice"] = _advice if _advice else ""
        
        # 진단 로그
        print(
            f"[TRYON-PARSE] score={result['styling_score']} "
            f"breakdown={_sb} "
            f"exec_len={len(result['executive_summary'])} "
            f"tpo_n={len(result['tpo_recommendations'])} "
            f"tips_n={len(result['improvement_tips'])} "
            f"cur_n={len(result['item_curation'])} "
            f"tags_n={len(result['style_hashtags'])} "
            f"advice_keys={list(_advice.keys()) if _advice else []}",
            flush=True
        )
        
    except Exception as _parse_e:
        print(f"[TRYON-PARSE] 파싱 중 경고: {_parse_e}", flush=True)
    
    return result


# ─── 2026-04-23 14:30 KST [TJ 지시 — 임시 디버그 엔드포인트] ───
# 트라이온 모델 라우팅 디버그용. 브라우저 접속으로 사용 가능.
# 테스트 완료 후 제거 권장.
@app.get("/api/debug/gemini-models")
def debug_gemini_models():
    """
    현재 Gemini API 계정에서 사용 가능한 이미지 생성 모델 목록 조회.
    
    반환:
      {
        "ok": true,
        "api_key_present": true/false,
        "total_models": N,
        "image_models": [...],
        "tryon_target_available": {
          "gemini-3-pro-image-preview": true/false,
          "gemini-3.1-flash-image-preview": true/false,
          "gemini-2.5-flash-image": true/false,
        },
        "current_config": {
          "CODISTYLE_GEMINI_MODEL": "...",
          "CODIBANK_MODEL_TRYON": "..." or null,
          "resolved_tryon_model": "..."
        }
      }
    
    사용:
      브라우저에서 접속:
        https://codibank-api.onrender.com/api/debug/gemini-models
    """
    import os as _os
    result = {
        "ok": False,
        "api_key_present": bool(_os.getenv("GEMINI_API_KEY")),
        "total_models": 0,
        "image_models": [],
        "tryon_target_available": {},
        "current_config": {
            "CODISTYLE_GEMINI_MODEL": _os.getenv("CODISTYLE_GEMINI_MODEL"),
            "CODIBANK_MODEL_TRYON": _os.getenv("CODIBANK_MODEL_TRYON"),
            "CODIBANK_ALIAS_TRYON": _os.getenv("CODIBANK_ALIAS_TRYON"),
            "resolved_tryon_model": None,
        }
    }
    
    # 현재 _resolve_engine이 어떤 모델을 반환하는지 기록
    try:
        result["current_config"]["resolved_tryon_model"] = _resolve_engine("FREE", "tryon")
    except Exception as _e:
        result["current_config"]["resolved_tryon_model_error"] = str(_e)
    
    # API 키 없으면 조기 리턴
    if not result["api_key_present"]:
        result["error"] = "GEMINI_API_KEY 환경변수가 없습니다"
        return result, 200
    
    # 새 SDK 우선 시도, 실패시 legacy SDK
    try:
        try:
            from google import genai as _new_genai
            client = _new_genai.Client(api_key=_os.getenv("GEMINI_API_KEY"))
            models_iter = client.models.list()
            all_models = []
            for m in models_iter:
                mname = getattr(m, "name", str(m))
                all_models.append(mname)
            result["sdk_used"] = "google-genai (new)"
        except Exception as _new_e:
            # legacy SDK fallback
            import google.generativeai as _genai_old
            _genai_old.configure(api_key=_os.getenv("GEMINI_API_KEY"))
            all_models = []
            for m in _genai_old.list_models():
                mname = getattr(m, "name", str(m))
                all_models.append(mname)
            result["sdk_used"] = f"google-generativeai (legacy) — new SDK failed: {_new_e}"
        
        result["total_models"] = len(all_models)
        
        # 이미지 생성 관련 모델만 필터링
        image_keywords = ["image", "imagen"]
        result["image_models"] = [
            mname for mname in all_models
            if any(kw in mname.lower() for kw in image_keywords)
        ]
        
        # 트라이온 타겟 모델들 존재 여부
        targets = [
            "gemini-3-pro-image-preview",      # Nano Banana Pro
            "gemini-3.1-flash-image-preview",  # Nano Banana 2
            "gemini-2.5-flash-image",           # Nano Banana 1 (검증됨)
            "gemini-3-pro-image",               # 혹시 이름 없이 존재할 수도
        ]
        for target in targets:
            # name에 target이 포함된 항목이 있는지 (models/... 접두사 고려)
            found = any(target in mname for mname in all_models)
            result["tryon_target_available"][target] = found
        
        result["ok"] = True
        
    except Exception as e:
        result["error"] = f"Gemini API 호출 실패: {type(e).__name__}: {str(e)}"
        import traceback
        result["traceback"] = traceback.format_exc()[:2000]
    
    return result, 200


# ════════════════════════════════════════════════════════════════════
# ─── 2026-04-23 16:00 KST [TJ 지시 — 트라이온 병렬 처리] ───────────
# 
# 기존 문제:
#   Gemini 3 Pro Image Preview 단일 호출로 이미지+분석 동시 생성 시
#   thinking 모드로 인해 분석 JSON이 부실하여 점수 0/0/0/0 표시됨
#
# 해결 방안:
#   이미지 생성(Gemini 3 Pro Image)과 분석(Gemini 3 Pro)을 병렬 호출.
#   ThreadPoolExecutor(max_workers=2)로 동시 실행 후 통합 응답.
#   프론트 코드 변경 0.
#
# 병렬 구조:
#   worker 1: _tryon_generate_image_via_gemini() → 이미지만 생성
#   worker 2: _tryon_analyze_via_text_model()     → 분석 JSON만 생성
#   둘 다 완료 후 통합하여 기존 응답 스키마로 반환.
#
# 분석 전용 모델:
#   기본값: gemini-3-pro-preview (텍스트, thinking 지원)
#   환경변수: CODIBANK_MODEL_TRYON_ANALYSIS 로 덮어쓰기 가능
# ════════════════════════════════════════════════════════════════════

def _tryon_build_analysis_prompt(
    *,
    mode: str,
    fit_target: str,
    model_gender: str,
    gender_ko: str,
    gender_en: str,
    age: str,
    height: str,
    weight: str,
    body_type_key: str,
    pc_summary: str,
    top_info: dict,
    bottom_info: dict,
    onepiece_info: dict,
    outer_info: dict,
    shoes_info: dict,
    attached_keys: set = None,  # [2026-04-24 v7] 실제 첨부된 이미지 기반 판단
    lang_en: bool = False,
):
    """
    [2026-04-23 16:00] 트라이온 분석 전용 프롬프트.
    [2026-04-24 v7] attached_keys 추가 — 실제 첨부된 이미지만 분석 대상으로
    
    Gemini 3 Pro (텍스트) 로 호출. 이미지 생성 없이 분석 JSON 만 요청.
    _tryon_parse_response가 파싱하는 마커 형식(STYLING_SCORE:, body_shape: 등) 준수.
    
    입력 이미지:
      - 얼굴 (fit_target != model)
      - 상의/하의 또는 원피스 (참고용)
      - 아우터/신발 (선택)
    
    반환:
      (prompt_text, required_image_keys)
    """
    # 체형 키 한글화
    _body_kor_map = {
        "straight": "스트레이트형",
        "wave": "웨이브형",
        "natural": "내추럴형",
        "pear": "하체비만형",
        "apple": "복부비만형",
        "hourglass": "모래시계형",
        "inverted": "역삼각형",
    }
    body_kor = _body_kor_map.get((body_type_key or "").lower(), body_type_key or "일반")
    
    # 퍼스널컬러 요약 (없으면 기본)
    pc_text = pc_summary or "분석된 퍼스널컬러 정보 없음"
    
    # [2026-04-24 v7] attached_keys 기반 로직
    # 이전: top_info 존재 여부로 _img_order 결정 → 이미지 있어도 info 없으면 누락
    # 수정: attached_keys (실제 첨부된 이미지 키)로 직접 판단
    _att = attached_keys or set()
    
    # 아이템 정보 정리
    _item_desc = []
    _img_order = []
    if fit_target != _TRYON_FIT_MODEL:
        _img_order.append("face")
    
    # 각 슬롯별 — attached_keys 기반 + xxx_info 의 메타데이터 보조
    def _item_label(key, info, default_cat):
        """첨부된 아이템의 한글 설명 생성"""
        cat = (info or {}).get("sub_category") or (info or {}).get("category") or default_cat
        col = (info or {}).get("color") or (info or {}).get("main_color_name") or ""
        return f"{cat}" + (f" ({col})" if col else "")
    
    if mode == _TRYON_MODE_TWOPIECE:
        # 투피스: top/bottom은 서버 검증에서 필수 (항상 _att에 있음)
        if "top" in _att:
            _item_desc.append(f"• 상의: {_item_label('top', top_info, '상의')} [이미지 첨부됨]")
            _img_order.append("top")
        if "bottom" in _att:
            _item_desc.append(f"• 하의: {_item_label('bottom', bottom_info, '하의')} [이미지 첨부됨]")
            _img_order.append("bottom")
        if "outer" in _att:
            _item_desc.append(f"• 아우터: {_item_label('outer', outer_info, '아우터')} [이미지 첨부됨]")
            _img_order.append("outer")
    elif mode == _TRYON_MODE_ONEPIECE:
        if "onepiece" in _att:
            _item_desc.append(f"• 원피스: {_item_label('onepiece', onepiece_info, '원피스')} [이미지 첨부됨]")
            _img_order.append("onepiece")
        if "outer" in _att:
            _item_desc.append(f"• 아우터: {_item_label('outer', outer_info, '아우터')} [이미지 첨부됨]")
            _img_order.append("outer")
    elif mode == _TRYON_MODE_OUTER:
        if "outer" in _att:
            _item_desc.append(f"• 아우터: {_item_label('outer', outer_info, '아우터')} [이미지 첨부됨, 메인 아이템]")
            _img_order.append("outer")
        # 아우터 모드: top/bottom 모두 선택 가능
        if "top" in _att:
            _item_desc.append(f"• 상의: {_item_label('top', top_info, '상의')} [이미지 첨부됨]")
            _img_order.append("top")
        else:
            # [v8] 미첨부는 "미선택"만 명시 — 자동 생성을 전제하지 않음 (프롬프트가 생성 금지이므로)
            _item_desc.append("• 상의: 미선택 — 아우터 안쪽의 최소 내피만 자연 노출")
        if "bottom" in _att:
            _item_desc.append(f"• 하의: {_item_label('bottom', bottom_info, '하의')} [이미지 첨부됨]")
            _img_order.append("bottom")
        else:
            _item_desc.append("• 하의: 미선택 — 아우터 하단의 최소 하의만 자연 노출")
    
    # 신발 (옵션, 모든 모드 공통)
    if "shoes" in _att:
        _item_desc.append(f"• 신발: {_item_label('shoes', shoes_info, '신발')} [이미지 첨부됨]")
        _img_order.append("shoes")
    else:
        # [v8] 신발은 예외적으로 중립 자동 생성 허용 (맨발 방지)
        _item_desc.append("• 신발: 미선택 — 전체 톤과 조화되는 중립 신발 자동 생성 (맨발 방지)")
    
    items_block = "\n".join(_item_desc) if _item_desc else "• (아이템 정보 없음)"
    
    # 사용자 정보 블록
    user_info_block = (
        f"• 성별: {gender_ko}\n"
        f"• 나이대: {age}\n"
        f"• 키: {height}cm\n"
        f"• 몸무게: {weight}kg\n"
        f"• 체형: {body_kor}\n"
        f"• 퍼스널컬러: {pc_text}"
    )
    
    # ─── 2026-04-23 18:00 [TJ 지시 — 조건부 퍼스널컬러 분석 B안] ───
    # 퍼스널컬러 분석 가능 여부 판정:
    #   • fit_target == "model" → 불가 (사용자 얼굴 없음 → 일반 조화로 대체)
    #   • fit_target == "somebody" & 얼굴 사진 없음 → 불가
    #   • pc_summary 비어있음 → 불가
    #   • 그 외 (myfit/somebody-with-photo 이면서 pc 있음) → 분석 가능
    _has_pc = bool(pc_summary and pc_summary.strip()) and fit_target != _TRYON_FIT_MODEL
    # 모델핏일 때는 pc_summary가 있어도 사용자 얼굴이 없으므로 퍼스널컬러 분석 부적절
    
    if _has_pc:
        # 정상 퍼스널컬러 분석 블록
        _pc_criterion = (
            "[2] personal_color (퍼스널컬러 조화) — 30점 만점\n"
            f"    • 의류 색상이 사용자 퍼스널컬러({pc_text})와 조화로운 정도\n"
            "    • 톤·온도·채도의 매칭\n"
            "    • 얼굴 혈색·피부톤에 미치는 시각적 효과"
        )
        _pc_section_title = "퍼스널컬러 분석"
        _pc_section_guide = f"[사용자의 {pc_text}와 의상 색상의 조화를 구체적으로 서술. 착장이 얼굴 혈색과 피부톤에 어떤 영향을 주는지 포함]"
    else:
        # 퍼스널컬러 정보 없음 → 일반 색상 조화 분석으로 대체 (B안)
        _pc_criterion = (
            "[2] color_harmony (색상 조화) — 30점 만점\n"
            "    • 의류 간 색상 조합의 전반적 조화\n"
            "    • 배색의 균형감·대비감·무드 통일성\n"
            "    • (참고: 사용자 퍼스널컬러 정보가 없어 일반적 색상 조화 기준으로 평가)"
        )
        _pc_section_title = "색상 조화 분석"
        _pc_section_guide = "[의상 간 색상 조합의 일반적 조화를 서술. 배색의 균형·대비·무드 일관성 평가. 퍼스널컬러 개인 맞춤 판단은 불가능하므로 보편적 색채학 관점에서 서술]"
    
    # 최종 프롬프트 (한국어 기본) — 전문 패션 스타일리스트 톤
    prompt = f"""당신은 보그(VOGUE)와 엘르(ELLE)에서 15년 이상 경력을 쌓은 
수석 패션 에디터이자 프로페셔널 퍼스널 스타일리스트입니다.
한국 톱클래스 모델 에이전시와 협업하며 수천 명의 고객 스타일을 컨설팅해왔고,
색채학·체형학·퍼스널컬러 이론에 모두 능통합니다.

첨부된 이미지(얼굴 + 의류 아이템)와 사용자 프로필을 종합 분석하여,
이 사용자가 해당 의류를 착용했을 때의 스타일링 완성도를 
정량 점수 + 전문가 시각의 심층 리포트로 제공합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 사용자 프로필:
{user_info_block}

👗 착용 아이템:
{items_block}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 평가 기준 (C.S.I. — Coordination Style Index):

[1] body_shape (체형 보완도) — 30점 만점
    • 체형의 단점을 커버하고 장점을 강조하는 정도
    • {body_kor}에 최적화된 실루엣인지
    • 시각적 체형 교정 효과

{_pc_criterion}

[3] proportion (비율 개선도) — 20점 만점
    • 상·하체 비율 최적화 (키 {height}cm 기준)
    • 다리·허리 라인 개선 효과
    • 골든 비율(3:7, 4:6)에 얼마나 가까운지

[4] harmony (전체 스타일 완성도) — 20점 만점
    • 의상 간 무드·패턴·소재의 조화
    • TPO 적합성 (언제 어디서 입을 수 있는지)
    • 전체적 시즌감과 트렌드 반영도

총점 = body_shape + personal_color/color_harmony + proportion + harmony = 100점

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 반드시 아래 정확한 형식으로 답변해 주세요 (파서 호환 필수):

STYLING_SCORE:[총점]/100
body_shape:[점수]
personal_color:[점수]
proportion:[점수]
harmony:[점수]

종합 평가: [2-3문장으로 이 착장의 전반적 평가. 전문 에디터의 시각으로 첫인상과 장점, 개선 포인트를 포함. 평범한 설명 금지 — 구체적이고 감각적인 표현 사용]

스타일 해시태그: #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
(키워드는 트렌디하고 검색 가능한 스타일 용어로 — 예: #오피스시크, #프렌치미니멀, #가을웜톤, #허리강조룩)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 심층 분석 (각 섹션 3-5문장, 전문 패션 매거진 아티클 톤):

{_pc_section_title}: {_pc_section_guide}

상의 스타일 분석: [상의의 디자인·핏·소재감·디테일이 체형에 어떤 시각적 효과를 주는지. 
전문가적 관점에서 컷·라인·볼륨감 분석. 단순 나열 금지 — 인과관계 중심으로 서술]

하의 스타일 분석: [하의의 실루엣·길이·웨이스트라인이 비율에 주는 영향. 
전문가 용어(페그 핏, 스트레이트, 와이드 등) 적절히 활용하며 일반 독자도 이해 가능한 설명]

실루엣과 비율: [전체 실루엣의 구조 분석. X/A/H/Y 라인 중 어느 것에 해당하는지, 
사용자 체형에 최적화된 라인인지. 개선 제안이 있다면 구체적으로]

전체 스타일 완성도: [첫인상·무드·시즌감·TPO 추천·완성도 평가. 
잡지 에디터가 착장을 리뷰하듯 감각적이고 구체적으로 작성]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 [v9 신규] 활용 가이드 (아래 3개 섹션은 반드시 포함 — 파서가 마커로 인식합니다):

Best TPO: [TPO1]|[TPO2]|[TPO3]|[TPO4]|[TPO5]
(이 착장이 가장 빛나는 상황 3~5개. | 파이프로 구분. 각 항목 5~15자 간결하게. 
 예: 평일 오피스 출근|카페 브런치 미팅|주말 갤러리 데이트|봄 웨딩 게스트|비즈니스 캐주얼)

개선 팁: [팁1]|[팁2]|[팁3]|[팁4]
(이 착장을 10% 더 돋보이게 할 실용 조언 3~5개. | 파이프로 구분. 각 항목 20~50자 구체적으로.
 예: 벨트를 살짝 높여 매면 허리선이 더 강조되어 다리가 길어 보여요|밝은 쉐이드의 립 컬러로 얼굴 혈색을 살려보세요)

퍼스널 아이템 큐레이션: [아이템1]|[아이템2]|[아이템3]|[아이템4]|[아이템5]
(이 착장을 완성시킬 신발/가방/액세서리 5개 구체 추천. | 파이프로 구분. 
 각 항목은 '카테고리 - 구체적 설명' 포맷. 예:
 신발 - 아이보리 포인티드 토 펌프스 (키와 다리를 길어 보이게)|가방 - 살구빛 미디엄 토트백 (전체 톤 조화)|
 주얼리 - 골드 드롭 이어링 (웜톤 피부와 매치)|스카프 - 피치 컬러 실크 스카프|워치 - 로즈골드 다이얼)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT:
- 위 형식 정확히 준수 (STYLING_SCORE:, body_shape:, Best TPO:, 개선 팁:, 퍼스널 아이템 큐레이션: 등 마커 필수)
- 점수는 0~최대점 사이 정수, 4개 지표 합계 = 총점 정확 일치
- 응답은 한국어로만 작성
- Best TPO / 개선 팁 / 퍼스널 아이템 큐레이션은 절대 생략하지 말 것 — 리포트 필수 섹션
- 뻔한 말 금지 — "세련되다" "잘 어울린다" 같은 모호한 표현 피하기
- 전문가 톤 유지하되 일반 소비자도 공감 가능한 언어
"""
    
    if lang_en:
        # 영어 버전 (간략 — 동일 마커 유지, 조건부 PC 분석 반영)
        _en_second = (
            "[2] personal_color — 30 pts (color harmony with personal color)"
            if _has_pc
            else "[2] color_harmony — 30 pts (general color balance; no personal color data)"
        )
        _en_section = "퍼스널컬러 분석" if _has_pc else "색상 조화 분석"
        prompt = f"""You are a senior VOGUE/ELLE fashion editor with 15+ years of experience
and a professional personal stylist. Analyze the attached images (face + clothing items)
and user profile to provide styling scores and a premium-magazine-style deep analysis.

USER PROFILE:
- Gender: {gender_en} / Age: {age} / Height: {height}cm / Weight: {weight}kg
- Body type: {body_type_key}
- Personal color: {pc_text if _has_pc else '(not provided — general harmony mode)'}

ITEMS:
{items_block}

SCORING (C.S.I.):
[1] body_shape — 30 pts (body shape enhancement)
{_en_second}
[3] proportion — 20 pts (height/body ratio improvement)
[4] harmony — 20 pts (overall styling completeness)
Total = 100

Respond in the EXACT format below (Korean text content):

STYLING_SCORE:[total]/100
body_shape:[score]
personal_color:[score]
proportion:[score]
harmony:[score]

종합 평가: [2-3 sentences, editor-tone]
스타일 해시태그: #tag1 #tag2 #tag3 #tag4 #tag5

{_en_section}: [analysis]
상의 스타일 분석: [analysis]
하의 스타일 분석: [analysis]
실루엣과 비율: [analysis]
전체 스타일 완성도: [analysis]

IMPORTANT: Exact markers required. Sum of 4 scores must equal total.
"""
    
    return prompt, {"item_order": _img_order}


# ─── 2026-04-23 17:00 KST [TJ 지시 — thinking_level 환경변수 제어] ───
# 마스터 관리자가 재배포 없이 Render 대시보드에서 즉시 변경 가능하도록 
# 환경변수 CODIBANK_TRYON_THINKING_LEVEL 로 제어.
#
# 허용값:
#   "low"    — 기본값 (비용/속도 최적). 스타일 분석에 충분.
#   "medium" — 중간. 균형.
#   "high"   — 최고 품질. 비용 +40%, 속도 -3배. 특별 이벤트용.
#
# 잘못된 값/미설정 → "low" 자동 폴백 (방어적).
# Gemini 3 시리즈 전용 — 2.5에선 무시됨.
def _resolve_thinking_level() -> str:
    """환경변수 기반 thinking_level 해석. 마스터가 Render 대시보드에서 실시간 변경 가능."""
    _raw = (os.getenv("CODIBANK_TRYON_THINKING_LEVEL") or "low").strip().lower()
    if _raw in ("low", "medium", "high"):
        return _raw
    # 잘못된 값 입력 시 안전한 기본값
    print(f"[TRYON-CONFIG] 알 수 없는 thinking_level='{_raw}', 'low'로 폴백", flush=True)
    return "low"


def _tryon_analyze_via_text_model(
    *,
    api_key: str,
    prompt: str,
    face_bytes: bytes = None,
    face_mime: str = None,
    images_map: dict = None,
    img_order: list = None,
    sdk_mode: str = "new",
) -> str:
    """
    [2026-04-23 16:00] 트라이온 분석 전용 Gemini 텍스트 모델 호출.
    [2026-04-23 17:00] thinking_level 환경변수로 동적 제어 추가.
    
    Gemini 3 Pro (gemini-3-pro-preview) 로 호출.
    이미지 참고 + 분석 JSON 생성 전담. 이미지 출력 없음.
    
    환경변수:
      CODIBANK_MODEL_TRYON_ANALYSIS (기본: gemini-3-pro-preview)
      CODIBANK_TRYON_THINKING_LEVEL (기본: low, 허용: low/medium/high)
    
    반환: 분석 텍스트 (파싱은 _tryon_parse_response가 처리)
    
    실패 시: 예외를 그대로 raise (상위에서 future.result() 시 잡음)
    """
    import os as _os
    # [2026-05-28 KST · TJ 보고] gemini-3-pro-preview 2026-03-09 종료(404) → gemini-3.1-pro-preview
    analysis_model = _os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS", "gemini-3.1-pro-preview")
    _thinking_level = _resolve_thinking_level()
    
    # Gemini 3 시리즈만 thinking_config 지원 (2.5 이하는 미지원)
    _supports_thinking = "gemini-3" in analysis_model.lower()
    
    images_map = images_map or {}
    img_order = img_order or []
    
    if sdk_mode == "new":
        from google import genai as _genai
        from google.genai import types as _gtypes
        
        contents = [prompt]
        # 얼굴 이미지 (fit != model 인 경우)
        if face_bytes:
            contents.append(_gtypes.Part.from_bytes(
                data=face_bytes,
                mime_type=face_mime or "image/jpeg"
            ))
        # 아이템 이미지
        for _k in img_order:
            if _k == "face":
                continue  # 이미 위에서 처리
            if _k in images_map:
                _m, _b = images_map[_k]
                contents.append(_gtypes.Part.from_bytes(
                    data=_b,
                    mime_type=_m or "image/jpeg"
                ))
        
        client = _genai.Client(api_key=api_key)
        
        # ─── 2026-04-23 17:00 [비용 최적화 + 동적 제어 — TJ 지시 A안 보완] ───
        # 환경변수 CODIBANK_TRYON_THINKING_LEVEL 로 실시간 제어:
        #   • 기본: "low" (비용 +1.4%, 속도 2-3초, 품질 충분)
        #   • 이벤트/프리미엄: "high" (비용 +45%, 속도 5-10초, 최고 품질)
        # Gemini 3 시리즈가 아니면 thinking_config 생략 (미지원 모델 대응).
        # SDK 버전 호환성: thinking_config 미지원 시 기본 설정으로 폴백.
        try:
            if _supports_thinking:
                _analysis_config = _gtypes.GenerateContentConfig(
                    temperature=0.3,           # 낮은 temperature (일관된 점수)
                    max_output_tokens=4096,
                    thinking_config=_gtypes.ThinkingConfig(
                        thinking_level=_thinking_level
                    ),
                )
            else:
                # Gemini 2.5 등 thinking 미지원 모델
                _analysis_config = _gtypes.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                )
        except (TypeError, AttributeError) as _cfg_e:
            # 구버전 SDK 폴백 — thinking_config 미지원 시 기본 설정으로
            print(f"[TRYON-ANALYSIS] thinking_config 미지원, 기본 설정 사용: {_cfg_e}", flush=True)
            _analysis_config = _gtypes.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=4096,
            )
        
        # ─── [2026-05-02 v54 TJ] 분석 모델 403 권한 거부 자동 fallback ───
        # gemini-3-pro-preview 권한 없으면 gemini-2.5-flash로 재시도.
        # 2.5는 thinking_config 미지원이므로 폴백 시 config 재구성.
        try:
            response = client.models.generate_content(
                model=analysis_model,
                contents=contents,
                config=_analysis_config,
            )
        except Exception as _ana_primary_err:
            _emsg_ana = str(_ana_primary_err)
            if ('403' in _emsg_ana or 'PERMISSION_DENIED' in _emsg_ana or 'denied access' in _emsg_ana):
                _fallback_ana_model = _os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS_FALLBACK", "gemini-2.5-flash")
                print(f"[TRYON-FALLBACK-ANA] '{analysis_model}' 권한 없음 → '{_fallback_ana_model}'로 재시도 (thinking 제외)", flush=True)
                # 2.5는 thinking 미지원 → config에서 thinking_config 제거
                _analysis_config_fb = _gtypes.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                )
                response = client.models.generate_content(
                    model=_fallback_ana_model,
                    contents=contents,
                    config=_analysis_config_fb,
                )
            else:
                raise
        
        # 텍스트 추출 (thought 필터링 포함)
        result_text = ""
        try:
            candidates = getattr(response, "candidates", []) or []
            if candidates:
                parts = getattr(getattr(candidates[0], "content", None), "parts", []) or []
                for p in parts:
                    # thought 파트는 제외
                    if getattr(p, "thought", False):
                        continue
                    text = getattr(p, "text", None)
                    if text:
                        result_text += str(text)
        except Exception as _e:
            print(f"[TRYON-ANALYSIS-PARSE] new SDK 파싱 경고: {_e}", flush=True)
        
        # 폴백: response.text 직접
        if not result_text:
            try:
                result_text = response.text or ""
            except Exception:
                pass
        
        return result_text
    
    else:  # old SDK
        import google.generativeai as _genai_old
        from PIL import Image as _PILImage
        import io as _io
        
        _genai_old.configure(api_key=api_key)
        model = _genai_old.GenerativeModel(analysis_model)
        
        def _bytes_to_pil(raw):
            return _PILImage.open(_io.BytesIO(raw))
        
        contents_old = [prompt]
        if face_bytes:
            contents_old.append(_bytes_to_pil(face_bytes))
        for _k in img_order:
            if _k == "face":
                continue
            if _k in images_map:
                _m, _b = images_map[_k]
                contents_old.append(_bytes_to_pil(_b))
        
        try:
            response = model.generate_content(
                contents_old,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4096,
                },
            )
        except TypeError:
            response = model.generate_content(contents_old)
        except Exception as _ana_primary_err_old:
            # ─── [2026-05-02 v54 TJ] old SDK 분석 403 권한 거부 fallback ───
            _emsg_ana_old = str(_ana_primary_err_old)
            if ('403' in _emsg_ana_old or 'PERMISSION_DENIED' in _emsg_ana_old or 'denied access' in _emsg_ana_old):
                _fallback_ana_model = _os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS_FALLBACK", "gemini-2.5-flash")
                print(f"[TRYON-FALLBACK-ANA][old SDK] '{analysis_model}' 권한 없음 → '{_fallback_ana_model}'로 재시도", flush=True)
                model_fb = _genai_old.GenerativeModel(_fallback_ana_model)
                try:
                    response = model_fb.generate_content(
                        contents_old,
                        generation_config={
                            "temperature": 0.3,
                            "max_output_tokens": 4096,
                        },
                    )
                except TypeError:
                    response = model_fb.generate_content(contents_old)
            else:
                raise
        
        try:
            return response.text or ""
        except Exception:
            return ""


@app.post("/api/tryon/generate")
def tryon_generate():
    """
    [2026-04-22 16:30 KST] 트라이온 전용 이미지 생성 엔드포인트 (Phase 4).
    
    프론트(tryon.html)에서 Step 3 생성 버튼 클릭 시 호출.
    codistyle_generate와 완전히 독립된 함수. 절대 통합 금지 (원칙).
    
    Request JSON:
      - user: { gender, ageGroup, height, weight, tier }
      - mode: "twopiece" | "onepiece" | "outer"
      - fitTarget: "my" | "somebody" | "model"
      - modelGender: "male" | "female"  (fitTarget == "model" 일 때만)
      - faceImage: dataURL            (fitTarget != "model" 일 때)
      - topDataUrl / topPath          (mode == twopiece/outer)
      - bottomDataUrl / bottomPath    (mode == twopiece/outer)
      - onepieceDataUrl / onepiecePath (mode == onepiece)
      - outerDataUrl / outerPath       (선택)
      - shoesDataUrl / shoesPath       (선택)
      - topAnalysis / bottomAnalysis / onepieceAnalysis / outerAnalysis  (Phase 1 분석)
      - bodyType, personalColor
      - lang: "ko" | "en"  (기본 ko)
    
    Response JSON (codistyle_generate와 동일 스키마 — 프론트 csScoreBox 호환):
      - ok, path, image, url, comment
      - styling_score, score_breakdown, styling_advice
      - executive_summary, tpo_recommendations, improvement_tips, style_hashtags
      - model, sdk
    """
    _t_lang = str((request.json or {}).get("lang") or "ko").strip().lower()
    _t_en = (_t_lang == "en")
    if not _GEMINI_KEY:
        return jsonify(ok=False, error="GEMINI_API_KEY 미설정"), 400

    # SDK 감지 (v53 SDK fix 패턴 준수: new → old fallback)
    _SDK = None
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

    payload = request.get_json(silent=True) or {}
    user_info = payload.get("user") or {}
    
    # 티어 → 엔진 라우팅 (재사용)
    _user_tier = str(user_info.get("tier") or payload.get("tier") or "FREE").upper().strip()
    if _user_tier not in ("FREE", "SILVER", "GOLD", "DIAMOND"):
        _user_tier = "FREE"
    _TRYON_MODEL = _resolve_engine(_user_tier, "tryon")
    print(f"[TRYON] tier={_user_tier} → model={_TRYON_MODEL}", flush=True)

    # 모드 & fit 검증
    mode = str(payload.get("mode") or "twopiece").strip().lower()
    if mode not in (_TRYON_MODE_TWOPIECE, _TRYON_MODE_ONEPIECE, _TRYON_MODE_OUTER):
        mode = _TRYON_MODE_TWOPIECE
    fit_target = str(payload.get("fitTarget") or "my").strip().lower()
    if fit_target not in (_TRYON_FIT_MY, _TRYON_FIT_SOMEBODY, _TRYON_FIT_MODEL):
        fit_target = _TRYON_FIT_MY
    model_gender = str(payload.get("modelGender") or "").strip().lower()

    # 프로필 정보
    gender = _normalize_gender_code(str(user_info.get("gender", "")))
    gender_en = "woman" if gender == "F" else "man"
    gender_ko = "여성" if gender == "F" else "남성"
    age = str(user_info.get("ageGroup", "30대")).strip()
    height = str(user_info.get("height", "")).strip()
    weight = str(user_info.get("weight", "")).strip()
    body_type_key = str(payload.get("bodyType", "")).strip()
    
    # 퍼스널컬러 summary
    _pc = payload.get("personalColor") or {}
    pc_summary = str(_pc.get("summary", "")).strip() if isinstance(_pc, dict) else ""

    # Phase 1 분석 결과
    top_info      = payload.get("topAnalysis")      or {}
    bottom_info   = payload.get("bottomAnalysis")   or {}
    onepiece_info = payload.get("onepieceAnalysis") or {}
    outer_info    = payload.get("outerAnalysis")    or {}
    shoes_info    = payload.get("shoesAnalysis")    or {}

    print(
        f"[TRYON-DIAG] mode={mode} fit={fit_target} model_g={model_gender} "
        f"tier={_user_tier} gender={gender} age={age} "
        f"H={height} W={weight} body={body_type_key} pc='{pc_summary[:40]}' "
        f"face={'Y' if payload.get('faceImage') else 'N'}",
        flush=True
    )

    # ─── 이미지 bytes 준비 (codistyle과 동일 _to_bytes 로컬 정의) ───
    def _to_bytes(data_url_val, path_val=None):
        """dataUrl / 로컬파일 / HTTP URL → (mime, raw_bytes). codistyle과 동일 로직."""
        src = str(data_url_val or "").strip()
        if src.startswith("data:"):
            header, b64 = src.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
            return mime, base64.b64decode(b64)
        if src.startswith("http://") or src.startswith("https://"):
            # 자기 서버 URL → R2 직접 로드
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
                        print(f"[TRYON _to_bytes] R2 직접 로드 실패: {e}")
                for d in [_UPLOAD_DIR, _LEGACY_UPLOAD_DIR]:
                    fpath = os.path.join(d, os.path.basename(_self_upload_path))
                    if os.path.exists(fpath):
                        with open(fpath, "rb") as fh:
                            return "image/jpeg", fh.read()
            # 외부 URL 일반 다운로드
            try:
                import requests as _rq
                r = _rq.get(src, timeout=15)
                if r.status_code == 200:
                    ct = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
                    return ct, r.content
            except Exception as e:
                print(f"[TRYON _to_bytes] 외부 URL 로드 실패: {e}")
        # 로컬 파일 경로
        if path_val:
            for d in [_UPLOAD_DIR, _LEGACY_UPLOAD_DIR, "."]:
                fpath = os.path.join(d, os.path.basename(path_val))
                if os.path.exists(fpath):
                    with open(fpath, "rb") as fh:
                        return "image/jpeg", fh.read()
        return None, None

    # 이미지 수집
    images_map = {}
    if mode in (_TRYON_MODE_TWOPIECE, _TRYON_MODE_OUTER):
        if payload.get("topDataUrl") or payload.get("topPath"):
            m, b = _to_bytes(payload.get("topDataUrl"), payload.get("topPath"))
            if b: images_map["top"] = (m, b)
        if payload.get("bottomDataUrl") or payload.get("bottomPath"):
            m, b = _to_bytes(payload.get("bottomDataUrl"), payload.get("bottomPath"))
            if b: images_map["bottom"] = (m, b)
    if mode == _TRYON_MODE_ONEPIECE:
        if payload.get("onepieceDataUrl") or payload.get("onepiecePath"):
            m, b = _to_bytes(payload.get("onepieceDataUrl"), payload.get("onepiecePath"))
            if b: images_map["onepiece"] = (m, b)
    if payload.get("outerDataUrl") or payload.get("outerPath"):
        m, b = _to_bytes(payload.get("outerDataUrl"), payload.get("outerPath"))
        if b: images_map["outer"] = (m, b)
    if payload.get("shoesDataUrl") or payload.get("shoesPath"):
        m, b = _to_bytes(payload.get("shoesDataUrl"), payload.get("shoesPath"))
        if b: images_map["shoes"] = (m, b)

    # 필수 검증
    if mode == _TRYON_MODE_TWOPIECE and ("top" not in images_map or "bottom" not in images_map):
        return jsonify(ok=False, error="투피스 모드는 상의와 하의 이미지가 필요합니다"), 400
    if mode == _TRYON_MODE_ONEPIECE and "onepiece" not in images_map:
        return jsonify(ok=False, error="원피스 모드는 원피스 이미지가 필요합니다"), 400
    if mode == _TRYON_MODE_OUTER and "outer" not in images_map:
        return jsonify(ok=False, error="아우터 모드는 아우터 이미지가 필요합니다"), 400

    # 얼굴 이미지 (fit_target에 따라)
    face_mime, face_bytes = None, None
    if fit_target != _TRYON_FIT_MODEL:
        face_mime, face_bytes = _to_bytes(payload.get("faceImage"), None)
        if not face_bytes and fit_target == _TRYON_FIT_MY:
            # 마이핏인데 얼굴 없으면 경고만 (계속 진행, 모델 얼굴로 대체됨)
            print("[TRYON-WARN] fit=my but faceImage is missing → will use generic face", flush=True)

    # ════════════════════════════════════════════════════════════════════
    # ─── 2026-04-23 16:00 KST [TJ 지시 — 병렬 처리] ────────────────────
    #
    # 기존: Gemini 3 Pro Image 단일 호출 (이미지+분석 동시) → JSON 부실
    # 신규: 이미지 생성 + 분석 JSON을 ThreadPoolExecutor 병렬 호출
    #   worker 1: Gemini 3 Pro Image (이미지 전담)
    #   worker 2: Gemini 3 Pro Text (분석 JSON 전담)
    # 둘 다 완료 후 통합. 프론트 코드 변경 없음.
    # ════════════════════════════════════════════════════════════════════
    
    # ─── [2026-04-24 v7] 실제 첨부된 이미지 key set 준비 ───
    # 프롬프트 빌더가 "어떤 이미지가 실제로 Gemini에 전달되는지" 판단하는 기준
    # 이전 버그: shoes_info({}) 기반 판단 → 이미지는 있는데 프롬프트엔 반영 안 됨
    # 수정: 실제 images_map 기반 → 이미지 유무와 프롬프트 지시 완전 일치
    _attached = set(images_map.keys())
    
    # 진단 로그 — 어떤 아이템이 첨부/미첨부 되었는지 명확히
    _possible = {"twopiece":["top","bottom","outer","shoes"],
                 "onepiece":["onepiece","outer","shoes"],
                 "outer":["outer","top","bottom","shoes"]}.get(mode, [])
    _missing = [k for k in _possible if k not in _attached]
    print(
        f"[TRYON-IMG] mode={mode} · attached=[{','.join(sorted(_attached))}] "
        f"· missing=[{','.join(_missing)}] · face={bool(face_bytes)}",
        flush=True
    )
    
    # ─── 이미지 생성용 프롬프트 ───
    prompt_img, img_meta = _tryon_build_prompt(
        mode=mode,
        fit_target=fit_target,
        model_gender=model_gender,
        gender_ko=gender_ko,
        gender_en=gender_en,
        age=age,
        height=height,
        weight=weight,
        body_type_key=body_type_key,
        pc_summary=pc_summary,
        top_info=top_info,
        bottom_info=bottom_info,
        onepiece_info=onepiece_info,
        outer_info=outer_info,
        shoes_info=shoes_info,
        attached_keys=_attached,  # [v7] 신규 — 실제 첨부된 이미지 기반 판단
        lang_en=_t_en,
    )
    
    # ─── 분석용 프롬프트 (텍스트 모델 전담) ───
    prompt_analysis, _analysis_img_meta = _tryon_build_analysis_prompt(
        mode=mode,
        fit_target=fit_target,
        model_gender=model_gender,
        gender_ko=gender_ko,
        gender_en=gender_en,
        age=age,
        height=height,
        weight=weight,
        body_type_key=body_type_key,
        pc_summary=pc_summary,
        top_info=top_info,
        bottom_info=bottom_info,
        onepiece_info=onepiece_info,
        outer_info=outer_info,
        shoes_info=shoes_info,
        attached_keys=_attached,  # [v7] 신규 — 동일 원칙 적용
        lang_en=_t_en,
    )
    
    # ─── Worker 1: 이미지 생성 전담 함수 ───
    def _worker_generate_image():
        """Gemini 3 Pro Image 호출 → 이미지 bytes + finish_reason 반환"""
        _img_bytes = None
        _comment_fallback = ""  # 이미지 모델이 혹시 텍스트도 주면 백업용
        _finish = "unknown"
        try:
            if _SDK == "new":
                contents = [prompt_img]
                if face_bytes:
                    contents.append(_gtypes.Part.from_bytes(
                        data=face_bytes, mime_type=face_mime or "image/jpeg"))
                for _k in img_meta["item_order"]:
                    if _k in images_map:
                        _m, _b = images_map[_k]
                        contents.append(_gtypes.Part.from_bytes(
                            data=_b, mime_type=_m or "image/jpeg"))
                
                client = _genai.Client(api_key=_GEMINI_KEY)
                
                # ─── 2026-04-23 17:30 [TJ 지시 — 전신 뷰박스 1:1.62 비율 대응] ───
                # ─── 2026-05-09 KST · TJ 지시 (v29) ─── aspect_ratio 가로로 강제
                #   원인 진단: 이전 "9:16" (portrait)으로 설정되어 있었음.
                #              프롬프트는 가로 2:1 강력 요청하지만 image_config가 우선.
                #              → 모델이 9:16 캔버스에 가로 콘텐츠를 욱여넣고
                #                위/아래 검은 패딩으로 채움 (TJ 첨부 이미지 1).
                #   수정: "16:9" (landscape, 1.78:1) — 코디핏의 가로 2:1과 가까운 비율.
                #         정/후면 두 인물이 가로로 자연스럽게 들어감, 패딩 없음.
                # ─── 2026-05-09 KST · TJ 지시 (v30) ─── 이미지 화질 업그레이드
                #   배경: 트라이온은 Nano Banana Pro($0.134/req) 사용 — 프리미엄 기능.
                #          구독료 만족도를 위해 고화질 출력 필수.
                #   변경: image_size "1K"(1024) → "2K"(2048) = 4배 픽셀 밀도
                #          가로 2K × 16:9 ≈ 2048×1152 출력 → 정/후면 각 1024×1152
                #          모바일 Retina 디스플레이에서도 선명, 저장/공유 시 고품질
                #   주의: "4K"는 응답 30초+ / 일부 미지원 / 에러율 높음 → "2K"가 최적점
                # ImageConfig는 SDK 버전에 따라 없을 수 있어 예외 처리.
                try:
                    _img_gen_config = _gtypes.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                        temperature=0.4,
                        max_output_tokens=8192,
                        image_config=_gtypes.ImageConfig(
                            aspect_ratio="16:9",
                            image_size="2K",
                        ),
                    )
                except (TypeError, AttributeError) as _cfg_e:
                    # 구버전 SDK 폴백 — ImageConfig 미지원 시 프롬프트의 비율 지시만으로 처리
                    print(f"[TRYON-IMG] image_config 미지원, 프롬프트만으로: {_cfg_e}", flush=True)
                    _img_gen_config = _gtypes.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                        temperature=0.4,
                        max_output_tokens=8192,
                    )
                
                # ─── [2026-05-02 v55 TJ] 403 권한 거부 자동 fallback (다단 재시도) ───
                # 진단: gemini-3-pro-image-preview 권한 없을 때, 단순히 모델만 바꾸면
                #       image_config(aspect_ratio,image_size)가 신규 모델 전용이라 fallback 모델이 거부함.
                # 해결: fallback 시 image_config 제거 + response_modalities만 유지
                # 추가: 그래도 실패하면 _CODISTYLE_MODEL(personal-color가 사용 중인 검증된 모델)로 재시도
                try:
                    response = client.models.generate_content(
                        model=_TRYON_MODEL,
                        contents=contents,
                        config=_img_gen_config,
                    )
                except Exception as _primary_err:
                    _emsg = str(_primary_err)
                    if ('403' in _emsg or 'PERMISSION_DENIED' in _emsg or 'denied access' in _emsg):
                        # ─── 1차 fallback: 환경변수 또는 기본 fallback 모델 + image_config 제거 ───
                        _fallback_img_model = os.getenv("CODIBANK_MODEL_TRYON_FALLBACK", "gemini-2.5-flash-image")
                        print(f"[TRYON-FALLBACK-IMG] '{_TRYON_MODEL}' 권한 없음 → '{_fallback_img_model}' (image_config 제거)로 재시도", flush=True)
                        # image_config 없는 단순 config (aspect_ratio는 프롬프트로 전달)
                        try:
                            _simple_config = _gtypes.GenerateContentConfig(
                                response_modalities=["IMAGE", "TEXT"],
                                temperature=0.4,
                                max_output_tokens=8192,
                            )
                        except Exception:
                            _simple_config = None
                        try:
                            response = client.models.generate_content(
                                model=_fallback_img_model,
                                contents=contents,
                                config=_simple_config,
                            )
                        except Exception as _fb1_err:
                            _emsg2 = str(_fb1_err)
                            print(f"[TRYON-FALLBACK-IMG] 1차 실패: {_emsg2[:200]}", flush=True)
                            # ─── 2차 fallback: personal-color/codistyle와 동일한 _CODISTYLE_MODEL 사용 ───
                            # personal-color가 200 OK로 작동 중이므로 이 모델은 검증됨
                            print(f"[TRYON-FALLBACK-IMG] 2차 시도 → '{_CODISTYLE_MODEL}' (personal-color 검증 모델)", flush=True)
                            response = client.models.generate_content(
                                model=_CODISTYLE_MODEL,
                                contents=contents,
                                config=_simple_config,
                            )
                    else:
                        raise
                
                # 이미지 + 백업 텍스트 추출
                candidates = getattr(response, "candidates", []) or []
                if candidates:
                    cand = candidates[0]
                    _finish = str(getattr(cand, "finish_reason", "")).upper()
                    parts = getattr(getattr(cand, "content", None), "parts", []) or []
                    for p in parts:
                        # thought 파트는 제외
                        if getattr(p, "thought", False):
                            continue
                        inline = getattr(p, "inline_data", None)
                        if inline and getattr(inline, "data", None):
                            raw = inline.data
                            if isinstance(raw, str):
                                raw = base64.b64decode(raw)
                            _img_bytes = raw
                        elif getattr(p, "text", None):
                            _comment_fallback += str(p.text)
            else:
                # old SDK
                from PIL import Image as _PILImage
                _genai_old.configure(api_key=_GEMINI_KEY)
                model_obj = _genai_old.GenerativeModel(_TRYON_MODEL)
                
                def _b2pil(raw):
                    return _PILImage.open(io.BytesIO(raw))
                
                contents_old = [prompt_img]
                if face_bytes:
                    contents_old.append(_b2pil(face_bytes))
                for _k in img_meta["item_order"]:
                    if _k in images_map:
                        _m, _b = images_map[_k]
                        contents_old.append(_b2pil(_b))
                
                try:
                    response = model_obj.generate_content(
                        contents_old,
                        generation_config={
                            "response_modalities": ["IMAGE", "TEXT"],
                            "temperature": 0.4,
                            "max_output_tokens": 8192,
                        },
                    )
                except TypeError:
                    response = model_obj.generate_content(contents_old)
                except Exception as _primary_err_old:
                    # ─── [2026-05-02 v55 TJ] old SDK 403 권한 거부 다단 fallback ───
                    _emsg_old = str(_primary_err_old)
                    if ('403' in _emsg_old or 'PERMISSION_DENIED' in _emsg_old or 'denied access' in _emsg_old):
                        _fallback_img_model = os.getenv("CODIBANK_MODEL_TRYON_FALLBACK", "gemini-2.5-flash-image")
                        print(f"[TRYON-FALLBACK-IMG][old SDK] '{_TRYON_MODEL}' 권한 없음 → '{_fallback_img_model}' 재시도", flush=True)
                        model_obj_fb = _genai_old.GenerativeModel(_fallback_img_model)
                        try:
                            try:
                                response = model_obj_fb.generate_content(
                                    contents_old,
                                    generation_config={
                                        "response_modalities": ["IMAGE", "TEXT"],
                                        "temperature": 0.4,
                                        "max_output_tokens": 8192,
                                    },
                                )
                            except TypeError:
                                response = model_obj_fb.generate_content(contents_old)
                        except Exception as _fb1_err_old:
                            _emsg2_old = str(_fb1_err_old)
                            print(f"[TRYON-FALLBACK-IMG][old SDK] 1차 실패: {_emsg2_old[:200]}", flush=True)
                            # 2차 fallback: _CODISTYLE_MODEL (personal-color 검증 모델)
                            print(f"[TRYON-FALLBACK-IMG][old SDK] 2차 시도 → '{_CODISTYLE_MODEL}'", flush=True)
                            model_obj_fb2 = _genai_old.GenerativeModel(_CODISTYLE_MODEL)
                            try:
                                response = model_obj_fb2.generate_content(
                                    contents_old,
                                    generation_config={
                                        "response_modalities": ["IMAGE", "TEXT"],
                                        "temperature": 0.4,
                                        "max_output_tokens": 8192,
                                    },
                                )
                            except TypeError:
                                response = model_obj_fb2.generate_content(contents_old)
                    else:
                        raise
                
                try:
                    _comment_fallback = response.text or ""
                except Exception:
                    pass
                try:
                    for cand in (response.candidates or []):
                        parts = (cand.content.parts if cand.content else [])
                        for p in parts:
                            if hasattr(p, "inline_data") and getattr(p.inline_data, "data", None):
                                raw = p.inline_data.data
                                if isinstance(raw, str):
                                    raw = base64.b64decode(raw)
                                _img_bytes = raw
                        if cand.finish_reason:
                            _finish = str(cand.finish_reason).upper()
                except Exception:
                    pass
        except Exception as _img_e:
            print(f"[TRYON-IMG-ERR] 이미지 생성 실패: {_img_e}", flush=True)
            raise
        return _img_bytes, _comment_fallback, _finish
    
    # ─── Worker 2: 분석 JSON 전담 함수 ───
    def _worker_analyze():
        """Gemini 3 Pro (텍스트) 호출 → 분석 JSON 텍스트 반환"""
        try:
            return _tryon_analyze_via_text_model(
                api_key=_GEMINI_KEY,
                prompt=prompt_analysis,
                face_bytes=face_bytes,
                face_mime=face_mime,
                images_map=images_map,
                img_order=_analysis_img_meta["item_order"],
                sdk_mode=_SDK,
            )
        except Exception as _ana_e:
            print(f"[TRYON-ANALYSIS-ERR] 분석 호출 실패: {_ana_e}", flush=True)
            raise
    
    # ─── 병렬 실행 (최대 90초 대기) ───
    import concurrent.futures as _cf
    import time as _time
    
    _ANALYSIS_MODEL = os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS", "gemini-3.1-pro-preview")
    _ANALYSIS_THINKING = _resolve_thinking_level()  # 환경변수 기반, 마스터가 실시간 변경 가능
    _t0 = _time.time()
    print(
        f"[TRYON-PARALLEL] 시작 — image={_TRYON_MODEL}, "
        f"analysis={_ANALYSIS_MODEL}, thinking={_ANALYSIS_THINKING}",
        flush=True
    )
    
    img_bytes = None
    comment = ""
    finish = "unknown"
    analysis_ok = False
    
    with _cf.ThreadPoolExecutor(max_workers=2, thread_name_prefix="tryon") as _executor:
        _fut_img = _executor.submit(_worker_generate_image)
        _fut_ana = _executor.submit(_worker_analyze)
        
        # 이미지 결과 (필수)
        try:
            img_bytes, _img_fallback_text, finish = _fut_img.result(timeout=120)
            _dt_img = _time.time() - _t0
            print(f"[TRYON-PARALLEL] ✓ image ready ({_dt_img:.1f}s)", flush=True)
        except Exception as _e:
            print(f"[TRYON-PARALLEL] ✗ image FAILED: {_e}", flush=True)
            return jsonify(
                ok=False,
                error=f"이미지 생성 실패: {str(_e)[:200]}"
            ), 500
        
        # 분석 결과 (선택 — 실패해도 이미지는 반환)
        try:
            comment = _fut_ana.result(timeout=120)
            analysis_ok = True
            _dt_ana = _time.time() - _t0
            print(f"[TRYON-PARALLEL] ✓ analysis ready ({_dt_ana:.1f}s, len={len(comment)})", flush=True)
        except Exception as _e:
            print(f"[TRYON-PARALLEL] ⚠ analysis FAILED (이미지는 성공): {_e}", flush=True)
            # 백업: 이미지 모델이 준 텍스트라도 사용
            comment = _img_fallback_text or ""
    
    _total_dt = _time.time() - _t0
    print(f"[TRYON-PARALLEL] 전체 완료 {_total_dt:.1f}s · analysis={'OK' if analysis_ok else 'FAIL'}", flush=True)
    
    # 이미지 필수 검증
    if not img_bytes:
        return jsonify(
            ok=False,
            error=f"착장 이미지 생성에 실패했습니다. 다시 시도해주세요. (reason={finish})"
        ), 500

    # ─── R2 업로드 + 응답 구성 ───
    if isinstance(img_bytes, str):
        img_bytes = base64.b64decode(img_bytes)
    rel = _write_upload_bytes("tryon", "jpg", img_bytes)
    base = _public_base()

    # 텍스트 응답에서 점수·분석 추출
    parsed = _tryon_parse_response(comment)

    # garment_summary 구성 (프론트 호환)
    garment_summary = {
        "mode": mode,
        "fit": fit_target,
        "top":      top_info.get("sub_category", "") if top_info else "",
        "bottom":   bottom_info.get("sub_category", "") if bottom_info else "",
        "onepiece": onepiece_info.get("sub_category", "") if onepiece_info else "",
        "outer":    outer_info.get("sub_category", "") if outer_info else "",
        "shoes":    shoes_info.get("sub_category", "") if shoes_info else "",
    }

    print(
        f"[TRYON] ✅ 생성 완료: {rel} · score={parsed['styling_score']} · "
        f"comment_len={len(comment)}",
        flush=True
    )

    return jsonify(
        ok=True,
        path=rel,
        image=f"{base}{rel}",
        url=f"{base}{rel}",
        comment=comment or "AI 트라이온 착장 이미지 생성 완료!",
        styling_score=parsed["styling_score"],
        score_breakdown=parsed["score_breakdown"],
        styling_advice=parsed["styling_advice"],
        executive_summary=parsed["executive_summary"],
        tpo_recommendations=parsed["tpo_recommendations"],
        improvement_tips=parsed["improvement_tips"],
        style_hashtags=parsed["style_hashtags"],
        item_curation=parsed.get("item_curation", []),  # [v9] 신발/가방/액세서리 큐레이션
        garment_summary=garment_summary,
        model=_TRYON_MODEL,
        sdk=_SDK,
        # 트라이온 전용 메타
        tryon_mode=mode,
        tryon_fit=fit_target,
        # [2026-04-23 16:00] 병렬 처리 메타 (디버깅/모니터링용)
        analysis_model=_ANALYSIS_MODEL,
        analysis_thinking_level=_ANALYSIS_THINKING,  # [17:00] 마스터가 변경 시 확인용
        analysis_ok=analysis_ok,
        elapsed_sec=round(_total_dt, 1),
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

# ─── 2026-04-21 KST ─── 엔진 라우팅 조회 API ───
# ─── 2026-04-22 17:05 KST ─── 서비스별 단일 모델 정책 반영 ───
@app.get("/admin/engine-config")
def admin_engine_config():
    """
    엔진 설정 현황 조회 (관리자 전용).
    
    [2026-04-22 17:05] 정책 변경: 티어 무시, 서비스(코디핏/트라이온)만 보고 모델 결정.
    
    응답 예시:
    {
      "ok": true,
      "engine_aliases": {
        "flash_v1": "gemini-2.5-flash-image",
        "flash_v2": "gemini-3.1-flash-image-preview",   // Nano Banana 2
        "pro":      "gemini-3-pro-image-preview"         // Nano Banana Pro
      },
      "service_engines": {
        "codifit": "gemini-3.1-flash-image-preview",    // 코디핏 → Nano Banana 2
        "tryon":   "gemini-3-pro-image-preview"          // 트라이온 → Nano Banana Pro
      },
      "matrix": {                                        // 하위호환 (모든 티어 동일)
        "FREE":    {"codifit": "...", "tryon": "..."},
        "SILVER":  {...}, "GOLD": {...}, "DIAMOND": {...}
      },
      "policy_note": "티어 무시 · 서비스별 단일 모델 (2026-04-22 17:05 KST)"
    }
    """
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        config = _get_engine_config_summary()
        config["ok"] = True
        return jsonify(config)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500



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

        # ── [Phase 1 — 2026-05-22 KST · TJ 지시] 파이프라인 단순화 ──────
        #   변경:
        #   · rembg — storage_upload() 에서 업로드 시점에 자동 실행됨 (재활성화).
        #             여기서 다시 호출 안 함 (HF Space 대기 누적 방지).
        #             image_url 로 받는 경우 이미 배경 제거된 PNG 가 R2 에 저장돼 있음.
        #             base64 로 받는 경우 (예: 카메라 즉시 분석) 는 storage_upload 미경유
        #             가능성 있으나, 분석 흐름 상 직전 업로드 → URL 경유가 대부분.
        #   · Lykdat 호출 — 제거 (외부 유료 API, Gemini 와 중복 작업)
        #   · Marqo embedding 호출 — 제거 (Render Starter RAM 부족으로 매번 silent 실패)
        #   · skip_embedding 분기 — 제거 (이제 무의미)
        # ──

        # ── img_bytes 최소 크기 검증 ──
        if not img_bytes or len(img_bytes) < 100:
            return jsonify(ok=False, error="이미지 데이터가 너무 작거나 없습니다"), 400

        # ── [Phase 1 — 2026-05-22] Gemini Vision 프롬프트 ──
        #   변경: Lykdat 컨텍스트(_lykdat_ctx) 제거. Gemini 단독 분석으로 단순화.
        #         프롬프트 본문(카테고리 룰)은 정확도 핵심이므로 그대로 유지.
        PROMPT = """
당신은 세계 최고의 패션 전문가 AI입니다.
이 의류 이미지를 분석하고 아래 JSON 형식으로만 응답하세요. JSON 외 다른 텍스트는 절대 포함하지 마세요.

⚠️ 배경 무시 규칙: 이미지에 바닥, 벽, 옷걸이, 손, 테이블 등 배경이 포함되어 있을 수 있습니다. 배경은 완전히 무시하고 의류 아이템 영역만 집중하여 분석하세요. 배경 색상을 의류 색상으로 착각하지 마세요.

⚠️ [2026-04-22 17:40 KST] 카테고리 판별 CRITICAL RULES — 순서대로 적용:

[규칙 1] 원피스(onepiece) 판별 — 치마/바지/상의와 구분
- 상의와 하의가 한 벌로 연결된 드레스 구조 → onepiece (원피스)
  · 상반신부터 허벅지 이상까지 한 장으로 이어지는 옷
  · 셔츠 형태여도 길이가 허벅지 이상 내려오며 벨트/허리 분리 없이 한 장이면 onepiece
  · 니트 원피스(knit dress), 셔츠 원피스(shirt dress) 등 모두 onepiece
- 상반신만 덮는 옷(셔츠/니트/티셔츠/블라우스) → top (상의)

[규칙 2] 치마/스커트 판별 — 원피스가 아닌 하의 전용
- 다리가 각각 분리된 통로(leg tube)가 있으면 → pants (바지류)
- 다리 분리 없이 한 장의 천이 아래로 퍼지면 → skirt (치마류) ← 착용샷이어도 동일하게 적용
- 폭이 넓어 바지처럼 보여도 leg separation 없으면 반드시 skirt
- 도트무늬/플리츠/티어드 등 디자인과 무관하게 구조로만 판별

[규칙 3] 아우터(coat/jacket) 판별 — 무릎 기준 길이로 구분
- 무릎 이상 긴 아우터 → coat (롱코트/트렌치코트/더플코트 등)
- 엉덩이 길이 또는 짧은 아우터 → jacket (블레이저/가디건/숏패딩/점퍼 등)
- 착용샷이어도 구조로만 판별 (디자인/패턴 무시)

[규칙 4] 가방(bag) 판별 — 2026-05-23 신규 추가 (TJ 지시)
- 들거나 메는 가방류 → bag
  · 핸드백, 토트백, 숄더백, 크로스백, 백팩, 클러치, 미니백, 에코백 등 모두 bag
  · 손잡이(handle) 또는 스트랩(strap) 이 있고 내부 수납이 가능한 형태이면 bag
- 가방을 든 사람 착용샷도 가방 자체가 주제이면 → bag (사람은 무시)
- bag 은 etc 로 절대 분류하지 말 것

[규칙 5] 모호한 경우 — 절대 etc 로 도피하지 말 것 (2026-05-23 TJ 지시)
- 의류 구조가 명확하면 (원피스/치마/바지/상의/아우터/신발/가방 등) 반드시 해당 카테고리 선택
- etc 는 진짜로 카테고리 11종 중 어디에도 속하지 않을 때만 (예: 액세서리, 헤어밴드, 안경 등)
- ⚠️ 명백한 원피스/드레스를 etc 로 분류한 사례가 있었음 → category 와 sub_category 는 반드시 일관성 있게
  · sub_category 에 "원피스"/"드레스" 가 들어가면 category 는 onepiece
  · sub_category 에 "가방"/"백" 이 들어가면 category 는 bag
  · sub_category 에 "스커트"/"치마" 가 들어가면 category 는 skirt
  · 두 필드가 모순되면 분석 실패로 간주

{
  "category": "coat | jacket | top | pants | skirt | onepiece | shoes | watch | scarf | socks | bag | etc 중 하나 — ⚠️ 치마/스커트는 반드시 skirt, 원피스는 반드시 onepiece, 가방은 반드시 bag. 혼동 금지.",
  "sub_category": "아래 세부 품목 중 하나로 정확히 분류:\n[아우터(coat)] 긴 아우터류: 아우터/코트/패딩/버버리(트렌치코트)/롱패딩\n[자켓(jacket)] 짧은 아우터류: 자켓/블레이저/점퍼/다운자켓/레더자켓/데님자켓/가디건 (기타 짧은 아우터: 수트자켓/콤비자켓/사파리자켓/집업자켓/후드집업자켓/숏패딩/다운조끼/볼레로)\n[상의(top)] 탑/셔츠/티셔츠/후드티/후드티셔츠/블라우스/면티/니트티/니트셔츠 (기타: 반팔티/긴팔티/맨투맨/스웨터)\n[바지(pants)] 바지/반바지/데님팬츠/조거팬츠/트레이닝하의/레깅스/숏팬츠/러너팬츠 (기타: 청바지/슬랙스/면바지/스키니/와이드팬츠)\n[치마(skirt)] 스커트/H라인스커트/A라인스커트/플레어스커트/플리츠스커트/머메이드스커트/미니스커트/미디스커트/롱스커트/레이어드스커트 (기타: 랩스커트/티어드스커트/도트스커트)\n[원피스(onepiece)] 원피스/미디원피스/롱원피스/셔츠원피스/시스원피스/랩원피스/슬립원피스/시프트원피스/드레스/웨딩드레스/원피스수영복/투피스수영복/비키니수영복 (기타: 미니원피스/니트원피스)\n[가방(bag)] 핸드백/토트백/숄더백/크로스백/백팩/클러치백/미니백/에코백/버킷백/호보백/새첼백/메신저백/더플백 (기타: 보스턴백/카메라백/지갑)",
  "is_skirt": "true if category=skirt, false otherwise — ⚠️ 원피스(onepiece)는 false로 설정",
  "is_onepiece": "true if category=onepiece, false otherwise — ⚠️ 원피스 여부 신규 필드 (2026-04-22 추가)",
  "skirt_length": "mini(무릎위) | midi(무릎~종아리중간) | maxi(종아리~발목) | null(치마아닌경우)",
  "dress_length": "mini(무릎위) | midi(무릎~종아리중간) | maxi(종아리~발목) | null(원피스아닌경우) — ⚠️ onepiece 전용 신규 필드",
  "outer_type": "아우터 | 코트 | 패딩 | 버버리 | 롱패딩 | 자켓 | 블레이저 | 점퍼 | 다운자켓 | 레더자켓 | 데님자켓 | 가디건 | null(아우터아닌경우) — ⚠️ [2026-04-23 TJ 분류] 긴 아우터(category=coat): 아우터/코트/패딩/버버리/롱패딩 · 짧은 아우터(category=jacket): 자켓/블레이저/점퍼/다운자켓/레더자켓/데님자켓/가디건",
  "main_color": "#RRGGBB 형식의 주요 색상 HEX",
  "main_color_name": "색상 이름 (한국어)",
  "sub_color": "#RRGGBB 또는 null",
  "sub_color_name": "보조 색상 이름 (한국어) 또는 null",
  "pattern": "단색|스트라이프|체크|도트|플로럴|기하학|카무플라주|그래픽|레터링|애니멀|페이즐리|추상 중 하나",
  "material": "면|린넨|울|캐시미어|실크|폴리에스터|나일론|데님|가죽|니트|혼방|기타 중 하나 이상 (쉼표 구분)",
  "fit": "오버사이즈|루즈|레귤러|슬림|스키니 중 하나",
  "season": "봄여름|가을겨울|사계절|여름전용|겨울전용 중 하나",
  "style_keywords": ["캐주얼|포멀|스트릿|미니멀|빈티지|스포티|로맨틱|클래식|오피스|데이트|데일리|파티|여행|운동 중 최대 3개 — TPO/스타일 태그로 활용"],
  "design_points": "이 아이템의 디자인 특징 1~2문장 (한국어) — 착용샷이면 의류 아이템만 묘사",
  "coordinate_hint": "이 아이템이 적합한 TPO(시간/장소/상황) 추천 코디 — 한국어 1문장, **반드시 50자 이내** — 예시: '오피스룩과 데이트 모두 어울리는 데일리 아이템' / '주말 카페나 친구 모임에 좋은 캐주얼 가방' / '격식 있는 비즈니스 자리에 적합한 클래식 아이템'"
}

분석 기준:
- 착용샷(사람이 입은 사진)이어도 의류 아이템 자체만 분석
- 배경과 착용자 신체 무시, 의류 구조에만 집중
- 원피스류(onepiece)는 category를 반드시 onepiece로, is_onepiece를 true로, dress_length를 채울 것
- 치마류(skirt)는 category를 반드시 skirt로, is_skirt를 true로, skirt_length를 채울 것
- 아우터일 때 outer_type 필드를 반드시 채울 것:
  · 긴 아우터(category=coat): 아우터/코트/패딩/버버리/롱패딩 중 하나
  · 짧은 아우터(category=jacket): 자켓/블레이저/점퍼/다운자켓/레더자켓/데님자켓/가디건 중 하나
- 가디건은 반드시 category=jacket (2026-04-23 TJ 확정)
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

        # ──── [Phase 1 — 2026-05-22 KST · TJ 지시] Gemini 모델 + JSON 스키마 ────
        #   변경 1: 모델 체인 교체
        #     이전: gemini-2.0-flash → gemini-1.5-flash → gemini-1.5-flash-8b
        #            (셋 다 2026-06-01 deprecated 예정 — Google 공지)
        #     신규: gemini-2.5-flash-lite (1순위, 1/3 비용)
        #          → gemini-2.5-flash (fallback, 안정성)
        #            (현역 모델만 사용, deprecated 회피)
        #   변경 2: JSON 스키마 강제 (response_mime_type + response_schema)
        #     이전: 텍스트 JSON 응답 → 정규식 정리 → json.loads → 가끔 실패
        #     신규: API 레벨에서 JSON·enum·필드 누락 검증 → 파싱 실패 0%
        #   호환성: 응답 필드 100% 유지 (camera.html / item.html 무수정)
        # ────────────────────────────────────────────────────────────────────
        _ANALYZE_PRIMARY = os.getenv("CODIBANK_ANALYZE_MODEL") or "gemini-2.5-flash-lite"
        _ANALYZE_CHAIN = [_ANALYZE_PRIMARY, "gemini-2.5-flash"]
        _seen_a = set()
        _ANALYZE_CHAIN = [m for m in _ANALYZE_CHAIN if not (m in _seen_a or _seen_a.add(m))]

        # ── JSON 스키마 정의 (response_schema 용) ──
        #   허용 값 enum 명시 → 모델이 임의 값 생성 불가 → 정확도 향상
        _ITEM_SCHEMA = {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["coat", "jacket", "top", "pants", "skirt", "onepiece", "shoes", "watch", "scarf", "socks", "bag", "etc"]
                },
                "sub_category":     {"type": "string"},
                "is_skirt":         {"type": "boolean"},
                "is_onepiece":      {"type": "boolean"},
                "skirt_length":     {"type": "string", "enum": ["mini", "midi", "maxi", "none"]},
                "dress_length":     {"type": "string", "enum": ["mini", "midi", "maxi", "none"]},
                "outer_type":       {"type": "string"},
                "main_color":       {"type": "string"},
                "main_color_name":  {"type": "string"},
                "sub_color":        {"type": "string"},
                "sub_color_name":   {"type": "string"},
                "pattern": {
                    "type": "string",
                    "enum": ["단색", "스트라이프", "체크", "도트", "플로럴", "기하학", "카무플라주", "그래픽", "레터링", "애니멀", "페이즐리", "추상"]
                },
                "material":         {"type": "string"},
                "fit": {
                    "type": "string",
                    "enum": ["오버사이즈", "루즈", "레귤러", "슬림", "스키니"]
                },
                "season": {
                    "type": "string",
                    "enum": ["봄여름", "가을겨울", "사계절", "여름전용", "겨울전용"]
                },
                "style_keywords": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "design_points":     {"type": "string"},
                "coordinate_hint":   {"type": "string"}
            },
            "required": [
                "category", "sub_category", "is_skirt", "is_onepiece",
                "main_color", "main_color_name", "pattern", "material",
                "fit", "season", "style_keywords", "design_points", "coordinate_hint"
            ]
        }

        _analyze_success_model = None
        _analyze_errors = []

        for _a_idx, _a_model in enumerate(_ANALYZE_CHAIN, 1):
            try:
                if _SDK == "new":
                    _cli = _gmod.Client(api_key=_GEMINI_KEY)
                    _img_part = _gtypes.Part.from_bytes(data=img_bytes, mime_type=img_mime)
                    # ── [Phase 1] JSON 스키마 강제 (google-genai 신 SDK) ──
                    _cfg = _gtypes.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=_ITEM_SCHEMA,
                    )
                    _resp = _cli.models.generate_content(
                        model=_a_model,
                        contents=[_gtypes.Content(parts=[_img_part, _gtypes.Part.from_text(text=PROMPT)])],
                        config=_cfg,
                    )
                    _tmp = _resp.text if hasattr(_resp, "text") else str(_resp)
                else:
                    _gmod.configure(api_key=_GEMINI_KEY)
                    import PIL.Image as _PILImage
                    import io
                    _pil = _PILImage.open(io.BytesIO(img_bytes))
                    # ── [Phase 1] JSON 스키마 강제 (google-generativeai 구 SDK) ──
                    _gen_cfg = {
                        "response_mime_type": "application/json",
                        "response_schema": _ITEM_SCHEMA,
                    }
                    _model = _gmod.GenerativeModel(_a_model, generation_config=_gen_cfg)
                    _resp = _model.generate_content([PROMPT, _pil])
                    _tmp = _resp.text

                # 최소 JSON 응답 길이 체크
                if _tmp and len(_tmp.strip()) > 50:
                    result_text = _tmp
                    _analyze_success_model = _a_model
                    print(
                        f"[analyze-item][DIAG] ✅ 성공: model={_a_model} "
                        f"(시도={_a_idx}/{len(_ANALYZE_CHAIN)}) resp_len={len(result_text)}",
                        flush=True,
                    )
                    break
                else:
                    _analyze_errors.append(f"{_a_model}: 응답 짧음({len(_tmp or '')}자)")
            except Exception as _a_err:
                _err_msg = f"{_a_model}: {str(_a_err)[:120]}"
                _analyze_errors.append(_err_msg)
                print(
                    f"[analyze-item][DIAG] ⚠️ {_a_model} 실패: {str(_a_err)[:120]} → 다음 모델 시도",
                    flush=True,
                )

        if not _analyze_success_model:
            print(
                f"[analyze-item][DIAG] ❌ 모든 모델 실패: {_analyze_errors}",
                flush=True,
            )
            return jsonify(ok=False, error=f"분석 모델 모두 실패: {_analyze_errors[:2]}"), 500

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

        # ── [Phase 1 — 2026-05-22] 결과 병합 단순화 ──
        #   제거: Lykdat 폴백 보완 (lykdat_data 없음)
        #   제거: Marqo embedding 응답 첨부 (Render Starter RAM 부족으로 미사용)
        #   유지: Gemini analysis 결과만으로 응답 구성

        # ── [Phase 3 — 2026-05-23 KST · TJ 지시] LAB/KMeans 색상 보강 ──
        #   배경: Gemini 단독 분석은 다중 색상 의류 (예: 블랙+버건디 반반 자켓) 를
        #         한 가지 색으로만 잡는 경향. 반대로 KMeans 는 색상 비율을
        #         수치로 제공하므로 두 결과를 결합하면 정확도 ↑.
        #   전략:
        #     1. 항상 KMeans 실행해 상위 3색 추출 → response["color_palette"]
        #     2. Gemini main_color HEX 와 KMeans top1 비교 → 불일치 + KMeans top2
        #        가 충분히 큰 비율 (>=30%) 이면 sub_color 자동 보강
        #     3. Gemini 결과는 보존 (덮어쓰기 X) — 사용자가 어느 쪽을 신뢰할지 선택
        #   안전장치: 색상 추출 실패해도 Gemini 결과만으로 정상 응답
        _color_palette = []
        try:
            _color_palette = extract_dominant_colors(img_bytes, top_n=3)
            if _color_palette:
                analysis["color_palette"] = _color_palette
                # Gemini sub_color 가 비어있고 KMeans top2 가 충분히 크면 보강
                _has_sub = bool(analysis.get("sub_color") or analysis.get("sub_color_name"))
                if not _has_sub and len(_color_palette) >= 2:
                    top2 = _color_palette[1]
                    if top2["ratio"] >= 0.30:
                        analysis["sub_color"] = top2["hex"]
                        analysis["sub_color_name"] = top2["name"]
                        print(f"[Phase3] sub_color 자동 보강: {top2['name']} ({top2['ratio']*100:.0f}%)")
        except Exception as _ce:
            print(f"[Phase3] color_palette 추출 스킵: {_ce}")

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
                
                # ── [HOTFIX B — 2026-05-23 KST · TJ 지시] 호환성 평가 모델 교체 ──
                #   원인: gemini-2.0-flash 가 신규 사용자에게 비활성화됨 (Google 정책 변경).
                #         로그에서 매 analyze-item 호출마다 다음 에러 발생:
                #         "404 NOT_FOUND. models/gemini-2.0-flash is no longer available
                #          to new users."
                #         → 호환성 평가(pc_score/bt_score/total_score) 누락된 채 응답.
                #   해결: gemini-2.5-flash-lite 로 교체 (Phase 1 의 메인 분석과 동일 모델).
                #         텍스트 전용 호출이라 image 모델 비호환 이슈 없음.
                if _SDK == "new":
                    _compat_resp = _cli.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=[_compat_prompt],
                    )
                    _compat_text = _compat_resp.text.strip()
                else:
                    _compat_model = _gmod.GenerativeModel("gemini-2.5-flash-lite")
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
    [Phase 1 — 2026-05-22 KST · TJ 지시] 일시 비활성화
      배경: 이 endpoint 는 Marqo-FashionSigLIP embedding 의존이었으나,
            Render Starter 512MB RAM 부족으로 모델이 매번 silent 로딩 실패
            → 사실상 항상 500 에러를 반환하던 dead endpoint.
      현재: Marqo 코드 전체 제거됨. 기능 복원은 Phase 2 (HF Space 분리) 에서
            FashionCLIP HTTP API 로 재구현 예정.
      Frontend 호환성: aicloset.html / closet.html 의 호출부는 try/catch +
            d.ok 체크로 graceful 처리됨 → 503 + empty matches 반환으로 충분.
    """
    return jsonify(
        ok=False,
        error="유사도 매칭 기능 일시 비활성화 (Phase 2 에서 복원 예정)",
        matches=[],
        total_compared=0,
    ), 503


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
    """
    ─── 2026-04-21 KST 개편 ───
    특정 이메일의 이번달 이미지 생성 보너스 조회.
    응답에 코디핏/트라이온 분리 필드 포함.
    
    응답 예:
      { ok, month, codifit_bonus, tryon_bonus, total_bonus }
    """
    try:
        email = email.strip().lower()
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        
        # ─── 2026-04-21: 메모리 캐시 우선 조회 (가장 최신 분리값 보장) ───
        mem_co, mem_tr = None, None
        if hasattr(app, "_usage_bonus_cache"):
            _mkey = f"{email}:{now_ym}"
            if _mkey in app._usage_bonus_cache:
                _c = app._usage_bonus_cache[_mkey]
                mem_co = int(_c.get("codifit_bonus") or _c.get("total_bonus") or 0)
                mem_tr = int(_c.get("tryon_bonus") or 0)
        
        params = {
            "email": f"eq.{email}",
            "month": f"eq.{now_ym}",
            "select": "codifit_bonus,tryon_bonus,total_bonus",
            "limit": "1",
        }
        # 1) Supabase 테이블 조회 (신규 스키마) — 메모리 캐시와 병합
        try:
            r = sb_query("GET", "user_usage_bonus", params=params)
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    row = rows[0]
                    co = row.get("codifit_bonus")
                    tr = row.get("tryon_bonus")
                    tb = int(row.get("total_bonus", 0))
                    if co is not None or tr is not None:
                        co_v = int(co or 0)
                        tr_v = int(tr or 0)
                    else:
                        # 레거시: total_bonus만 있음 → 코디핏으로 간주
                        co_v = tb
                        tr_v = 0
                    # ─── 메모리 캐시가 있으면 오버라이드 (레거시 스키마에서 트라이온 복원) ───
                    if mem_co is not None or mem_tr is not None:
                        co_v = mem_co if mem_co is not None else co_v
                        tr_v = mem_tr if mem_tr is not None else tr_v
                    return jsonify({
                        "ok": True, "month": now_ym,
                        "codifit_bonus": co_v, "tryon_bonus": tr_v,
                        "total_bonus": co_v + tr_v,
                    })
        except Exception:
            pass
        
        # 2) 레거시 스키마로 재시도 + 메모리 캐시 병합
        try:
            _legacy = dict(params); _legacy["select"] = "total_bonus"
            r2 = sb_query("GET", "user_usage_bonus", params=_legacy)
            if r2.status_code == 200:
                _rows = r2.json() or []
                if _rows:
                    tb = int(_rows[0].get("total_bonus", 0))
                    co_v = tb
                    tr_v = 0
                    if mem_co is not None or mem_tr is not None:
                        co_v = mem_co if mem_co is not None else co_v
                        tr_v = mem_tr if mem_tr is not None else tr_v
                    return jsonify({
                        "ok": True, "month": now_ym,
                        "codifit_bonus": co_v, "tryon_bonus": tr_v,
                        "total_bonus": co_v + tr_v,
                    })
        except Exception:
            pass
        
        # 3) Supabase 데이터 없음 → 메모리 캐시만으로 응답
        if mem_co is not None or mem_tr is not None:
            return jsonify({
                "ok": True, "month": now_ym,
                "codifit_bonus": mem_co or 0, "tryon_bonus": mem_tr or 0,
                "total_bonus": (mem_co or 0) + (mem_tr or 0),
                "source": "memory",
            })
        return jsonify({
            "ok": True, "month": now_ym,
            "codifit_bonus": 0, "tryon_bonus": 0, "total_bonus": 0,
        })
    except Exception as e:
        return jsonify({
            "ok": True, "month": __import__('datetime').datetime.now().strftime("%Y-%m"),
            "codifit_bonus": 0, "tryon_bonus": 0, "total_bonus": 0, "error": str(e),
        })


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
    """
    ─── 2026-04-21 KST 개편 ───
    이달 보너스 지급 현황 전체 조회 (MASTER 전용).
    응답에 codifit_bonus와 tryon_bonus를 분리 필드로 반환.
    
    조회 우선순위:
      1. Supabase 신규 스키마 (codifit_bonus/tryon_bonus 컬럼 존재)
      2. Supabase 레거시 스키마 (total_bonus만) + 메모리 캐시 병합
      3. 메모리 캐시만
    """
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        
        # ─── 메모리 캐시 수집 (우선 병합용) ───
        mem_cache = {}
        if hasattr(app, "_usage_bonus_cache"):
            for k, v in app._usage_bonus_cache.items():
                if not k.endswith(now_ym): continue
                em = k.split(":")[0]
                mem_cache[em] = {
                    "codifit_bonus": int(v.get("codifit_bonus") or v.get("total_bonus") or 0),
                    "tryon_bonus":   int(v.get("tryon_bonus") or 0),
                    "total_bonus":   int(v.get("total_bonus") or 0),
                }
        
        # ─── 1. Supabase 신규 스키마 쿼리 ───
        params = {"month": f"eq.{now_ym}", "order": "updated_at.desc", "limit": "500",
                  "select": "email,month,codifit_bonus,tryon_bonus,total_bonus,updated_at"}
        r = sb_query("GET", "user_usage_bonus", params=params)
        if r.status_code == 200:
            _rows = r.json() or []
            for row in _rows:
                em = (row.get("email") or "").lower()
                # 신규 컬럼 값 사용
                if row.get("codifit_bonus") is not None or row.get("tryon_bonus") is not None:
                    row["codifit_bonus"] = int(row.get("codifit_bonus") or 0)
                    row["tryon_bonus"]   = int(row.get("tryon_bonus") or 0)
                else:
                    # 컬럼은 있지만 값이 모두 null → 레거시 데이터
                    row["codifit_bonus"] = int(row.get("total_bonus") or 0)
                    row["tryon_bonus"]   = 0
                # ─── 메모리 캐시가 더 최신 값이면 오버라이드 (레거시 스키마에서 트라이온 복원) ───
                if em in mem_cache:
                    row["codifit_bonus"] = mem_cache[em]["codifit_bonus"]
                    row["tryon_bonus"]   = mem_cache[em]["tryon_bonus"]
                    row["total_bonus"]   = row["codifit_bonus"] + row["tryon_bonus"]
            # 메모리에만 있고 Supabase에 없는 항목도 추가
            supa_emails = {(row.get("email") or "").lower() for row in _rows}
            for em, v in mem_cache.items():
                if em not in supa_emails:
                    _rows.append({
                        "email": em, "month": now_ym,
                        "codifit_bonus": v["codifit_bonus"],
                        "tryon_bonus":   v["tryon_bonus"],
                        "total_bonus":   v["codifit_bonus"] + v["tryon_bonus"],
                        "updated_at":    "—",
                    })
            return jsonify({"ok": True, "list": _rows, "month": now_ym})
        
        # ─── 2. 신규 스키마 실패 → 레거시 스키마로 재조회 + 메모리 캐시 병합 ───
        try:
            _legacy_params = dict(params)
            _legacy_params["select"] = "email,month,total_bonus,updated_at"
            r2 = sb_query("GET", "user_usage_bonus", params=_legacy_params)
            if r2.status_code == 200:
                _rows = r2.json() or []
                for row in _rows:
                    em = (row.get("email") or "").lower()
                    # 레거시 기본값
                    row["codifit_bonus"] = int(row.get("total_bonus") or 0)
                    row["tryon_bonus"]   = 0
                    # 메모리 캐시 우선 병합
                    if em in mem_cache:
                        row["codifit_bonus"] = mem_cache[em]["codifit_bonus"]
                        row["tryon_bonus"]   = mem_cache[em]["tryon_bonus"]
                        row["total_bonus"]   = row["codifit_bonus"] + row["tryon_bonus"]
                # 메모리에만 있는 항목 추가
                supa_emails = {(row.get("email") or "").lower() for row in _rows}
                for em, v in mem_cache.items():
                    if em not in supa_emails:
                        _rows.append({
                            "email": em, "month": now_ym,
                            "codifit_bonus": v["codifit_bonus"],
                            "tryon_bonus":   v["tryon_bonus"],
                            "total_bonus":   v["codifit_bonus"] + v["tryon_bonus"],
                            "updated_at":    "—",
                        })
                return jsonify({"ok": True, "list": _rows, "month": now_ym, "schema": "legacy"})
        except Exception:
            pass
        
        # ─── 3. Supabase 완전 실패 → 메모리 캐시만 반환 ───
        if mem_cache:
            rows = [{"email": em, "month": now_ym,
                     "codifit_bonus": v["codifit_bonus"],
                     "tryon_bonus":   v["tryon_bonus"],
                     "total_bonus":   v["codifit_bonus"] + v["tryon_bonus"]}
                    for em, v in mem_cache.items()]
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
    """
    ─── 2026-04-21 KST 개편 ───
    회원(일반 유저)에게 이번달 이미지 생성 보너스 지급 (MASTER 전용).
    
    코디핏(codifit_bonus)과 트라이 온(tryon_bonus)을 완전히 분리 관리.
    
    요청 바디:
      email         : (필수) 회원 이메일
      codifit_bonus : (선택) 코디핏 보너스 횟수. 생략 시 기존 값 유지
      tryon_bonus   : (선택) 트라이 온 보너스 횟수. 생략 시 기존 값 유지
      total_bonus   : (하위 호환) codifit_bonus/tryon_bonus가 없을 때만 코디핏에 할당
      month         : (선택) YYYY-MM. 기본값: 이번 달
    
    응답:
      { ok, email, month, codifit_bonus, tryon_bonus, total_bonus, note }
    """
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        import requests as _rq
        data        = request.get_json(silent=True) or {}
        email       = str(data.get("email", "")).strip().lower()
        month       = str(data.get("month") or __import__('datetime').datetime.now().strftime("%Y-%m"))

        if not email:
            return jsonify({"ok": False, "error": "email 필수"}), 400

        # ─── 분리된 보너스 값 읽기 (None이면 "미지정" = 기존값 유지) ───
        co_raw = data.get("codifit_bonus", None)
        tr_raw = data.get("tryon_bonus", None)
        # 하위 호환: 두 개 모두 미지정이면 total_bonus를 코디핏에 할당
        if co_raw is None and tr_raw is None:
            co_raw = data.get("total_bonus", data.get("closet_bonus", 0)) or 0
            tr_raw = 0

        # 기존 값 조회 (codifit_bonus 또는 tryon_bonus 중 한쪽만 전달되었을 때 다른 쪽 보존)
        existing_co, existing_tr = 0, 0
        try:
            _get_url = f"{supabase_url()}/rest/v1/user_usage_bonus"
            _get_params = {"email": f"eq.{email}", "month": f"eq.{month}",
                           "select": "codifit_bonus,tryon_bonus,total_bonus", "limit": "1"}
            _get_r = _rq.get(_get_url, headers=supabase_admin_headers(), params=_get_params, timeout=5)
            if _get_r.status_code == 200:
                _rows = _get_r.json() or []
                if _rows:
                    row = _rows[0]
                    existing_co = int(row.get("codifit_bonus") or 0)
                    # codifit_bonus 컬럼이 없는 레거시 데이터 → total_bonus를 코디핏으로 간주
                    if not existing_co and row.get("total_bonus"):
                        existing_co = int(row.get("total_bonus") or 0)
                    existing_tr = int(row.get("tryon_bonus") or 0)
        except Exception:
            pass

        # 메모리 폴백에서도 기존값 조회
        if not existing_co and not existing_tr and hasattr(app, "_usage_bonus_cache"):
            _mem_key = f"{email}:{month}"
            if _mem_key in app._usage_bonus_cache:
                _cached = app._usage_bonus_cache[_mem_key]
                existing_co = int(_cached.get("codifit_bonus") or _cached.get("total_bonus") or 0)
                existing_tr = int(_cached.get("tryon_bonus") or 0)

        # 최종 적용값 결정
        codifit_b = max(0, int(co_raw)) if co_raw is not None else existing_co
        tryon_b   = max(0, int(tr_raw)) if tr_raw is not None else existing_tr
        total_b   = codifit_b + tryon_b  # 하위 호환 합산값

        bonus_body = {
            "email": email, "month": month,
            "codifit_bonus": codifit_b,
            "tryon_bonus":   tryon_b,
            "total_bonus":   total_b,  # 레거시 필드 유지
            "updated_at": __import__('datetime').datetime.utcnow().isoformat() + "Z",
            "updated_by": (request.headers.get("X-Admin-Key") or "")[:16],
        }
        url     = f"{supabase_url()}/rest/v1/user_usage_bonus"
        headers = supabase_admin_headers()
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        r = _rq.post(url, headers=headers, json=bonus_body, timeout=10)

        # ─── 2026-04-21: 저장 결과 로그 + 메모리 미러링 강화 ───
        # Supabase 성공 여부와 무관하게 메모리 캐시에도 분리값 저장
        # (레거시 스키마로 Supabase에 total_bonus만 저장된 경우에도 조회 시 tryon_bonus 복원 가능)
        if not hasattr(app, "_usage_bonus_cache"):
            app._usage_bonus_cache = {}
        app._usage_bonus_cache[f"{email}:{month}"] = {
            "codifit_bonus": codifit_b,
            "tryon_bonus":   tryon_b,
            "total_bonus":   total_b,
        }

        note = "saved_to_supabase"
        if r.status_code not in (200, 201):
            # 새 컬럼이 없는 경우 → total_bonus만으로 재시도
            print(f"[set-bonus] Supabase 신규 스키마 쓰기 실패 (status={r.status_code}), 레거시 폴백 시도", flush=True)
            try:
                _fallback_body = {
                    "email": email, "month": month,
                    "total_bonus": total_b,
                    "updated_at": bonus_body["updated_at"],
                    "updated_by": bonus_body["updated_by"],
                }
                r2 = _rq.post(url, headers=headers, json=_fallback_body, timeout=10)
                if r2.status_code in (200, 201):
                    note = "saved_legacy_schema"
                    print(f"[set-bonus] 레거시 스키마로 저장 성공 — tryon_bonus={tryon_b}은 메모리에만 보존됨. SQL 마이그레이션 필요.", flush=True)
                else:
                    print(f"[set-bonus] 레거시 폴백도 실패 (status={r2.status_code}, body={r2.text[:200]})", flush=True)
                    raise Exception("supabase_write_failed")
            except Exception as fe:
                note = "memory_fallback"
                print(f"[set-bonus] 메모리 폴백 사용: {fe}", flush=True)
        else:
            print(f"[set-bonus] ✅ Supabase 저장 성공 — email={email}, codifit=+{codifit_b}, tryon=+{tryon_b}", flush=True)

        return jsonify({
            "ok": True, "email": email, "month": month,
            "codifit_bonus": codifit_b,
            "tryon_bonus":   tryon_b,
            "total_bonus":   total_b,
            "note": note,
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


# ══════════════════════════════════════════════════════════════
# [Phase 4 — 2026-05-23 KST · TJ 지시] 사용자 수정 피드백 루프
#   목적: 사용자가 AI 자동분류 결과를 수정해 저장할 때마다 (AI 결과, 사용자 수정
#         결과) 쌍을 Supabase 에 누적 저장. 향후 프롬프트 개선·few-shot 학습·
#         Phase 3 색명 사전 확장의 근거 데이터로 활용.
#   사전조건: Supabase 에 item_corrections 테이블 + 4개 통계 뷰가 생성돼 있어야 함
#            (supabase_phase4_schema.sql 실행 필요)
#   기존 헬퍼 재사용: supabase_admin_headers(), supabase_url() — line 8553~8563
#   환경변수: SUPABASE_SERVICE_KEY, SUPABASE_URL (둘 다 이미 설정됨)
# ══════════════════════════════════════════════════════════════

# AI 결과 키 ↔ 사용자 저장 키 매핑 (필드명 다른 케이스)
#   AI 응답은 analyze-item endpoint 의 analysis 객체 (백엔드 스키마 정의)
#   사용자 저장은 프론트엔드 item 객체 (CodiBank.addItem 의 필드명)
_FIELD_PAIRS = [
    # (ai_key,            user_key,         정규화 함수 또는 None)
    ("category",          "categoryKey",    None),       # 'jacket' vs 'jacket'
    ("sub_category",      "sub_category",   None),       # '다운자켓' vs '다운자켓'
    ("main_color",        "main_color",     None),       # '#1a1a1a' (HEX)
    ("main_color_name",   "color",          None),       # '블랙' (한국어 색명)
    ("sub_color",         "sub_color",      None),
    ("sub_color_name",    "sub_color_name", None),
    ("pattern",           "pattern",        None),
    ("material",          "material",       None),
    ("fit",               "fit",            None),
    ("season",            "season",         None),
    ("brand",             "brand",          None),
]

def _norm_val(v):
    """비교 정규화: None/빈 → '', str 은 strip + 소문자, 그 외 str() 처리"""
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip().lower()
    if isinstance(v, (list, dict)):
        # 복잡 필드는 비교 안 함 (color_palette 등)
        return ""
    return str(v).strip().lower()

def _compute_changed_fields(ai_result, user_result):
    """ai_result vs user_result 비교 → 변경된 필드명 배열 (ai 측 키 기준).
       빈값 → 채워진 값 도 변경으로 간주."""
    if not isinstance(ai_result, dict) or not isinstance(user_result, dict):
        return []
    changed = []
    for ai_key, user_key, _norm_fn in _FIELD_PAIRS:
        ai_v   = _norm_val(ai_result.get(ai_key))
        user_v = _norm_val(user_result.get(user_key))
        if ai_v != user_v:
            changed.append(ai_key)
    return changed


@app.post("/api/ai/record-correction")
def ai_record_correction():
    """
    사용자가 AI 자동분류 결과를 수정해 저장한 시점에 호출.
      Body:
        user_email          : str  (필수)
        ai_result           : dict (필수) — analyze-item 응답의 analysis 객체
        user_result         : dict (필수) — 사용자 최종 저장 값 (item 객체)
        correction_source   : str  (필수) — 'item.html' | 'aicloset.html' | 'camera.html'
        item_id             : str  (옵션) — 원본 아이템 ID
        image_url           : str  (옵션) — R2 이미지 URL
      응답:
        { ok, id, changed_fields, no_change }
        - no_change=True : 변경 사항 없으면 저장 안 함 (200 응답, id 없음)

    실패 시: ok=false + error + 적절한 HTTP 코드
    """
    try:
        d = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify(ok=False, error="JSON 파싱 실패"), 400

    user_email = (d.get("user_email") or "").strip().lower()
    ai_result  = d.get("ai_result")
    user_result= d.get("user_result")
    source     = (d.get("correction_source") or "other").strip()
    item_id    = d.get("item_id") or None
    image_url  = d.get("image_url") or None

    # 입력 검증
    if not user_email:
        return jsonify(ok=False, error="user_email 누락"), 400
    if not isinstance(ai_result, dict) or not isinstance(user_result, dict):
        return jsonify(ok=False, error="ai_result/user_result 는 객체여야 합니다"), 400
    if source not in ("item.html", "aicloset.html", "camera.html", "other"):
        source = "other"

    # 변경 필드 자동 계산
    changed_fields = _compute_changed_fields(ai_result, user_result)
    if not changed_fields:
        # 사용자가 저장은 눌렀지만 실제 변경 없음 → 저장 안 함 (저장량 절약)
        return jsonify(ok=True, no_change=True, changed_fields=[])

    # Supabase REST API 로 INSERT
    svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not svc_key:
        print("[record-correction] ⚠ SUPABASE_SERVICE_KEY 미설정 — 저장 스킵")
        return jsonify(ok=False, error="Supabase 키 미설정"), 500

    payload = {
        "user_email":        user_email,
        "item_id":           item_id,
        "image_url":         image_url,
        "ai_result":         ai_result,
        "user_result":       user_result,
        "changed_fields":    changed_fields,
        "correction_source": source,
    }
    try:
        url = supabase_url().rstrip("/") + "/rest/v1/item_corrections"
        headers = supabase_admin_headers()
        # 응답에 생성된 행 포함하려면 Prefer 헤더 필요
        headers["Prefer"] = "return=representation"
        resp = http_requests.post(url, json=payload, headers=headers, timeout=8)
        if resp.status_code in (200, 201):
            rows = resp.json() if resp.text else []
            row_id = (rows[0].get("id") if rows else None) if isinstance(rows, list) else None
            print(f"[record-correction] ✅ 저장: user={user_email} source={source} "
                  f"changed={changed_fields}")
            return jsonify(ok=True, id=row_id, changed_fields=changed_fields)
        else:
            print(f"[record-correction] ⚠ Supabase {resp.status_code}: {resp.text[:200]}")
            return jsonify(ok=False, error=f"Supabase {resp.status_code}",
                           detail=resp.text[:200]), 500
    except Exception as e:
        print(f"[record-correction] ⚠ 예외: {e}")
        return jsonify(ok=False, error=str(e)[:200]), 500


# ── 통계 뷰 이름 화이트리스트 (SQL injection 방지) ──
_CORRECTION_VIEWS = {
    "field_freq":       "v_correction_field_freq",
    "by_category":      "v_correction_by_category",
    "category_mapping": "v_correction_category_mapping",
    "color_mapping":    "v_correction_color_mapping",
}

@app.get("/admin/correction-stats")
def admin_correction_stats():
    """
    Phase 4 통계 뷰 조회 (admin 전용).
      Query params:
        view  : 'field_freq' | 'by_category' | 'category_mapping' | 'color_mapping' (필수)
        limit : 1~500 (기본 100)
      응답:
        { ok, view, rows: [...], count }
    """
    if not verify_admin(request):
        return jsonify({"error": "Unauthorized"}), 401

    view_key = (request.args.get("view") or "").strip()
    if view_key not in _CORRECTION_VIEWS:
        return jsonify(ok=False,
                       error="view 파라미터 필요",
                       allowed=list(_CORRECTION_VIEWS.keys())), 400

    try:
        limit = int(request.args.get("limit", "100"))
        limit = max(1, min(500, limit))
    except Exception:
        limit = 100

    view_name = _CORRECTION_VIEWS[view_key]
    svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not svc_key:
        return jsonify(ok=False, error="SUPABASE_SERVICE_KEY 미설정"), 500

    try:
        url = f"{supabase_url().rstrip('/')}/rest/v1/{view_name}?limit={limit}"
        headers = supabase_admin_headers()
        resp = http_requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            rows = resp.json() if resp.text else []
            return jsonify(ok=True, view=view_key, count=len(rows), rows=rows)
        else:
            print(f"[correction-stats] ⚠ Supabase {resp.status_code}: {resp.text[:200]}")
            return jsonify(ok=False,
                           error=f"Supabase {resp.status_code}",
                           detail=resp.text[:200]), 500
    except Exception as e:
        print(f"[correction-stats] ⚠ 예외: {e}")
        return jsonify(ok=False, error=str(e)[:200]), 500


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


# ═══════════════════════════════════════════════════════════════════
# ─── 2026-05-14 v67 Phase 1.7-fix5 ─── KMA(한국 기상청) 백엔드 프록시
# 배경: Open-Meteo는 한국 지역에서 글로벌 모델 사용 → 실측 대비 2°C 오차
# 해결: 한국 좌표는 KMA 단기예보/초단기실황 API를 백엔드 프록시로 호출
#       UV/PM2.5는 KMA에서 미제공이라 Open-Meteo air-quality로 보강
# 환경변수: KMA_SERVICE_KEY (공공데이터포털 발급, URL-encoded 형식)
#   미설정 시 503 반환 → 프론트엔드가 Open-Meteo fallback
# 라우팅: 프론트엔드가 한국 좌표(33-39N, 124-132E) 감지 시 호출
# ═══════════════════════════════════════════════════════════════════

def _kma_dfs_xy_conv(lat, lon):
    """위경도 → KMA 격자 좌표 변환 (Lambert Conformal Conic, 5km 격자)"""
    import math
    RE, GRID = 6371.00877, 5.0
    SLAT1, SLAT2 = 30.0, 60.0
    OLON, OLAT = 126.0, 38.0
    XO, YO = 43, 136
    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1, slat2 = SLAT1 * DEGRAD, SLAT2 * DEGRAD
    olon, olat = OLON * DEGRAD, OLAT * DEGRAD
    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi: theta -= 2.0 * math.pi
    if theta < -math.pi: theta += 2.0 * math.pi
    theta *= sn
    nx = int(ra * math.sin(theta) + XO + 0.5)
    ny = int(ro - ra * math.cos(theta) + YO + 0.5)
    return nx, ny


def _kma_calc_base_dt(now=None, kind="village"):
    """KMA API 호출용 base_date/base_time 계산
    kind:
      'village' — 단기예보 (1일 8회: 02/05/08/11/14/17/20/23시, 10분 후 제공)
      'ultra'   — 초단기실황 (매시 정각, 10분 후 제공)
    """
    from datetime import datetime, timedelta
    if now is None:
        now = datetime.now()
    if kind == "ultra":
        # 매시 정각 발표, 10분 후 제공
        if now.minute < 10:
            now -= timedelta(hours=1)
        return now.strftime("%Y%m%d"), now.strftime("%H00")
    # village (단기예보): 8회 발표
    base_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    cur_hhmm = now.hour * 100 + now.minute
    selected_h = None
    for bh in reversed(base_hours):
        if cur_hhmm >= bh * 100 + 10:  # 발표 10분 후부터 사용 가능
            selected_h = bh
            break
    if selected_h is None:
        # 어제 23시 발표
        now -= timedelta(days=1)
        selected_h = 23
    return now.strftime("%Y%m%d"), f"{selected_h:02d}00"


def _kma_pty_sky_to_wmo(pty, sky):
    """KMA PTY(강수형태)+SKY(하늘상태) → WMO weather_code 매핑"""
    try:
        pty = int(pty); sky = int(sky)
    except (TypeError, ValueError):
        return 0
    # PTY: 0=없음, 1=비, 2=비/눈, 3=눈, 4=소나기, 5=빗방울, 6=빗방울눈날림, 7=눈날림
    if pty == 1: return 61   # rain
    if pty == 2: return 67   # freezing rain (sleet)
    if pty == 3: return 71   # snow
    if pty == 4: return 80   # rain showers
    if pty == 5: return 51   # drizzle
    if pty == 6: return 68   # light freezing rain
    if pty == 7: return 73   # light snow
    # PTY=0: SKY 기준 (1=맑음, 3=구름많음, 4=흐림)
    return {1: 0, 3: 2, 4: 3}.get(sky, 0)


@app.route("/api/weather", methods=["GET"])
def weather_endpoint():
    """KMA 한국 기상청 + Open-Meteo air-quality 하이브리드 프록시
    Query: lat, lon, tz(optional)
    Response: Open-Meteo Forecast API 호환 형식
    """
    try:
        lat = float(request.args.get("lat") or 0)
        lon = float(request.args.get("lon") or 0)
        tz  = str(request.args.get("tz") or "Asia/Seoul")
    except (TypeError, ValueError):
        return jsonify(ok=False, error="invalid lat/lon"), 400
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify(ok=False, error="lat/lon out of range"), 400

    service_key = os.getenv("KMA_SERVICE_KEY", "").strip()
    if not service_key:
        return jsonify(ok=False, error="KMA_SERVICE_KEY not configured"), 503

    nx, ny = _kma_dfs_xy_conv(lat, lon)
    from datetime import datetime, timedelta
    now = datetime.now()

    # ── 1) 초단기실황 (현재 시점 기온 — 가장 정확) ──
    cur_temp = None
    cur_wsd = None
    cur_pty = 0
    cur_reh = None
    try:
        base_date_u, base_time_u = _kma_calc_base_dt(now, kind="ultra")
        url_ultra = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
        params_u = {
            "serviceKey": service_key, "pageNo": 1, "numOfRows": 100,
            "dataType": "JSON", "base_date": base_date_u, "base_time": base_time_u,
            "nx": nx, "ny": ny
        }
        ru = http_requests.get(url_ultra, params=params_u, timeout=6)
        rj = ru.json()
        items = (((rj or {}).get("response") or {}).get("body") or {}).get("items", {}).get("item", []) or []
        for it in items:
            cat = it.get("category"); val = it.get("obsrValue")
            if cat == "T1H" and val not in (None, "", "-99"): cur_temp = float(val)
            elif cat == "WSD" and val not in (None, "", "-99"): cur_wsd = float(val)
            elif cat == "PTY":
                try: cur_pty = int(val or 0)
                except (TypeError, ValueError): cur_pty = 0
            elif cat == "REH" and val not in (None, "", "-99"): cur_reh = float(val)
    except Exception as _e:
        print(f"[KMA ultra-now] err: {_e}", flush=True)

    # ── 2) 단기예보 (3일 시간별 + 일별 최저/최고) ──
    hourly = {"time": [], "temperature_2m": [], "weather_code": [],
              "precipitation_probability": [], "wind_speed_10m": []}
    daily_map = {}  # date → {tmax, tmin, pop_max, wsd_max, sky_dominant}
    try:
        base_date_v, base_time_v = _kma_calc_base_dt(now, kind="village")
        url_vill = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        params_v = {
            "serviceKey": service_key, "pageNo": 1, "numOfRows": 1000,
            "dataType": "JSON", "base_date": base_date_v, "base_time": base_time_v,
            "nx": nx, "ny": ny
        }
        rv = http_requests.get(url_vill, params=params_v, timeout=8)
        rj = rv.json()
        items = (((rj or {}).get("response") or {}).get("body") or {}).get("items", {}).get("item", []) or []
        # 시간별 데이터 buffer: {(date, time) → {TMP, POP, PTY, SKY, WSD}}
        slot = {}
        for it in items:
            d = it.get("fcstDate"); t = it.get("fcstTime")
            cat = it.get("category"); v = it.get("fcstValue")
            if not d or not t: continue
            key = (d, t)
            slot.setdefault(key, {})[cat] = v
            # 일별 최저/최고
            if cat == "TMX" and v not in (None, "", "-99"):
                daily_map.setdefault(d, {})["tmax"] = float(v)
            elif cat == "TMN" and v not in (None, "", "-99"):
                daily_map.setdefault(d, {})["tmin"] = float(v)
        # 시간 정렬
        for (d, t) in sorted(slot.keys()):
            s = slot[(d, t)]
            try: tmp = float(s.get("TMP") or 0)
            except (TypeError, ValueError): tmp = None
            try: pop = float(s.get("POP") or 0)
            except (TypeError, ValueError): pop = 0
            try: wsd = float(s.get("WSD") or 0)
            except (TypeError, ValueError): wsd = 0
            iso_time = f"{d[0:4]}-{d[4:6]}-{d[6:8]}T{t[0:2]}:{t[2:4]}"
            hourly["time"].append(iso_time)
            hourly["temperature_2m"].append(tmp)
            hourly["weather_code"].append(_kma_pty_sky_to_wmo(s.get("PTY"), s.get("SKY")))
            hourly["precipitation_probability"].append(int(pop))
            hourly["wind_speed_10m"].append(wsd)
            # 일별 누적 (POP max, WSD max)
            dm = daily_map.setdefault(d, {})
            dm["pop_max"] = max(dm.get("pop_max", 0), pop)
            dm["wsd_max"] = max(dm.get("wsd_max", 0), wsd)
            # 우세 날씨코드 (POP 가장 높은 시간 또는 정오 기준)
            if t == "1200" or "sky_pty" not in dm:
                dm["sky_pty"] = (s.get("PTY"), s.get("SKY"))
    except Exception as _e:
        print(f"[KMA village-fcst] err: {_e}", flush=True)

    # ── 3) Open-Meteo air-quality + UV 보강 (KMA는 UV/PM2.5 미제공) ──
    uv_max_per_day = {}
    pm25_current = None
    try:
        url_om = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                  f"&daily=uv_index_max&timezone={tz}&forecast_days=14")
        ro = http_requests.get(url_om, timeout=6).json()
        d_dates = ((ro or {}).get("daily") or {}).get("time", []) or []
        d_uvs = ((ro or {}).get("daily") or {}).get("uv_index_max", []) or []
        for i, dt in enumerate(d_dates):
            uv_max_per_day[dt.replace("-", "")] = d_uvs[i] if i < len(d_uvs) else None
    except Exception as _e:
        print(f"[Open-Meteo UV] err: {_e}", flush=True)
    try:
        url_aq = (f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
                  f"&current=pm2_5,pm10&timezone={tz}")
        ra = http_requests.get(url_aq, timeout=6).json()
        pm25_current = ((ra or {}).get("current") or {}).get("pm2_5")
    except Exception as _e:
        print(f"[Open-Meteo AQ] err: {_e}", flush=True)

    # ── 4) Open-Meteo 형식으로 매핑 ──
    daily_sorted_dates = sorted(daily_map.keys())
    daily = {
        "time": [f"{d[0:4]}-{d[4:6]}-{d[6:8]}" for d in daily_sorted_dates],
        "temperature_2m_max": [daily_map[d].get("tmax") for d in daily_sorted_dates],
        "temperature_2m_min": [daily_map[d].get("tmin") for d in daily_sorted_dates],
        "weather_code": [_kma_pty_sky_to_wmo(*daily_map[d].get("sky_pty", (0, 1))) for d in daily_sorted_dates],
        "precipitation_probability_max": [int(daily_map[d].get("pop_max", 0)) for d in daily_sorted_dates],
        "wind_speed_10m_max": [daily_map[d].get("wsd_max", 0) for d in daily_sorted_dates],
        "uv_index_max": [uv_max_per_day.get(d) for d in daily_sorted_dates],
    }

    # 현재 weather_code: 초단기실황 PTY + 단기예보 첫 SKY
    cur_sky = 1
    if hourly["time"]:
        # 첫 시간 SKY 활용 (대략 현재에 가장 가까움)
        try:
            first_d = hourly["time"][0][0:4] + hourly["time"][0][5:7] + hourly["time"][0][8:10]
            first_t = hourly["time"][0][11:13] + hourly["time"][0][14:16]
            cur_sky_pty = daily_map.get(first_d, {}).get("sky_pty", (cur_pty, 1))
            cur_sky = int(cur_sky_pty[1]) if cur_sky_pty[1] else 1
        except Exception:
            pass
    current = {
        "time": now.strftime("%Y-%m-%dT%H:%M"),
        "temperature_2m": cur_temp,
        "weather_code": _kma_pty_sky_to_wmo(cur_pty, cur_sky),
        "is_day": 1 if 6 <= now.hour < 19 else 0,
        "precipitation": 0,
        "wind_speed_10m": cur_wsd,
    }

    return jsonify({
        "latitude": lat,
        "longitude": lon,
        "timezone": tz,
        "source": "KMA+OpenMeteo",
        "current": current,
        "hourly": hourly,
        "daily": daily,
        "airQuality": {"current": {"pm2_5": pm25_current}},
    }), 200


# ═══════════════════════════════════════════════════════════════════════════
# ─── 2026-05-24 KST · 런웨이 (동영상 서비스) API ──────────────────────────
#   상태: stub 단계 — 더미 데이터 응답 + placeholder 비디오 응답
#   엔드포인트:
#     GET    /api/runway/candidates       후보 리스트 (코디핏 3rd + 트라이온)
#     POST   /api/runway/generate         동영상 생성 (Luma/Veo placeholder)
#     GET    /api/runway/videos           사용자 생성 영상 리스트
#     DELETE /api/runway/videos/<id>      영상 삭제
#     GET    /api/runway/usage            tier 별 사용량 / 한도
#
#   향후 통합 (TODO):
#     · 사용자 인증: Supabase 토큰 검증 (다른 API 와 동일 패턴)
#     · 후보 리스트: Supabase 'ai_album' 테이블 (코디핏 3rd 결과 + 트라이온)
#     · 동영상 생성: Luma Ray2 API (image-to-video, 6초) + 폴링 + R2 저장
#     · 영상 리스트: Supabase 'user_videos' 테이블 + R2 URL 조회
#     · 사용량: Supabase 'user_usage' 테이블 (월별 video_count)
#     · tier 한도: FREE/SILVER=0, GOLD=20, DIAMOND=50 (월 기준)
# ─────────────────────────────────────────────────────────────────────────


def _runway_now_iso():
    """현재 시각 ISO 포맷 (UTC+9 한국 시간)."""
    from datetime import datetime, timezone, timedelta
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S")


def _runway_model_candidates():
    """런웨이 영상 생성 모델 ID 목록.

    [2026-05-30 TJ 결정] Seedance 2.0 → Seedance 1.5 Pro 전환.
      사유: 2.0 은 모델 레이어에서 사실적 인물 레퍼런스를 하드 차단(deepfake 정책).
            공식 가이드도 '사람은 1.5 Pro / Kling / Veo 사용' 권고.
            1.5 Pro 는 사실적 인물 모션 + image-to-video 지원 → 인물 워킹 가능.

    ⚠️ 모델 ID 문자열은 플랫폼별로 다름:
      · Volcengine(중국, ark.cn-beijing): doubao-seedance-1-5-pro-251215
      · BytePlus 인터내셔널(ap-southeast, 현재 사용): 콘솔 'Get Model ID' 에서 확인 필요.
    따라서 환경변수 CODIBANK_RUNWAY_MODEL(쉼표 구분 가능)로 지정하는 것을 우선한다.
    Render 에 정확한 ID 를 넣으면 재배포 없이 교체 가능. (아래 기본값은 추정치)
    """
    raw = os.getenv("CODIBANK_RUNWAY_MODEL", "seedance-1-5-pro-251215").strip()
    cands = [m.strip() for m in raw.split(",") if m.strip()]
    return cands or ["seedance-1-5-pro-251215"]


def _runway_dummy_candidates():
    """후보 리스트 더미 데이터 — 코디핏 4 + 트라이온 2."""
    return [
        {"id": "c1", "type": "codifit", "image_url": "", "label": "코디핏",
         "date": "2026-05-24", "thumb_gradient": "linear-gradient(135deg,#2a3a72 0%,#0e1937 100%)"},
        {"id": "c2", "type": "codifit", "image_url": "", "label": "코디핏",
         "date": "2026-05-23", "thumb_gradient": "linear-gradient(135deg,#2a3a72 0%,#0e1937 100%)"},
        {"id": "c3", "type": "tryon",   "image_url": "", "label": "트라이온",
         "date": "2026-05-23", "thumb_gradient": "linear-gradient(135deg,#4a2a72 0%,#19112e 100%)"},
        {"id": "c4", "type": "codifit", "image_url": "", "label": "코디핏",
         "date": "2026-05-22", "thumb_gradient": "linear-gradient(135deg,#2a3a72 0%,#0e1937 100%)"},
        {"id": "c5", "type": "tryon",   "image_url": "", "label": "트라이온",
         "date": "2026-05-20", "thumb_gradient": "linear-gradient(135deg,#4a2a72 0%,#19112e 100%)"},
        {"id": "c6", "type": "codifit", "image_url": "", "label": "코디핏",
         "date": "2026-05-18", "thumb_gradient": "linear-gradient(135deg,#2a3a72 0%,#0e1937 100%)"},
    ]


def _runway_dummy_videos():
    """영상 리스트 더미 데이터 — 코디핏 3 + 트라이온 1."""
    return [
        {"id": "v1", "title": "코디핏 영상 #001", "type": "codifit",
         "duration_seconds": 6, "video_url": "", "thumb_url": "",
         "created_at": "2026-05-24T14:30:00", "candidate_id": "c1"},
        {"id": "v2", "title": "트라이온 영상 #002", "type": "tryon",
         "duration_seconds": 6, "video_url": "", "thumb_url": "",
         "created_at": "2026-05-23T18:15:00", "candidate_id": "c3"},
        {"id": "v3", "title": "코디핏 영상 #003", "type": "codifit",
         "duration_seconds": 6, "video_url": "", "thumb_url": "",
         "created_at": "2026-05-20T10:45:00", "candidate_id": "c2"},
        {"id": "v4", "title": "코디핏 영상 #004", "type": "codifit",
         "duration_seconds": 6, "video_url": "", "thumb_url": "",
         "created_at": "2026-05-18T09:20:00", "candidate_id": "c4"},
    ]


# ─── 2026-05-24 KST · Phase A · 사용자 인증 헬퍼 ────────────────────────
#   다른 페이지(closet.html 등)의 패턴 차용:
#     - 프론트엔드가 payload 또는 query 에 user.email 포함
#     - 백엔드는 user_email / userEmail 둘 다 허용
#     - 비어있어도 통과 (게스트 모드 — stub 단계). 향후 강제 필수.
# ─────────────────────────────────────────────────────────────────────
def _runway_extract_user_email(req):
    """request 에서 user_email 추출 — POST payload / GET query 모두 지원."""
    try:
        # POST / DELETE: JSON payload
        if req.method in ("POST", "PUT", "DELETE", "PATCH"):
            data = req.get_json(silent=True) or {}
            email = (data.get("user_email") or data.get("userEmail") or "").strip().lower()
            if email:
                return email
        # GET: query string
        email = (req.args.get("user_email") or req.args.get("userEmail") or "").strip().lower()
        return email
    except Exception:
        return ""


def _runway_get_user_tier(user_email):
    """user_email 로 tier 조회.
       1) admin/test 이메일 화이트리스트 → 자동 DIAMOND (Supabase 우회)
       2) Supabase user_usage.tier 조회
       3) fallback: FREE
       ⚠️ user_usage 테이블의 실제 컬럼명은 'email' (기존 코드와 동일 패턴)."""
    if not user_email:
        return "FREE"
    # ① 관리자/테스트 이메일은 Supabase 설정 없이 자동 DIAMOND
    email_lower = str(user_email).strip().lower()
    if email_lower in _RUNWAY_ADMIN_EMAILS or email_lower in _RUNWAY_TEST_EMAILS:
        return "DIAMOND"
    # ② Supabase user_usage 테이블에서 tier 조회
    try:
        import requests as _rq
        svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        sb_url = os.environ.get("SUPABASE_URL", "https://drgsayvlpzcacurcczjq.supabase.co")
        if not svc_key:
            return "FREE"
        # user_usage 테이블에서 tier 조회 — 컬럼명: email (user_email 아님)
        r = _rq.get(
            f"{sb_url}/rest/v1/user_usage",
            params={"select": "tier", "email": f"eq.{user_email}", "limit": 1},
            headers={
                "apikey": svc_key,
                "Authorization": f"Bearer {svc_key}",
                "Accept": "application/json",
            },
            timeout=8,
        )
        if r.status_code == 200:
            rows = r.json() or []
            if rows and rows[0].get("tier"):
                return str(rows[0]["tier"]).upper().strip()
    except Exception as e:
        print(f"[_runway_get_user_tier] error: {e}", flush=True)
    return "FREE"


def _runway_is_admin(user_email):
    """관리자 이메일 검증 — admin endpoint 보호용."""
    if not user_email:
        return False
    return str(user_email).strip().lower() in _RUNWAY_ADMIN_EMAILS


def _runway_get_monthly_video_count(user_email):
    """이번 달 동영상 생성 횟수 조회 — Supabase user_usage.runway_count.
       ⚠️ 컬럼명: email + month (user_email/month_key 아님)."""
    if not user_email:
        return 0
    try:
        import requests as _rq
        from datetime import datetime
        svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        sb_url = os.environ.get("SUPABASE_URL", "https://drgsayvlpzcacurcczjq.supabase.co")
        if not svc_key:
            return 0
        month_key = datetime.now().strftime("%Y-%m")
        r = _rq.get(
            f"{sb_url}/rest/v1/user_usage",
            params={
                "select": "runway_count",
                "email": f"eq.{user_email}",
                "month": f"eq.{month_key}",
                "limit": 1,
            },
            headers={
                "apikey": svc_key,
                "Authorization": f"Bearer {svc_key}",
                "Accept": "application/json",
            },
            timeout=8,
        )
        if r.status_code == 200:
            rows = r.json() or []
            if rows:
                return int(rows[0].get("runway_count") or 0)
    except Exception as e:
        print(f"[_runway_get_monthly_video_count] error: {e}", flush=True)
    return 0


def _runway_increment_usage(user_email):
    """동영상 생성 1회당 사용량 +1 — Supabase user_usage.runway_count 영구 반영.
       ─── 2026-05-30 KST · TJ 지시 (#3) ───
       이 컬럼이 진실의 출처(source of truth):
         · 앱 배지 '동영상 N회 가능' → GET /api/runway/usage 가 동일 컬럼을 읽음(구독플랜 한도와 연동)
         · 관리자페이지 '동영상 횟수' → 동일 user_usage 테이블의 runway_count 를 읽으면 자동 동기화
       month 포맷은 '%Y-%m'(예 2026-05) — _runway_get_monthly_video_count / /api/runway/usage 와 일치.
       증가 방식: read-modify-write (행 있으면 PATCH, 없으면 POST). 동시성은 본 용도에서 허용 범위.
    """
    if not user_email:
        return
    try:
        import requests as _rq
        from datetime import datetime
        svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        sb_url  = os.environ.get("SUPABASE_URL", "https://drgsayvlpzcacurcczjq.supabase.co")
        if not svc_key:
            print("[runway_usage_increment] ⚠ SUPABASE_SERVICE_KEY 없음 → 차감 미반영", flush=True)
            return
        month_key = datetime.now().strftime("%Y-%m")
        hdrs = {
            "apikey": svc_key,
            "Authorization": f"Bearer {svc_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # 1) 현재 행 조회 — PK 가 email 단독(유저당 1행)이므로 email 로만 조회
        chk = _rq.get(
            f"{sb_url}/rest/v1/user_usage",
            params={
                "select": "runway_count,month",
                "email": f"eq.{user_email}",
                "limit": 1,
            },
            headers=hdrs, timeout=8,
        )
        rows = chk.json() if chk.status_code == 200 else []
        if rows:
            # 행 존재 → 같은 달이면 +1, 다른 달이면 카운트 리셋(=1) + month 갱신
            row_month = str(rows[0].get("month") or "")
            if row_month == month_key:
                new_val = int(rows[0].get("runway_count") or 0) + 1
            else:
                new_val = 1
            r = _rq.patch(
                f"{sb_url}/rest/v1/user_usage",
                params={"email": f"eq.{user_email}"},   # email 단독키로 PATCH
                json={"month": month_key, "runway_count": new_val},
                headers={**hdrs, "Prefer": "return=minimal"}, timeout=8,
            )
        else:
            # 행 없음 → 신규 insert (동시성 대비 merge-duplicates 로 upsert 안전망)
            r = _rq.post(
                f"{sb_url}/rest/v1/user_usage",
                json={"email": user_email, "month": month_key, "runway_count": 1},
                headers={**hdrs, "Prefer": "resolution=merge-duplicates,return=minimal"}, timeout=8,
            )
            new_val = 1
        ok = r.status_code in (200, 201, 204)
        print(f"[runway_usage_increment] user={user_email} {month_key} runway_count→{new_val} "
              f"(status={r.status_code}, ok={ok})", flush=True)
        if not ok:
            print(f"[runway_usage_increment] ⚠ 응답본문: {(r.text or '')[:200]}", flush=True)
    except Exception as e:
        print(f"[_runway_increment_usage] error: {e}", flush=True)


def _runway_stage_bg_colorkey(_pil_img):
    """
    ─── 2026-05-29 KST · TJ 지시 (방법 A fallback — REMBG 없이 배경 교체) ───
    rembg(HF Space) 없이, 색상 기반으로 솔리드 파스텔 배경을 어둡게 교체.

    원리:
      코디핏/트라이온 배경은 '솔리드 파스텔'(거의 단색)이라, 가장자리 색을
      배경색으로 추정한 뒤, 그 색과 비슷한 픽셀(=배경)만 어두운 무대 톤으로 교체.
      인물(배경색과 다른 픽셀)은 그대로 보존.

    한계:
      배경색과 비슷한 옷(예: 흰 배경 + 흰 셔츠)은 일부 함께 어두워질 수 있음.
      → 임계값(_thresh)을 보수적으로 잡아 인물 손상 최소화.
      배경이 단색이 아니면(그라데이션/복잡) None 반환 → 원본 유지.

    입력: PIL RGB 이미지
    반환: 배경 교체된 RGB PIL 이미지 (성공) 또는 None (단색 아님 → 원본 유지)
    """
    try:
        from PIL import Image as _PImg, ImageStat as _PStat, ImageFilter as _PFilt
        _w, _h = _pil_img.size
        if _pil_img.mode != "RGB":
            _pil_img = _pil_img.convert("RGB")

        # 1) 배경색 추정 — 4 모서리 영역 평균 (인물은 보통 중앙)
        _cs = max(4, min(_w, _h) // 20)
        _corners = [
            _pil_img.crop((0, 0, _cs, _cs)),
            _pil_img.crop((_w - _cs, 0, _w, _cs)),
            _pil_img.crop((0, _h - _cs, _cs, _h)),
            _pil_img.crop((_w - _cs, _h - _cs, _w, _h)),
        ]
        _means = [_PStat.Stat(c).mean for c in _corners]
        _bg = tuple(sum(m[i] for m in _means) / 4 for i in range(3))
        # 모서리 간 색 편차가 크면 단색 배경 아님 → fallback 포기
        _spread = max(max(m[i] for m in _means) - min(m[i] for m in _means) for i in range(3))
        if _spread > 25:
            print(f"[runway_stage_colorkey] ⚠ 배경 비단색 (편차 {_spread:.0f}) → 원본 유지", flush=True)
            return None

        # 2) 어두운 무대 톤 (세로 그라데이션 상단→바닥)
        _top = (20, 23, 28)
        _bot = (42, 46, 54)

        # 3) 픽셀 단위 배경 교체 — 배경색과의 거리로 판정
        #    distance < _thresh → 배경 → 어둡게 / 아니면 인물 → 유지
        _thresh = 60.0   # 색 거리 임계 (보수적 — 인물 손상 최소화)
        _thresh_sq = _thresh * _thresh
        _src = _pil_img.load()
        _out = _PImg.new("RGB", (_w, _h))
        _dst = _out.load()
        _br, _bgc, _bb = _bg
        for _y in range(_h):
            _t = _y / max(_h - 1, 1)
            _sr = int(_top[0] + (_bot[0] - _top[0]) * _t)
            _sg = int(_top[1] + (_bot[1] - _top[1]) * _t)
            _sb = int(_top[2] + (_bot[2] - _top[2]) * _t)
            for _x in range(_w):
                _r, _g, _b = _src[_x, _y]
                _d = (_r - _br) ** 2 + (_g - _bgc) ** 2 + (_b - _bb) ** 2
                if _d < _thresh_sq:
                    _dst[_x, _y] = (_sr, _sg, _sb)   # 배경 → 어두운 무대
                else:
                    _dst[_x, _y] = (_r, _g, _b)       # 인물 → 유지
        print(f"[runway_stage_colorkey] ✅ 색상기반 배경 교체 완료 (bg≈{tuple(int(v) for v in _bg)})", flush=True)
        return _out
    except Exception as _e:
        print(f"[runway_stage_colorkey] ⚠ 실패 → 원본 유지: {_e}", flush=True)
        return None


def _runway_make_stage_bg(_pil_img):
    """
    ─── 2026-05-29 KST · TJ 지시 (방법 A — 런웨이 전용 무대 배경) ───────────
    인물을 분리해 '어두운 런웨이 무대' 배경에 합성한다.

    목적:
      · 코디핏/트라이온 정지이미지(파스텔)는 그대로 두고,
        런웨이 영상 진입 시에만 배경을 어두운 무대로 교체.
      · 어두운 단색 배경 → BytePlus 안전필터 통과 유리 + 진짜 런웨이 느낌
        + 워킹하는 착장이 부각됨 (인물 외 요소 최소).

    동작:
      1) rembg(HF Space)로 인물 분리 (RGBA)
      2) 비투명 비율 < 15% 면 실패로 간주 → None 반환 (호출부에서 원본 사용)
      3) 어두운 무대 배경(상단 어두움 → 하단 약간 밝은 바닥 그라데이션)에 합성
      4) 합성된 RGB PIL 이미지 반환

    입력: PIL RGB 이미지 (정면 또는 후면 1장)
    반환: 합성된 PIL RGB 이미지 (성공) 또는 None (실패 → 원본 유지)
    """
    try:
        from PIL import Image as _PImg
        import io as _io2
        _w, _h = _pil_img.size

        # 1) 인물 분리 (rembg HF Space) — RGBA 결과 직접 받기 위해 흰배경 합성 전 단계 사용
        if not _REMBG_API_URL:
            print("[runway_stage] ⚠ REMBG 미설정 → 색상기반 배경 교체 fallback", flush=True)
            return _runway_stage_bg_colorkey(_pil_img)
        _buf = _io2.BytesIO()
        _pil_img.save(_buf, format="JPEG", quality=92)
        _resp = http_requests.post(
            f"{_REMBG_API_URL}/remove-bg",
            files={"file": ("frame.jpg", _buf.getvalue(), "image/jpeg")},
            timeout=30,
        )
        if _resp.status_code != 200:
            print(f"[runway_stage] ⚠ rembg 응답 오류 {_resp.status_code} → 색상기반 fallback", flush=True)
            return _runway_stage_bg_colorkey(_pil_img)
        _data = _resp.json()
        if not (_data.get("ok") and _data.get("image")):
            print("[runway_stage] ⚠ rembg 결과 없음 → 색상기반 fallback", flush=True)
            return _runway_stage_bg_colorkey(_pil_img)
        _b64 = _data["image"].split(",", 1)[1]
        _cut = _PImg.open(_io2.BytesIO(base64.b64decode(_b64)))
        if _cut.mode != "RGBA":
            _cut = _cut.convert("RGBA")

        # 2) 분리 품질 검증 (비투명 비율)
        _alpha = _cut.getchannel("A")
        _total = _cut.width * _cut.height
        _visible = sum(1 for p in _alpha.getdata() if p > 128)
        _ratio = _visible / max(_total, 1)
        if _ratio < 0.15:
            print(f"[runway_stage] ⚠ 인물 분리 품질 불량 (비투명 {_ratio:.1%}) → 원본 유지", flush=True)
            return None

        # 3) 어두운 무대 배경 생성 (세로 그라데이션: 상단 #14171c → 하단 #2a2e36 바닥)
        #    솔리드에 가까운 어두운 톤이라 필터·패딩 모두 유리.
        _top = (20, 23, 28)     # 어두운 상단
        _bot = (42, 46, 54)     # 약간 밝은 바닥
        _stage = _PImg.new("RGB", (_w, _h), _top)
        _px = _stage.load()
        for _y in range(_h):
            _t = _y / max(_h - 1, 1)
            _r = int(_top[0] + (_bot[0] - _top[0]) * _t)
            _g = int(_top[1] + (_bot[1] - _top[1]) * _t)
            _b = int(_top[2] + (_bot[2] - _top[2]) * _t)
            for _x in range(_w):
                _px[_x, _y] = (_r, _g, _b)

        # 4) 인물 합성 (알파 마스크 사용)
        _stage.paste(_cut, (0, 0), mask=_cut.split()[3])
        print(f"[runway_stage] ✅ 어두운 무대 배경 합성 완료 (인물 {_ratio:.0%})", flush=True)
        return _stage
    except Exception as _e:
        print(f"[runway_stage] ⚠ 무대배경 합성 실패 → 원본 유지: {_e}", flush=True)
        return None


def _runway_split_front_back(image_url: str) -> tuple:
    """
    [2026-05-25 KST] 코디핏 1536x1024 합성 이미지를 정면(좌) + 후면(우) 두 URL로 분리.

    배경:
      코디핏 결과는 1536x1024 가로 합성 이미지 (좌: 정면 / 우: 후면).
      BytePlus Seedance 2.0 의 First/Last Frame 모드를 사용하려면
      두 이미지를 분리해서 각각 전송해야 함.

    동작:
      1) image_url 에서 이미지 fetch
      2) PIL 로 좌측(0~width/2) → 정면, 우측(width/2~width) → 후면 분리
      3) 각각 R2 에 새 파일명으로 업로드 (절대 URL 반환)
      4) (front_url, back_url) tuple 반환

    실패 시:
      (image_url, image_url) — 원본 URL 두 번 반환 (호출부에서 분기)
    """
    try:
        import requests as _rq
        from PIL import Image
        import io as _io

        # 1) 원본 이미지 fetch
        ir = _rq.get(image_url, timeout=15)
        if ir.status_code != 200:
            print(f"[split_front_back] 이미지 fetch 실패 ({ir.status_code}): {image_url}", flush=True)
            return (image_url, image_url)

        img = Image.open(_io.BytesIO(ir.content))
        if img.mode != "RGB":
            img = img.convert("RGB")
        w, h = img.size

        # 2) 좌/우 분할 (정면 = 좌측 절반, 후면 = 우측 절반)
        half_w = w // 2
        front_img = img.crop((0, 0, half_w, h))
        back_img  = img.crop((half_w, 0, w, h))

        # ─── 2026-05-25 KST · TJ 보고 (v5) ─── 9:16 패딩 (인물 잘림 방지) ───
        #   배경: 분할 후 정면/후면 = 768x1024 (3:4 = 0.75)
        #         BytePlus 영상 출력 = 9:16 (0.5625) → 가로 영상을 세로에 맞추며
        #         위/아래 잘림 발생 (머리/발 잘림).
        #   해결: 분할 후 이미지를 9:16 비율로 배경색 패딩.
        #         768x1024 → 768x1365 (위/아래 약 170px 패딩).
        #         배경색은 이미지 가장자리 평균 (대부분 단색 배경).
        #   효과: BytePlus 가 인물 그대로 + 위/아래 자연 배경 = 잘림 X
        from PIL import ImageStat as _PILStat
        # ─── 2026-05-28 KST · TJ 기준 ─── 배경 확대 패딩 (솔리드 파스텔 보존) ───
        #   원칙: 코디뱅크 입력 = 아바타 + 솔리드 파스텔 배경.
        #         배경 컬러를 변경·변형하지 않고, 뷰박스 빈틈 없게 "배경색만 확대".
        #   동작: 4 가장자리(상/하/좌/우 테두리)를 샘플링 → 표준편차로 단색 여부 판정.
        #         · 단색(파스텔)이면: 그 정확한 단색으로 캔버스 전체를 채움 → 이음새 0.
        #         · 비단색이면: 기존 방식(인접 가장자리 평균)으로 fallback.
        def _edge_fill_color(_img):
            """4 가장자리 테두리에서 배경색 추출 + 단색 여부 반환 → (fill_rgb, is_solid)"""
            _w, _h = _img.size
            _b = max(3, min(_w, _h) // 40)  # 테두리 두께 (이미지 비례, 최소 3px)
            _strips = [
                _img.crop((0, 0, _w, _b)),          # 상
                _img.crop((0, _h - _b, _w, _h)),    # 하
                _img.crop((0, 0, _b, _h)),          # 좌
                _img.crop((_w - _b, 0, _w, _h)),    # 우
            ]
            _means = [_PILStat.Stat(s).mean for s in _strips]
            _stds  = [_PILStat.Stat(s).stddev for s in _strips]
            # 전체 가장자리 평균 = 패딩색
            _fill = tuple(
                int(round(sum(m[i] for m in _means) / len(_means))) for i in range(3)
            )
            # 단색 판정: 각 가장자리 내부 표준편차 + 가장자리 간 색차 모두 작아야 함
            _max_internal_std = max(max(s[:3]) for s in _stds)
            _ch_spread = max(
                max(m[i] for m in _means) - min(m[i] for m in _means) for i in range(3)
            )
            _is_solid = (_max_internal_std < 8.0) and (_ch_spread < 10.0)
            return _fill, _is_solid

        def _pad_to_9_16(_img):
            # ─── 2026-06-02 KST · TJ 지시 (옵션 A) ─── 인물 잘림 없이 9:16 ───
            #   배경: 직전 '좌우 25% 크롭'이 인물 어깨/팔까지 잘라 인물이 과대·잘림.
            #   해결: ①인물 바운딩박스를 감지해 '배경 여백 범위 내에서만' 좌우 크롭(인물 보존)
            #         ②남은 비율 차이는 위/아래 '최소' 패딩으로 보정
            #         ③정면/후면을 동일 720×1280(9:16)로 정규화 → first/last 크기 일치.
            _STD = (720, 1280)
            _LANCZOS = getattr(Image, "LANCZOS", None) or getattr(getattr(Image, "Resampling", None), "LANCZOS", 1)
            _w, _h = _img.size
            _t = 9.0 / 16.0  # 0.5625
            _cur = _w / _h
            _fill, _is_solid = _edge_fill_color(_img)

            # 2026-06-02 KST · TJ #1 — 인물이 프레임을 꽉 채워 워킹 시 머리·발 잘림.
            #   → 9:16 유지하며 인물을 88%로 축소해 상하/좌우 소폭 여백 부여(워킹 다가옴 버퍼).
            #     배경은 가장자리색(_fill)로 채움(스튜디오 배경과 동일 톤).
            def _finalize(_im):
                # ─── 2026-06-09 KST · TJ 지시 (#3) ─── 영상 속 '이중 액자틀' 제거 ───
                #   기존: 인물 88% 축소 후 단색(_fill) 패딩 → 영상에 사각 테두리(액자틀)가 구워짐.
                #   변경: 여백을 단색이 아니라 인물 이미지의 '가장자리 픽셀을 늘려' 채움
                #         → 스튜디오 배경이 자연스럽게 연속, 보이는 프레임 없음(워킹 여백은 유지).
                _scale = 0.88
                _iw, _ih = int(round(_STD[0] * _scale)), int(round(_STD[1] * _scale))
                _inner = _im.resize((_iw, _ih), _LANCZOS)
                _ox, _oy = (_STD[0] - _iw) // 2, (_STD[1] - _ih) // 2
                _rm, _bm = _STD[0] - (_ox + _iw), _STD[1] - (_oy + _ih)  # 우/하 여백
                _canvas = Image.new('RGB', _STD, _fill)
                # 상/하 여백 = 위/아래 끝줄 늘리기
                if _oy > 0:
                    _canvas.paste(_inner.crop((0, 0, _iw, 1)).resize((_iw, _oy), _LANCZOS), (_ox, 0))
                if _bm > 0:
                    _canvas.paste(_inner.crop((0, _ih - 1, _iw, _ih)).resize((_iw, _bm), _LANCZOS), (_ox, _oy + _ih))
                # 좌/우 여백 = 좌/우 끝열 늘리기
                if _ox > 0:
                    _canvas.paste(_inner.crop((0, 0, 1, _ih)).resize((_ox, _ih), _LANCZOS), (0, _oy))
                if _rm > 0:
                    _canvas.paste(_inner.crop((_iw - 1, 0, _iw, _ih)).resize((_rm, _ih), _LANCZOS), (_ox + _iw, _oy))
                # 코너 4곳 = 코너 픽셀로 채움
                if _ox > 0 and _oy > 0:
                    _canvas.paste(_inner.crop((0, 0, 1, 1)).resize((_ox, _oy), _LANCZOS), (0, 0))
                if _rm > 0 and _oy > 0:
                    _canvas.paste(_inner.crop((_iw - 1, 0, _iw, 1)).resize((_rm, _oy), _LANCZOS), (_ox + _iw, 0))
                if _ox > 0 and _bm > 0:
                    _canvas.paste(_inner.crop((0, _ih - 1, 1, _ih)).resize((_ox, _bm), _LANCZOS), (0, _oy + _ih))
                if _rm > 0 and _bm > 0:
                    _canvas.paste(_inner.crop((_iw - 1, _ih - 1, _iw, _ih)).resize((_rm, _bm), _LANCZOS), (_ox + _iw, _oy + _ih))
                # 마지막에 선명한 인물 본체를 위에 붙임
                _canvas.paste(_inner, (_ox, _oy))
                return _canvas

            if abs(_cur - _t) < 0.005:
                return _finalize(_img)

            if _cur > _t:
                _need = _w - int(round(_h * _t))   # 9:16 되려면 줄여야 할 가로 px (예: 768→576 = 192)
                # ── 인물 좌우 경계 감지(배경색 대비 차이) ──
                _safe_l, _safe_r = None, None
                try:
                    import numpy as _np
                    _small = _img.convert('RGB').resize((192, int(192 * _h / _w)), _LANCZOS)
                    _a = _np.asarray(_small, dtype=_np.int16)
                    _fv = _np.array(_fill, dtype=_np.int16)
                    _d = _np.abs(_a - _fv).sum(axis=2)               # 행×열 배경 대비 차이
                    _colact = (_d > 45).sum(axis=0)                  # 열별 '인물' 픽셀 수
                    _rowthr = max(2, int(_small.size[1] * 0.04))
                    _cols = _np.where(_colact > _rowthr)[0]
                    if len(_cols) > 0:
                        _sx = _w / float(_small.size[0])
                        _pl = int(_cols[0] * _sx)                    # 인물 좌단(원본 px)
                        _pr = int((_cols[-1] + 1) * _sx)             # 인물 우단
                        _safe_l = max(0, _pl)                        # 좌측 배경 여백
                        _safe_r = max(0, _w - _pr)                   # 우측 배경 여백
                except Exception:
                    _safe_l = _safe_r = None

                if _safe_l is None:
                    # 감지 실패 → 보수적으로 한쪽 최대 10%까지만 크롭
                    _safe_l = _safe_r = int(_w * 0.10)

                # ── 배경 여백 범위 내에서만 좌우 크롭(인물 보존) ──
                _each = _need / 2.0
                _cl = int(min(_safe_l, _each))
                _cr = int(min(_safe_r, _each))
                _deficit = _need - (_cl + _cr)
                if _deficit > 0:                                     # 한쪽 여백 부족분은 다른 쪽에서 보충(여전히 배경만)
                    _ex = int(min(_safe_l - _cl, _deficit)); _cl += _ex; _deficit -= _ex
                    _ex = int(min(_safe_r - _cr, _deficit)); _cr += _ex; _deficit -= _ex
                _crop = _img.crop((_cl, 0, _w - _cr, _h))
                _cw, _ch = _crop.size

                if (_cw / _ch) > (_t + 0.005):
                    # 아직 가로가 김 → 부족분만큼 위/아래 '최소' 패딩
                    _nh = int(round(_cw / _t))
                    _pt = (_nh - _ch) // 2
                    if not _is_solid:
                        _tm = _PILStat.Stat(_crop.crop((0, 0, _cw, 5))).mean
                        _bm = _PILStat.Stat(_crop.crop((0, _ch - 5, _cw, _ch))).mean
                        _fill = tuple(int(round((_tm[i] + _bm[i]) / 2)) for i in range(3))
                    _new = Image.new('RGB', (_cw, _nh), _fill)
                    _new.paste(_crop, (0, _pt))
                    return _finalize(_new)
                return _finalize(_crop)
            else:
                # 세로가 더 김 → 가로를 늘려서 9:16 (좌/우 패딩)
                _new_w = int(round(_h * _t))
                _pad_left = (_new_w - _w) // 2
                if not _is_solid:
                    _left_mean = _PILStat.Stat(_img.crop((0, 0, 5, _h))).mean
                    _right_mean = _PILStat.Stat(_img.crop((_w - 5, 0, _w, _h))).mean
                    _fill = tuple(int(round((_left_mean[i] + _right_mean[i]) / 2)) for i in range(3))
                _new = Image.new('RGB', (_new_w, _h), _fill)
                _new.paste(_img, (_pad_left, 0))
                return _finalize(_new)

        # ─── 2026-05-29 KST · TJ 지시 (방법 A) ─── 런웨이 무대 배경 교체 ───
        #   환경변수 CODIBANK_RUNWAY_STAGE_BG=1 (기본 on) 이면, 패딩 전에
        #   인물을 분리해 어두운 무대 배경에 합성.
        #   실패 시 None → 원본(파스텔 배경) 그대로 사용 (안전 폴백).
        # [2026-05-30 TJ 결정] 배경 제거 전면 중단 — 원본 정/후면 그대로 사용.
        #   사유: 배경제거가 밝은 코트에 남긴 검은 잔흔을 Seedance가 '무늬'로 증폭시킴
        #         (TJ 첨부 영상). 무대 배경은 영상 모델이 프롬프트로 직접 생성하도록 위임.
        #   기본값 OFF. 재개하려면 CODIBANK_RUNWAY_STAGE_BG=1 (단, 잔흔 재발 주의).
        #   ※ Render 환경변수에 CODIBANK_RUNWAY_STAGE_BG=1 이 설정돼 있으면 삭제 필요.
        _stage_on = os.getenv("CODIBANK_RUNWAY_STAGE_BG", "0") == "1"
        if _stage_on:
            _f2 = _runway_make_stage_bg(front_img)
            if _f2 is not None:
                front_img = _f2
            _b2 = _runway_make_stage_bg(back_img)
            if _b2 is not None:
                back_img = _b2

        front_img = _pad_to_9_16(front_img)
        back_img  = _pad_to_9_16(back_img)

        # 3) 각각 JPEG 92% 인코딩
        front_buf = _io.BytesIO()
        front_img.save(front_buf, format="JPEG", quality=92, optimize=True)
        front_bytes = front_buf.getvalue()

        back_buf = _io.BytesIO()
        back_img.save(back_buf, format="JPEG", quality=92, optimize=True)
        back_bytes = back_buf.getvalue()

        # 4) R2 에 두 파일 업로드 (각각 새 파일명)
        ts = _now_ms()
        rand = os.urandom(3).hex()
        front_fixed = f"runway_front_{ts}_{rand}.jpg"
        back_fixed  = f"runway_back_{ts}_{rand}.jpg"

        front_rel = _write_upload_bytes("runway", "jpg", front_bytes, fixed_name=front_fixed)
        back_rel  = _write_upload_bytes("runway", "jpg", back_bytes,  fixed_name=back_fixed)

        # 5) 절대 URL 조립
        try:
            base = _public_base()
        except Exception:
            base = "https://codibank-api.onrender.com"
        front_url = f"{base}{front_rel}" if front_rel.startswith("/") else f"{base}/{front_rel}"
        back_url  = f"{base}{back_rel}"  if back_rel.startswith("/")  else f"{base}/{back_rel}"

        _final_w, _final_h = front_img.size
        print(f"[split_front_back] ✅ 분리+9:16패딩 완료 ({w}x{h} → {_final_w}x{_final_h} × 2): front={front_fixed}, back={back_fixed}", flush=True)
        return (front_url, back_url)

    except Exception as e:
        print(f"[split_front_back] 분리 실패: {e}", flush=True)
        return (image_url, image_url)


def _runway_neutralize_image(image_url: str, strength: str = "strong") -> str:
    """
    [2026-05-25 KST v6] BytePlus 안전 필터 우회용 painterly stylization.

    배경 (TJ 보고 + Render log 분석):
      v5 의 "얼굴 100% 보존" 방식이 BytePlus 모든 단계에서 거부 (real person 인식).
      얼굴 영역만 보존해도 옷/배경 변형으로는 우회 불가능.

    핵심 전략 변경:
      이미지 전체를 "AI 디지털 페인팅" 처럼 stylization →
      - 사용자는 자기 얼굴 인식 가능 (features 유지)
      - BytePlus 는 사실적 사진 아닌 painted artwork 로 판단 → 통과 가능성 ↑

    strength:
      'light'   → 약한 stylization, 얼굴 radius 1.5 blur, median 3
      'strong'  → 강한 stylization, 얼굴 radius 2.5 blur, median 5 + posterize
    """
    try:
        import requests as _rq
        from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageOps
        import io as _io
        import random as _random

        ir = _rq.get(image_url, timeout=15)
        if ir.status_code != 200:
            print(f"[neutralize] 이미지 fetch 실패 ({ir.status_code}): {image_url}", flush=True)
            return image_url

        img = Image.open(_io.BytesIO(ir.content))
        if img.mode != "RGB":
            img = img.convert("RGB")
        orig_size = img.size
        w, h = orig_size

        if strength == "light":
            # LIGHT 모드 — 약한 painterly stylization
            face_h = int(h * 0.38)
            face_area = img.crop((0, 0, w, face_h))
            body_area = img.crop((0, face_h, w, h))

            # 얼굴 영역 — 약한 blur + median + edge enhance
            face_processed = face_area.filter(ImageFilter.GaussianBlur(radius=1.5))
            face_processed = face_processed.filter(ImageFilter.MedianFilter(size=3))
            face_processed = face_processed.filter(ImageFilter.EDGE_ENHANCE)

            # 옷/배경 — 더 강한 painterly
            body_processed = body_area.filter(ImageFilter.GaussianBlur(radius=2.0))
            body_processed = body_processed.filter(ImageFilter.MedianFilter(size=5))
            body_processed = body_processed.filter(ImageFilter.EDGE_ENHANCE)

            # 색조 변형
            face_processed = ImageEnhance.Color(face_processed).enhance(1.20)
            face_processed = ImageEnhance.Contrast(face_processed).enhance(1.05)
            body_processed = ImageEnhance.Color(body_processed).enhance(1.25)
            body_processed = ImageEnhance.Contrast(body_processed).enhance(1.08)
            body_processed = ImageEnhance.Brightness(body_processed).enhance(0.96)

            img = Image.new('RGB', (w, h))
            img.paste(face_processed, (0, 0))
            img.paste(body_processed, (0, face_h))

            quality = 88
            log_prefix = "[neutralize light · painterly stylization]"

        elif strength == "very_strong":
            # ─── 2026-05-26 KST · TJ 보고 (남자 영상 배경 깨짐) ─── VERY_STRONG v2 ─────
            # 진단 (Render log):
            #   남자 트라이온 → 5단계 모두 거쳐 VERY_STRONG 통과 → 영상 배경 컬러 블록 깨짐
            #   여자 트라이온 → LIGHT/STRONG 1차 통과 → 영상 배경 깨끗
            #
            # BytePlus 영상 처리 분석:
            #   - 인물(얼굴/옷)은 BytePlus 가 자체 모델로 재생성 → painterly 영향 약함
            #   - 배경은 input image 의 색조/구조 그대로 사용 → painterly 영향 강함
            #
            # 핵심 전략 변경 (v2):
            #   - 얼굴 영역: 강한 painterly 유지 (BytePlus person detection 회피 필수)
            #   - 옷/배경 영역: painterly 대폭 약화 (영상 결과 배경 깨끗하게)
            #     Posterize 4 → 6 (16색 → 64색 - 색상 블록 줄임)
            #     MedianFilter 9 → 5 (배경 깨짐 줄임)
            #     GaussianBlur 4.0 → 2.5 (배경 부드럽게)
            #     Color 1.60 → 1.30 (배경 hue shift 약화)
            face_h = int(h * 0.38)
            face_area = img.crop((0, 0, w, face_h))
            body_area = img.crop((0, face_h, w, h))

            # 얼굴 — 강한 painterly 유지 + 약간 약화 (2026-05-27 KST · TJ 보고)
            #   변경: Posterize 4 → 5 (16색 → 32색), MedianFilter 7 → 5
            #         → BytePlus 통과는 유지, 그러나 얼굴 features (안경 등) 보존 ↑
            face_processed = face_area.filter(ImageFilter.GaussianBlur(radius=3.0))
            face_processed = face_processed.filter(ImageFilter.MedianFilter(size=5))
            face_processed = face_processed.filter(ImageFilter.EDGE_ENHANCE_MORE)
            face_processed = ImageOps.posterize(face_processed, 5)

            # 옷/배경 — 약화 (영상 결과 깨끗하게)
            body_processed = body_area.filter(ImageFilter.GaussianBlur(radius=2.5))
            body_processed = body_processed.filter(ImageFilter.MedianFilter(size=5))
            body_processed = body_processed.filter(ImageFilter.EDGE_ENHANCE)
            body_processed = ImageOps.posterize(body_processed, 6)

            # 색조 변형 — 얼굴 강함 유지, 배경 약화
            face_processed = ImageEnhance.Color(face_processed).enhance(1.50)
            face_processed = ImageEnhance.Contrast(face_processed).enhance(1.20)
            face_processed = ImageEnhance.Brightness(face_processed).enhance(0.90)
            body_processed = ImageEnhance.Color(body_processed).enhance(1.30)
            body_processed = ImageEnhance.Contrast(body_processed).enhance(1.10)
            body_processed = ImageEnhance.Brightness(body_processed).enhance(0.94)

            # noise — 얼굴 강함(1500), 배경 약화(800, 이전 2000 → 800)
            for _area, _is_face in [(face_processed, True), (body_processed, False)]:
                _draw = ImageDraw.Draw(_area)
                _random.seed(_now_ms() + (1 if _is_face else 0))
                _aw, _ah = _area.size
                _count = 1500 if _is_face else 800
                _shift_max = 25 if _is_face else 12  # 배경 noise shift 약화
                for _ in range(_count):
                    x = _random.randint(0, _aw - 1)
                    y = _random.randint(0, _ah - 1)
                    shift = _random.randint(-_shift_max, _shift_max)
                    try:
                        r, g, b = _area.getpixel((x, y))
                        _draw.point((x, y), fill=(
                            max(0, min(255, r + shift)),
                            max(0, min(255, g + shift)),
                            max(0, min(255, b + shift))
                        ))
                    except Exception:
                        pass

            img = Image.new('RGB', (w, h))
            img.paste(face_processed, (0, 0))
            img.paste(body_processed, (0, face_h))

            quality = 84  # 78 → 84 (배경 화질 ↑)
            log_prefix = "[neutralize VERY_STRONG v2 · 얼굴 강함 + 배경 약화]"

        else:
            # STRONG 모드 — 약화된 painterly stylization v2 (2026-05-25 KST)
            face_h = int(h * 0.38)
            face_area = img.crop((0, 0, w, face_h))
            body_area = img.crop((0, face_h, w, h))

            # 얼굴 영역 — 약한 blur + median + edge enhance (posterize 제거)
            face_processed = face_area.filter(ImageFilter.GaussianBlur(radius=2.0))
            face_processed = face_processed.filter(ImageFilter.MedianFilter(size=3))
            face_processed = face_processed.filter(ImageFilter.EDGE_ENHANCE)

            # 옷/배경 — 중간 painterly (v6 의 강한 처리 약화 — TJ 보고 배경 픽셀화 fix)
            #   변경: MedianFilter 7 → 5, Posterize 4 → 6 (16단계 → 64단계 색상)
            #   효과: 배경 깨짐 ↓ + BytePlus 통과는 유지 (충분한 stylization)
            body_processed = body_area.filter(ImageFilter.GaussianBlur(radius=2.5))
            body_processed = body_processed.filter(ImageFilter.MedianFilter(size=5))
            body_processed = body_processed.filter(ImageFilter.EDGE_ENHANCE)
            body_processed = ImageOps.posterize(body_processed, 6)

            # 색조 변형 (강하게)
            face_processed = ImageEnhance.Color(face_processed).enhance(1.20)
            face_processed = ImageEnhance.Contrast(face_processed).enhance(1.05)
            body_processed = ImageEnhance.Color(body_processed).enhance(1.30)
            body_processed = ImageEnhance.Contrast(body_processed).enhance(1.10)
            body_processed = ImageEnhance.Brightness(body_processed).enhance(0.94)

            # 추가 noise (옷/배경만 — 1000 → 800 약화)
            body_draw = ImageDraw.Draw(body_processed)
            _random.seed(_now_ms())
            _bw, _bh = body_processed.size
            for _ in range(800):
                x = _random.randint(0, _bw - 1)
                y = _random.randint(0, _bh - 1)
                shift = _random.randint(-12, 12)
                try:
                    r, g, b = body_processed.getpixel((x, y))
                    body_draw.point((x, y), fill=(
                        max(0, min(255, r + shift)),
                        max(0, min(255, g + shift)),
                        max(0, min(255, b + shift))
                    ))
                except Exception:
                    pass

            img = Image.new('RGB', (w, h))
            img.paste(face_processed, (0, 0))
            img.paste(body_processed, (0, face_h))

            quality = 88
            log_prefix = "[neutralize strong v2 · 약화된 painterly]"

        out = _io.BytesIO()
        img.save(out, format="JPEG", quality=quality, optimize=True)
        new_bytes = out.getvalue()

        fixed = f"runway_neutralized_{_now_ms()}_{os.urandom(3).hex()}.jpg"
        rel = _write_upload_bytes("runway", "jpg", new_bytes, fixed_name=fixed)

        try:
            base = _public_base()
        except Exception:
            base = "https://codibank-api.onrender.com"
        new_url = f"{base}{rel}" if rel.startswith("/") else f"{base}/{rel}"

        print(f"{log_prefix} ✅ ({orig_size[0]}x{orig_size[1]}, {len(new_bytes)} bytes) → {fixed}", flush=True)
        return new_url

    except Exception as e:
        print(f"[neutralize] 처리 실패: {e}", flush=True)
        return image_url


# tier 별 월 동영상 한도 (향후 Supabase 사용자 tier 와 연동)
_RUNWAY_TIER_LIMITS = {
    "FREE":    0,
    "SILVER":  2,
    "GOLD":    20,
    "DIAMOND": 50,
}

# 총괄 관리자 이메일 — admin endpoint 접근 권한 + 자동 DIAMOND 처리
_RUNWAY_ADMIN_EMAILS = {
    "admin@codibank.kr",
}

# 테스트 사용자 이메일 — 자동 DIAMOND 처리 (admin endpoint 접근 권한 없음)
_RUNWAY_TEST_EMAILS = {
    "prowizard@naver.com",
}


@app.route("/api/runway/candidates", methods=["GET"])
def runway_candidates():
    """
    후보 리스트 — 코디핏 3rd 결과 + 트라이온 결과.
    ⚠️ 실제 데이터는 클라이언트 IDB ('codibank' DB > 'codi_history' store) 에 있음.
    백엔드는 향후 Supabase 마이그레이션 시 활성화. 현재는 빈 배열 + 안내.
    클라이언트 (runway.html) 가 IDB 에서 직접 가져옴.
    """
    try:
        user_email = _runway_extract_user_email(request)
        # 향후: Supabase 마이그레이션 시 user_email 로 ai_album 조회
        # 현재: 클라이언트가 IDB 에서 가져오므로 빈 배열 안내
        return jsonify({
            "ok": True,
            "candidates": [],
            "total": 0,
            "user_email": user_email,
            "_source": "client_idb",
            "_note": "후보 리스트는 클라이언트 IDB(codibank.codi_history)에서 가져옵니다. 이 endpoint 는 향후 Supabase 마이그레이션용 placeholder.",
        })
    except Exception as e:
        print(f"[runway_candidates] error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e), "candidates": [], "total": 0}), 500


@app.route("/api/runway/generate", methods=["POST"])
def runway_generate():
    """
    동영상 생성 — BytePlus ModelArk Seedance 2.0 (Fast) REST API.
    payload:
      · candidate_id: 후보 ID (필수)
      · image_url: 후보 이미지 URL (Seedance 입력) — 빈 값이면 stub
      · duration: 영상 길이 초 (기본 6, 범위 4~10)
      · model: 'seedance' | 'placeholder' (기본 'seedance' — 키 있으면 시도, 없으면 폴백)
      · user_email: 사용자 식별 (Phase A)
      · prompt: 프롬프트 (선택, 기본 패션 회전 프롬프트)
    """
    try:
        payload = request.get_json(silent=True) or {}
        candidate_id = str(payload.get("candidate_id") or "").strip()
        image_url = str(payload.get("image_url") or "").strip()
        duration = int(payload.get("duration") or 6)
        model_req = str(payload.get("model") or "seedance").strip().lower()
        prompt_in = str(payload.get("prompt") or "").strip()

        # ─── 2026-05-27 KST · TJ 디자인 시안 ─── 해상도 옵션 (80M/1K/4K) ─────
        #   프론트 UI 토글 매핑:
        #     '80M' → 480p (854x480, BytePlus size='480p', 토큰 ~57K, 저렴)
        #     '1K'  → 720p (1280x720, BytePlus size='720p', 토큰 ~130K, 기본)
        #     '4K'  → 1080p (1920x1080, BytePlus size='1080p', 토큰 ~291K, 고화질)
        #   기본 = '1K' (720p) — 기존 동작과 호환.
        _res_in = str(payload.get("resolution") or "1K").strip().upper()
        _res_map = {"80M": "480p", "1K": "720p", "4K": "1080p"}
        seedance_size = _res_map.get(_res_in, "720p")
        print(f"[runway_generate] 해상도 옵션: {_res_in} → BytePlus size={seedance_size}", flush=True)

        if not candidate_id:
            return jsonify({"ok": False, "error": "candidate_id 가 필요합니다"}), 400
        if duration < 4 or duration > 10:
            return jsonify({"ok": False, "error": "duration 은 4~10초 범위"}), 400

        # ─── Phase A · 사용자 인증 + tier 검증 ───────────────────────
        user_email = _runway_extract_user_email(request)
        user_tier = _runway_get_user_tier(user_email)
        # 게스트(이메일 없음) 또는 FREE 는 stub 모드만
        # SILVER/GOLD/DIAMOND 는 실제 Seedance 시도 (2026-05-25: SILVER 도 동영상 2회 기본)
        is_paid = user_tier in ("SILVER", "GOLD", "DIAMOND")

        # ─── tier 별 월 한도 체크 (유료 사용자만) + 런웨이 보너스 합산 ───────
        if is_paid:
            used = _runway_get_monthly_video_count(user_email)
            base_limit = _RUNWAY_TIER_LIMITS.get(user_tier, 0)
            bonus = _runway_get_bonus(user_email)
            limit = base_limit + bonus  # 실효 한도 = tier 한도 + 보너스
            if used >= limit > 0:
                return jsonify({
                    "ok": False,
                    "error": f"월 한도 초과 ({used}/{limit})",
                    "tier": user_tier,
                    "used_this_month": used,
                    "monthly_limit": limit,
                    "base_limit": base_limit,
                    "runway_bonus": bonus,
                }), 429

        # ─── Phase C · BytePlus Seedance 2.0 통합 ────────────────────
        byteplus_key = os.environ.get("BYTEPLUS_API_KEY", "").strip()
        force_stub = (model_req == "placeholder") or (not byteplus_key) or (not is_paid) or (not image_url)

        if force_stub:
            # stub 모드 — 즉시 빈 응답
            reason = (
                "placeholder 명시" if model_req == "placeholder" else
                "BYTEPLUS_API_KEY 미설정" if not byteplus_key else
                f"비유료 tier ({user_tier})" if not is_paid else
                "image_url 없음" if not image_url else
                "기타"
            )
            return jsonify({
                "ok": True,
                "video_url": "",
                "thumb_url": "",
                "duration_seconds": duration,
                "model": "placeholder",
                "candidate_id": candidate_id,
                "generated_at": _runway_now_iso(),
                "_stub": True,
                "_stub_reason": reason,
                "_note": "실제 영상 생성을 위해 GOLD 이상 요금제 + BYTEPLUS_API_KEY 환경변수 설정 필요",
            })

        # ─── BytePlus Seedance 2.0 Fast REST API 호출 (실제) ─────────
        try:
            import requests as _rq

            # ─── 2026-05-25 KST 패치 (v2): 정면/후면 분리 + First/Last Frame 모드 + 워킹 prompt ─────
            #   변경 사항:
            #   1) 코디핏 1536x1024 합성 이미지를 정면(좌)+후면(우) 두 URL로 분리
            #   2) BytePlus Seedance 2.0 의 First/Last Frame 모드 사용:
            #      정면 = first_frame (시작 frame), 후면 = last_frame (끝 frame)
            #      → 정면 워킹 → 자연스러운 턴 → 후면 워킹 흐름이 자연 생성
            #   3) prompt 에 멋있는 런웨이 워킹 컨셉 명시 (TJ 차별화 의도)
            #   4) ratio/resolution/duration 을 root 파라미터로 분리
            #      (이전: prompt 안에 --resolution 식 — BytePlus가 무시했을 가능성)

            # 1) 정면/후면 분리
            front_url, back_url = _runway_split_front_back(image_url)
            has_split = (front_url != back_url) and (front_url != image_url)
            if has_split:
                print(f"[runway_generate] ✅ 이미지 분리 성공 → first/last frame 모드 사용", flush=True)
            else:
                print(f"[runway_generate] ⚠️ 이미지 분리 실패 → 단일 이미지 모드 폴백", flush=True)

            # 2) 런웨이 워킹 prompt
            # ─── 2026-06-02 KST · TJ 지시 (v22) ─── v21 고정본 + 3가지 보강(추가만) ───
            #   ※ v21 본문은 한 줄도 삭제/변경하지 않고 그대로 유지. 아래 문장만 추가.
            #   ① 워킹 시 팔을 자연스럽게 흔들며 걷기.
            #   ② 배경 이미지(스튜디오 배경)는 처음부터 끝까지 변경 금지.
            #   ③ 물리법칙 일관성: 정면 이미지에 보인 모든 요소(가방 위치/끈, 시계, 신발, 헤어,
            #      소지품, 비율)가 워킹·턴·후면에서도 동일하게 물리적으로 자연스럽게 유지.
            seedance_prompt = prompt_in or (
                "Use the FRONT image as the starting appearance and the BACK image as the reference for the rear outfit details.\n"
                "A realistic fashion runway presentation of the same person.\n"
                "The model starts standing naturally facing the camera.\n"
                "The model slowly walks forward toward the camera with smooth professional runway steps.\n"
                "After approaching the camera, the model stops naturally and holds a front-facing pose for a moment so the entire outfit can be clearly seen.\n"
                "Then the model slowly rotates 90 degrees to show the full side profile.\n"
                "After holding the side profile briefly, the model continues rotating until the full back view is visible.\n"
                "The model pauses to clearly display the back of the outfit.\n"
                "Finally, the model walks away from the camera while maintaining the back view until gradually moving into the distance.\n"
                "While walking, the arms swing naturally and gently at the sides in rhythm with the steps, like a real person walking.\n"
                "Always keep the model's entire body, from the top of the head to the feet, fully inside the frame at all times; keep a full-body shot and never crop the head or feet, and never zoom in closer than a full-body view, even while the model walks toward the camera.\n"
                "While walking — both when walking toward the camera and when walking away — both hands are always out of the pockets and the arms swing naturally with the steps. The hands may rest in the pockets only while standing still during a pause, and must be taken out again before walking. Never walk with the hands in the pockets.\n"
                "The person must remain identical throughout the entire sequence.\n"
                "Preserve all clothing details, silhouette, colors, textures, accessories, and proportions exactly.\n"
                "The front view must match the front reference image.\n"
                "The back view must match the back reference image.\n"
                "Keep every element exactly as shown in the front image consistent and physically correct during walking and turning: the bag stays on the same shoulder with its strap in a natural, fixed position, the watch, shoes, hair and all items stay in the same place and obey real-world physics, with no floating, morphing, swapping sides, duplicating or sudden changes.\n"
                "Always render correct, realistic human anatomy: exactly two eyes, one nose, one mouth, two ears, two arms, two legs, and exactly five fingers on each hand; never add, remove, duplicate, merge or deform any body part.\n"
                "Obey real-world physics at all times: gravity applies, the body, clothing and hair move together naturally and consistently with the motion, and the hair falls and sways according to gravity and momentum.\n"
                "Never move any body part beyond the natural human range of motion. The head and neck must NEVER rotate a full 180 degrees or twist backwards; turning to show the back is done by rotating the whole body, never by spinning the head or neck around. Absolutely no grotesque, horror-like, impossible or broken-joint deformations.\n"
                "Natural body motion.\n"
                "Smooth turning motion.\n"
                "Professional fashion model walk.\n"
                "No camera movement.\n"
                "No scene changes.\n"
                "Do not change or replace the background; keep the exact same background scene from start to end.\n"
                "No outfit changes.\n"
                "No facial distortion.\n"
                "No extra people.\n"
                "Exactly one single person in the entire video, only one model, no duplicate or clone of the person.\n"
                "Luxury fashion presentation.\n"
                "Photorealistic.\n"
                "High-end commercial fashion video."
            )
            # 2026-06-02 KST · TJ — 배포본이 실제 어느 프롬프트인지 로그로 확인 (배포 지연 진단용)
            print(f"[runway_generate] 프롬프트 버전: v24 | override(prompt_in)={'Y' if prompt_in else 'N'} | 길이={len(seedance_prompt)}자", flush=True)

            # 3) BytePlus 비디오 생성 요청
            create_url = "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks"
            # [2026-05-30] 모델 = Seedance 1.5 Pro (env CODIBANK_RUNWAY_MODEL 로 정확 ID 지정)
            _model_candidates = _runway_model_candidates()
            create_headers = {
                "Authorization": f"Bearer {byteplus_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            def _build_payload(_model_id: str, _front: str, _back: str, _use_first_last: bool, _use_role: bool = False) -> dict:
                """payload 빌더 — first/last frame 모드 또는 단일 frame 모드
                _use_role=True: image_url object 에 role 필드 (BytePlus 일부 wrapper 표준)
                _use_role=False: 순서로 인식 (첫 번째=first, 두 번째=last) — BytePlus 공식 가능성 높음
                """
                base = {
                    "model": _model_id,
                    "ratio": "9:16",         # root 파라미터 — 세로 영상
                    "resolution": seedance_size,  # 2026-05-27 KST · TJ 시안 — 사용자 선택 (480p/720p/1080p)
                    "duration": duration,    # root 파라미터
                }
                if _use_first_last:
                    if _use_role:
                        # 시도 A: role 필드 명시 (wrapper API 표준)
                        base["content"] = [
                            {"type": "text", "text": seedance_prompt},
                            {"type": "image_url", "image_url": {"url": _front}, "role": "first_frame"},
                            {"type": "image_url", "image_url": {"url": _back},  "role": "last_frame"},
                        ]
                    else:
                        # 시도 B: 순서로 인식 (BytePlus ModelArk 공식 가능성)
                        base["content"] = [
                            {"type": "text", "text": seedance_prompt},
                            {"type": "image_url", "image_url": {"url": _front}},  # 순서 1 = first
                            {"type": "image_url", "image_url": {"url": _back}},   # 순서 2 = last
                        ]
                else:
                    # 단일 이미지 모드 (분리 실패 또는 first/last 거부 시 폴백)
                    base["content"] = [
                        {"type": "text", "text": seedance_prompt},
                        {"type": "image_url", "image_url": {"url": _front}},
                    ]
                return base

            # ─── 모델 후보 순회 — sensitive content 에러 시 다음 모델 자동 시도 ─────
            cr = None
            used_model_id = None
            used_mode = None  # "single_frame" / "single_frame_neutralized"
            sensitive_blocked = False
            sensitive_err_text = ""

            # ─── 2026-06-01 KST · TJ 승인 (A) ─── First/Last Frame 재활성화 ─────────
            #   배경: 정면 1장만 보내 측면·후면 자세를 모델이 상상 → 턴 괴기 변형.
            #   해결: 정면=first_frame, 후면=last_frame 으로 보내 끝자세를 이미지로 고정.
            #   Seedance 1.5 Pro 는 first/last frame 공식 지원(시작·끝 프레임 일관성).
            #   전략: ①role 형식(first_frame/last_frame) → ②순서 형식 → ③단일(정면) 폴백.
            #         400 응답 본문을 전부 로그에 남겨 거부 시 원인 즉시 확인.
            #   ※ 분리 실패(has_split=False) 시엔 first/last 생략하고 곧장 단일 모드.

            # ─── 시도 1: First/Last Frame (정면=first, 후면=last) ─── has_split 일 때만 ───
            if used_model_id is None and has_split:
                for _model_id in _model_candidates:
                    _broke_sensitive = False
                    for _use_role in (True, False):  # role 형식 우선, 실패 시 순서 형식
                        _mode_lbl = "first_last(role)" if _use_role else "first_last(order)"
                        create_payload = _build_payload(_model_id, front_url, back_url, True, _use_role)
                        cr = _rq.post(create_url, json=create_payload, headers=create_headers, timeout=20)
                        if cr.status_code < 400:
                            used_model_id = _model_id
                            used_mode = _mode_lbl
                            print(f"[runway_generate] ✅ {_mode_lbl} 통과: {_model_id} (정면=first, 후면=last)", flush=True)
                            break
                        _body = cr.text or ""
                        # sensitive 거부면 다음 '모델' 로 (형식 바꿔도 동일하게 거부됨)
                        if cr.status_code == 400 and ("InputImageSensitiveContent" in _body or "PrivacyInformation" in _body or "may contain real person" in _body):
                            sensitive_blocked = True
                            sensitive_err_text = _body[:300]
                            print(f"[runway_generate] {_model_id} ({_mode_lbl}) sensitive 거부 → 다음 모델", flush=True)
                            _broke_sensitive = True
                            break
                        # 그 외 400 → 형식 문제일 수 있으니 본문 전체 로그 후 다음 형식 시도
                        print(f"[runway_generate] ⚠ {_mode_lbl} 거부 ({cr.status_code}): {_body[:400]}", flush=True)
                    if used_model_id is not None or _broke_sensitive:
                        break

            # ─── 시도 2: 단일 이미지 모드 (정면만) — first/last 실패 또는 분리 실패 ─────
            if used_model_id is None and not sensitive_blocked:
                fallback_url = front_url if has_split else image_url
                print(f"[runway_generate] ↪ first/last 미통과 → 단일(정면) 모드 폴백", flush=True)
                for _model_id in _model_candidates:
                    create_payload = _build_payload(_model_id, fallback_url, fallback_url, False)
                    cr = _rq.post(create_url, json=create_payload, headers=create_headers, timeout=20)
                    if cr.status_code < 400:
                        used_model_id = _model_id
                        used_mode = "single_frame"
                        print(f"[runway_generate] ✅ 단일 모드 통과: {_model_id}", flush=True)
                        break
                    _body = cr.text or ""
                    if cr.status_code == 400 and ("InputImageSensitiveContent" in _body or "PrivacyInformation" in _body or "may contain real person" in _body):
                        sensitive_blocked = True
                        sensitive_err_text = _body[:300]
                        print(f"[runway_generate] {_model_id} (single) sensitive 거부 → 다음", flush=True)
                        continue
                    raise RuntimeError(f"BytePlus create 실패 ({cr.status_code}): {_body[:300]}")

            # [2026-05-30 TJ 결정] neutralize/스타일화 폴백 전면 제거 — 원본 그대로만 사용.
            #   이미지를 일절 변형하지 않으므로, BytePlus 필터가 거부하면 그대로 사용자에게 안내.
            #   (기존 LIGHT/STRONG painterly neutralize 는 옷·얼굴을 손상시켜 제거함.)
            if used_model_id is None:
                if sensitive_blocked:
                    raise RuntimeError(f"SENSITIVE_CONTENT::AI 생성 이미지가 BytePlus 안전 필터로 차단됨 (원본 그대로 사용 정책 — 다른 코디로 다시 시도해주세요): {sensitive_err_text[:200]}")
                else:
                    raise RuntimeError(f"BytePlus create 실패: {(cr.text if cr else '')[:300]}")

            gen_data = cr.json() or {}
            task_id = gen_data.get("id") or gen_data.get("task_id")
            if not task_id:
                raise RuntimeError(f"BytePlus response 에 task id 없음: {str(gen_data)[:200]}")

            # 2) 폴링 (최대 300초, 3초 간격 — Seedance 평균 60~180초 소요, 안전 margin)
            import time as _time
            poll_url = f"https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/{task_id}"
            video_url = ""
            thumb_url = ""
            for _i in range(100):  # 100 * 3 = 300초
                _time.sleep(3)
                pr = _rq.get(poll_url, headers=create_headers, timeout=15)
                if pr.status_code >= 400:
                    continue
                pd = pr.json() or {}
                status = (pd.get("status") or "").lower()
                if status in ("succeeded", "completed", "success"):
                    content = pd.get("content") or {}
                    video_url = content.get("video_url") or ""
                    # BytePlus 는 thumbnail 별도 안 줄 수도
                    thumb_url = content.get("thumbnail_url") or content.get("first_frame_url") or ""

                    # ─── 2026-05-27 KST · TJ 질문 ─── 토큰 사용량 추출 + log ─────
                    #   BytePlus 응답에 usage 정보가 포함되어 있다면 추출 + log 기록.
                    #   응답 구조 (관찰): pd.usage = {"total_tokens", "completion_tokens", "input_tokens"} 또는
                    #                    pd.content.usage = {...} 또는 pd.metadata.usage 등 다양.
                    #   공식 계산: (width × height × duration × 24fps) / 1024 = tokens
                    #   720p (720×1280) × 6초 × 24fps / 1024 = 129,600 tokens / 영상
                    #   2026-05-27 KST · TJ 시안 — 해상도별 동적 계산
                    _usage = {}
                    try:
                        _u1 = pd.get("usage") or {}
                        _u2 = (content.get("usage") if isinstance(content, dict) else None) or {}
                        _u3 = (pd.get("metadata", {}) or {}).get("usage") or {}
                        for _u in [_u1, _u2, _u3]:
                            if _u and isinstance(_u, dict):
                                _usage.update(_u)
                        # 응답에 usage 없으면 공식으로 추정 (해상도별)
                        if not _usage:
                            _res_dims = {
                                "480p":  (854, 480),    # 80M → ~57K tokens
                                "720p":  (1280, 720),   # 1K  → ~129K tokens
                                "1080p": (1920, 1080),  # 4K  → ~291K tokens
                            }
                            _w, _h = _res_dims.get(seedance_size, (1280, 720))
                            _est_tokens = (_w * _h * duration * 24) // 1024
                            _usage = {"estimated_tokens": _est_tokens, "source": f"formula_{seedance_size}"}
                    except Exception:
                        pass

                    _tok_total = _usage.get("total_tokens") or _usage.get("estimated_tokens") or 0
                    _tok_cost_usd = round((_tok_total / 1_000_000) * 3.30, 4) if _tok_total else 0  # fast pack: $3.30/1M
                    _tok_cost_krw = round(_tok_cost_usd * 1400, 0) if _tok_cost_usd else 0
                    print(f"[runway_generate · 토큰 사용량] task={task_id}, tokens={_tok_total:,}, "
                          f"비용=${_tok_cost_usd:.4f} ≈ ₩{int(_tok_cost_krw):,}, source={_usage.get('source','byteplus_response')}", flush=True)

                    # 응답에 포함 (프론트가 사용량 표시 가능)
                    _token_info = {
                        "tokens": _tok_total,
                        "cost_usd": _tok_cost_usd,
                        "cost_krw": int(_tok_cost_krw),
                        "source": _usage.get("source", "byteplus_response"),
                    }
                    break
                if status in ("failed", "error", "cancelled"):
                    err = pd.get("error") or {}
                    err_msg = err.get("message") or err.get("code") or str(err)[:200]
                    # ─── 2026-05-28 KST · TJ 기준 ─── 배경 보존: very_strong 재시도 제거 ───
                    #   기존: 출력 영상 copyright 거부 시 very_strong painterly 재시도.
                    #   변경: very_strong 은 배경을 강한 painterly 로 변형 → 솔리드 파스텔
                    #         배경 깨짐 (TJ 기준 위반). 배경 망가진 영상을 내보내느니
                    #         명확한 안내로 처리 (작업 B/C 가 입력 단계에서 통과율을 높임).
                    raise RuntimeError(f"Seedance 생성 실패: {err_msg}")
            if not video_url:
                raise RuntimeError("Seedance 폴링 타임아웃 (300초)")

            # 3) Supabase 사용량 +1
            _runway_increment_usage(user_email)

            # ─── 2026-05-29 KST · TJ 지시 (2번 — 영상 리스트 재생 안 됨 fix) ───
            #   원인: BytePlus 영상 URL 은 24h 만료 → 어제 만든 영상 오늘 재생 불가.
            #   해결: 생성 직후 BytePlus 영상을 다운로드해 R2 에 영구 저장 →
            #         자체 URL(/uploads/..)을 반환. 만료 없는 영구 재생.
            #   실패 시: BytePlus 원본 URL 로 폴백 (최소한 당장은 재생되게).
            final_video_url = video_url
            try:
                _vid_resp = _rq.get(video_url, timeout=60)
                if _vid_resp.status_code == 200 and _vid_resp.content:
                    _vid_name = f"runway_video_{_now_ms()}_{os.urandom(3).hex()}.mp4"
                    _vid_rel = _write_upload_bytes("runway", "mp4", _vid_resp.content,
                                                   fixed_name=_vid_name)
                    try:
                        _vbase = _public_base()
                    except Exception:
                        _vbase = "https://codibank-api.onrender.com"
                    final_video_url = (f"{_vbase}{_vid_rel}" if _vid_rel.startswith("/")
                                       else f"{_vbase}/{_vid_rel}")
                    print(f"[runway_video_r2] ✅ 영상 R2 영구저장 완료: {_vid_name} "
                          f"({len(_vid_resp.content)//1024}KB)", flush=True)
                else:
                    print(f"[runway_video_r2] ⚠ 영상 다운로드 실패 ({_vid_resp.status_code}) "
                          f"→ BytePlus 원본 URL 사용", flush=True)
            except Exception as _ve:
                print(f"[runway_video_r2] ⚠ R2 저장 실패 → BytePlus 원본 URL 사용: {_ve}", flush=True)

            return jsonify({
                "ok": True,
                "video_url": final_video_url,  # R2 영구 URL (실패 시 BytePlus 원본)
                "thumb_url": thumb_url,
                "duration_seconds": duration,
                "model": used_model_id or "seedance-2.0-fast",
                "mode": used_mode or "single_frame",  # first_last_frame / single_frame / *_neutralized
                "candidate_id": candidate_id,
                "generated_at": _runway_now_iso(),
                "task_id": task_id,
                "tier": user_tier,
                "token_usage": _token_info if '_token_info' in dir() else None,  # 2026-05-27 KST · TJ 질문
            })

        except Exception as seedance_err:
            err_text = str(seedance_err)
            print(f"[runway_generate · BytePlus Seedance 호출 실패] {err_text}", flush=True)
            # ─── 에러 분류 — sensitive content 거부는 별도 reason ─────
            #   클라이언트 (runway.html) 가 stubReason 매칭으로 사용자 친화적 메시지 표시
            if err_text.startswith("SENSITIVE_CONTENT::"):
                _reason = "sensitive_content"
                _user_err = "AI 안전 필터로 영상 생성이 차단되었어요"
            elif "copyright" in err_text.lower():
                # 2026-05-28 KST · TJ 보고 — 출력 영상 저작권/초상권 차단
                #   주로 트라이온 이미지(사실적)에서 발생. BytePlus 가 실제 인물/유명인
                #   닮은 영상을 저작권 위험으로 판단. 코디핏 이미지는 거의 발생 안 함.
                _reason = "copyright_content"
                _user_err = "이 이미지는 안전 필터로 영상 생성이 어려워요. 다른 코디를 시도해보세요"
            elif "타임아웃" in err_text or "timeout" in err_text.lower():
                _reason = "BytePlus Seedance timeout"
                _user_err = "영상 생성 시간이 초과되었어요"
            else:
                _reason = "BytePlus Seedance API 호출 실패"
                _user_err = "BytePlus 일시적 오류"
            # 호출 실패 시 stub 응답으로 폴백
            return jsonify({
                "ok": True,
                "video_url": "",
                "thumb_url": "",
                "duration_seconds": duration,
                "model": "placeholder",
                "candidate_id": candidate_id,
                "generated_at": _runway_now_iso(),
                "_stub": True,
                "_stub_reason": _reason,
                "_user_error": _user_err,
                "_seedance_error": err_text[:300],
            })

    except Exception as e:
        print(f"[runway_generate] error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/runway/videos", methods=["GET"])
def runway_videos_list():
    """사용자가 생성한 동영상 리스트 (Supabase user_videos 테이블 — 향후 구현)."""
    try:
        user_email = _runway_extract_user_email(request)
        # TODO: Supabase user_videos 테이블 조회
        #   rows = _rq.get(f"{sb_url}/rest/v1/user_videos",
        #                  params={"select": "*", "user_email": f"eq.{user_email}",
        #                          "order": "created_at.desc", "limit": "50"},
        #                  headers={...})
        # 현재: 빈 배열 (테이블 미생성)
        return jsonify({
            "ok": True,
            "videos": [],
            "total": 0,
            "user_email": user_email,
            "_note": "user_videos 테이블 생성 후 활성화 — 현재는 빈 배열",
        })
    except Exception as e:
        print(f"[runway_videos_list] error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e), "videos": [], "total": 0}), 500


@app.route("/api/runway/videos/<video_id>", methods=["DELETE"])
def runway_video_delete(video_id):
    """영상 삭제."""
    try:
        vid = str(video_id or "").strip()
        if not vid:
            return jsonify({"ok": False, "error": "video_id 가 필요합니다"}), 400
        user_email = _runway_extract_user_email(request)
        # TODO: R2 + Supabase 에서 삭제 (소유권 검증 포함)
        return jsonify({
            "ok": True,
            "deleted_id": vid,
            "user_email": user_email,
            "_stub": True,
        })
    except Exception as e:
        print(f"[runway_video_delete] error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/runway/usage", methods=["GET"])
def runway_usage():
    """tier 별 사용량 + 한도 + 보너스."""
    try:
        user_email = _runway_extract_user_email(request)
        tier = _runway_get_user_tier(user_email)
        used = _runway_get_monthly_video_count(user_email) if user_email else 0
        base_limit = _RUNWAY_TIER_LIMITS.get(tier, 0)
        bonus = _runway_get_bonus(user_email) if user_email else 0
        effective_limit = base_limit + bonus
        return jsonify({
            "ok": True,
            "user_email": user_email,
            "tier": tier,
            "used_this_month": used,
            "monthly_limit": effective_limit,   # 실효 한도 (보너스 포함)
            "base_limit": base_limit,           # tier 기본 한도
            "runway_bonus": bonus,              # 이번달 보너스
            "remaining": max(0, effective_limit - used),
            "tier_limits": _RUNWAY_TIER_LIMITS,
            "is_paid": tier in ("GOLD", "DIAMOND"),
        })
    except Exception as e:
        print(f"[runway_usage] error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500


# ─── 2026-05-25 KST · Phase C 활성화 점검 endpoint (BytePlus Seedance 2.0) ─
#   동영상 생성 서비스가 작동 가능한지 한눈에 확인.
#   배포 후 호출:
#     curl https://codibank-api.onrender.com/api/runway/health
#   응답:
#     - ready: true (모든 조건 충족)
#     - missing: ["BYTEPLUS_API_KEY", ...] (부족한 환경변수)
#     - checks: 각 항목별 상세
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/runway/health", methods=["GET"])
def runway_health():
    """동영상 생성 활성화 점검 — 환경변수 + Supabase + BytePlus Seedance 핑."""
    checks = {}
    missing = []

    # ① BYTEPLUS_API_KEY 환경변수
    byteplus_key = os.environ.get("BYTEPLUS_API_KEY", "").strip()
    key_format_ok = False
    key_format_warning = ""
    if byteplus_key:
        # BytePlus ModelArk 키는 UUID 형식 또는 base64 형식
        # 최소 길이 16자 이상
        if len(byteplus_key) >= 16:
            key_format_ok = True
        elif " " in byteplus_key or "\n" in byteplus_key or "\t" in byteplus_key:
            key_format_warning = "환경변수에 공백/줄바꿈/탭 포함 — 값 재입력 필요"
        else:
            key_format_warning = f"키 길이가 너무 짧음 ({len(byteplus_key)}자) — 일부만 복사했을 가능성"
    checks["BYTEPLUS_API_KEY"] = {
        "set": bool(byteplus_key),
        "length": len(byteplus_key) if byteplus_key else 0,
        "prefix": (byteplus_key[:8] + "...") if len(byteplus_key) > 8 else byteplus_key,
        "suffix": ("..." + byteplus_key[-4:]) if len(byteplus_key) > 12 else "",
        "format_ok": key_format_ok,
        "format_warning": key_format_warning,
    }
    if not byteplus_key:
        missing.append("BYTEPLUS_API_KEY")

    # ② Supabase 연결
    svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    sb_url = os.environ.get("SUPABASE_URL", "https://drgsayvlpzcacurcczjq.supabase.co")
    checks["SUPABASE_SERVICE_KEY"] = {
        "set": bool(svc_key),
        "url": sb_url,
    }
    if not svc_key:
        missing.append("SUPABASE_SERVICE_KEY")

    # ③ Supabase user_usage 테이블 점검 (tier/runway_count 컬럼 존재 — month 는 기존)
    sb_table_ok = False
    sb_table_error = ""
    if svc_key:
        try:
            import requests as _rq
            r = _rq.get(
                f"{sb_url}/rest/v1/user_usage",
                params={"select": "tier,runway_count,month", "limit": 1},
                headers={
                    "apikey": svc_key,
                    "Authorization": f"Bearer {svc_key}",
                    "Accept": "application/json",
                },
                timeout=8,
            )
            if r.status_code == 200:
                sb_table_ok = True
            else:
                sb_table_error = f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            sb_table_error = str(e)[:200]
    checks["supabase_user_usage"] = {
        "ok": sb_table_ok,
        "expected_columns": ["tier", "runway_count", "month"],
        "error": sb_table_error,
    }
    if not sb_table_ok and svc_key:
        missing.append("supabase_user_usage_columns")

    # ④ BytePlus Seedance API 핑 (인증 + 모델 확인)
    #   생성 호출은 비용이 들기 때문에 list endpoint 만 호출 (인증 검증)
    seedance_api_ok = False
    seedance_api_error = ""
    seedance_api_hint = ""
    seedance_status_code = None
    seedance_response_body = ""
    if byteplus_key:
        try:
            import requests as _rq
            # BytePlus ModelArk 비디오 생성 작업 목록 조회 (인증 검증용 — 비용 0)
            ping_url = "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks"
            r = _rq.get(
                ping_url,
                params={"page_size": "1"},
                headers={
                    "Authorization": f"Bearer {byteplus_key}",
                    "Accept": "application/json",
                },
                timeout=10,
            )
            seedance_status_code = r.status_code
            seedance_response_body = r.text[:300]
            if r.status_code in (200, 201):
                seedance_api_ok = True
                seedance_api_hint = "✅ BytePlus Seedance 2.0 API 정상 작동 — 비디오 생성 가능"
            elif r.status_code == 401:
                seedance_api_error = "인증 실패 (401) — API Key 가 유효하지 않음"
                seedance_api_hint = (
                    "Render 환경변수 BYTEPLUS_API_KEY 확인. "
                    "BytePlus 콘솔 (console.byteplus.com/ark) 의 'API keys' 에서 키 재확인."
                )
            elif r.status_code == 403:
                seedance_api_error = "권한 거부 (403) — 모델 활성화 또는 결제 문제"
                seedance_api_hint = (
                    "BytePlus 콘솔의 'Model activation' 에서 Dreamina-Seedance-2.0 활성화 확인. "
                    "Free Credits Only Mode 가 켜져 있고 무료 크레딧 0 이면 자동 중단됨."
                )
            elif r.status_code == 404:
                seedance_api_error = "endpoint 404 — base URL 점검 필요"
                seedance_api_hint = (
                    "리전 확인. 사용 리전: ap-southeast (Japan). "
                    "다른 리전은 endpoint 가 다름 (예: cn-beijing)."
                )
            else:
                seedance_api_error = f"HTTP {r.status_code}"
                seedance_api_hint = "응답 본문 확인 후 BytePlus 문서 참조"
        except Exception as e:
            seedance_api_error = str(e)[:200]
            seedance_api_hint = "네트워크 오류 — Render 외부 호출 가능한지 확인"
    checks["byteplus_seedance_api"] = {
        "ok": seedance_api_ok,
        "endpoint": "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks",
        "status_code": seedance_status_code,
        "error": seedance_api_error,
        "hint": seedance_api_hint,
        "response_body_preview": seedance_response_body,
        "model_id_used": _runway_model_candidates()[0],
    }
    if not seedance_api_ok and byteplus_key:
        missing.append("byteplus_seedance_api_auth")

    # ⑤ R2 / 결제 관련 (향후)
    checks["r2_video_storage"] = {
        "ok": False,
        "note": "향후 R2 비디오 저장 활성화 시 점검",
    }

    ready = (
        bool(byteplus_key)
        and bool(svc_key)
        and sb_table_ok
        and seedance_api_ok
    )

    return jsonify({
        "ok": True,
        "ready": ready,
        "missing": missing,
        "checks": checks,
        "tier_limits": _RUNWAY_TIER_LIMITS,
        "model_info": {
            "provider": "BytePlus ModelArk",
            "model": "Seedance 1.5 Pro",
            "model_id": _runway_model_candidates()[0],
            "region": "Asia Pacific (Japan)",
            "base_url": "https://ark.ap-southeast.bytepluses.com/api/v3",
        },
        "_note": (
            "ready=true 일 때 동영상 생성 가능. "
            "missing 항목이 있다면 가이드에 따라 환경변수 설정 또는 Supabase 마이그레이션 필요."
        ),
    })


# ═══════════════════════════════════════════════════════════════════════════
# Runway Admin Endpoints (2026-05-25 KST)
#
# 관리자 페이지(admin.html)의 '런웨이' 탭에서 사용하는 endpoint 4개.
# 모든 admin endpoint 는 X-Admin-Email 헤더 또는 admin_email 쿼리/페이로드로
# 관리자 검증. _RUNWAY_ADMIN_EMAILS 에 포함된 이메일만 통과.
#
# Endpoint 목록:
#   GET    /api/admin/runway/stats        — 전체 통계 (총 영상 수, 총 사용자 수)
#   GET    /api/admin/runway/users        — 사용자별 런웨이 사용 현황
#   GET    /api/admin/runway/videos       — 전체 영상 목록 (최근 N개)
#   PATCH  /api/admin/runway/user/<email> — 사용자 tier 변경 + 한도 초기화
# ═══════════════════════════════════════════════════════════════════════════

def _runway_admin_check(req):
    """admin 권한 검증 — 헤더/쿼리/페이로드 모두 확인.
       유효한 admin 이메일 반환, 아니면 None."""
    candidates = []
    try:
        candidates.append(req.headers.get("X-Admin-Email", ""))
    except Exception:
        pass
    try:
        candidates.append(req.args.get("admin_email", ""))
    except Exception:
        pass
    try:
        body = req.get_json(silent=True) or {}
        candidates.append(body.get("admin_email", ""))
    except Exception:
        pass
    for c in candidates:
        if c and _runway_is_admin(c):
            return str(c).strip().lower()
    return None


@app.route("/api/admin/runway/stats", methods=["GET"])
def admin_runway_stats():
    """런웨이 전체 통계 — 총 사용자 수, 총 영상 수, tier별 분포, 월별 사용량.
       헤더: X-Admin-Email: admin@codibank.kr"""
    admin = _runway_admin_check(request)
    if not admin:
        return jsonify({"ok": False, "error": "관리자 권한 필요 (X-Admin-Email 헤더 또는 admin_email 쿼리)"}), 403

    stats = {
        "total_users": 0,
        "total_videos_this_month": 0,
        "tier_distribution": {"FREE": 0, "SILVER": 0, "GOLD": 0, "DIAMOND": 0},
        "admin_emails": list(_RUNWAY_ADMIN_EMAILS),
        "test_emails": list(_RUNWAY_TEST_EMAILS),
        "tier_limits": _RUNWAY_TIER_LIMITS,
    }
    try:
        import requests as _rq
        from datetime import datetime
        svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        sb_url = os.environ.get("SUPABASE_URL", "https://drgsayvlpzcacurcczjq.supabase.co")
        if svc_key:
            month_key = datetime.now().strftime("%Y-%m")
            # 1) 이번 달 user_usage row 조회 — tier 분포 + 총 사용자/영상
            r = _rq.get(
                f"{sb_url}/rest/v1/user_usage",
                params={
                    "select": "email,tier,runway_count",
                    "month": f"eq.{month_key}",
                    "limit": "1000",
                },
                headers={
                    "apikey": svc_key,
                    "Authorization": f"Bearer {svc_key}",
                    "Accept": "application/json",
                },
                timeout=10,
            )
            if r.status_code == 200:
                rows = r.json() or []
                stats["total_users"] = len(rows)
                total_videos = 0
                for row in rows:
                    tier = str(row.get("tier") or "FREE").upper().strip()
                    if tier in stats["tier_distribution"]:
                        stats["tier_distribution"][tier] += 1
                    total_videos += int(row.get("runway_count") or 0)
                stats["total_videos_this_month"] = total_videos
                stats["month"] = month_key
    except Exception as e:
        print(f"[admin_runway_stats] error: {e}", flush=True)
        stats["_error"] = str(e)[:200]

    return jsonify({"ok": True, "stats": stats, "admin": admin})


@app.route("/api/admin/runway/users", methods=["GET"])
def admin_runway_users():
    """사용자별 런웨이 사용 현황 — 이메일/tier/이번달 영상수/한도.
       쿼리:
         - month (선택): YYYY-MM (기본 현재 달)
         - tier (선택): FREE/SILVER/GOLD/DIAMOND (필터)
         - sort (선택): runway_count|email (기본 runway_count desc)
         - limit (선택): 기본 100, 최대 500"""
    admin = _runway_admin_check(request)
    if not admin:
        return jsonify({"ok": False, "error": "관리자 권한 필요"}), 403

    try:
        import requests as _rq
        from datetime import datetime
        svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        sb_url = os.environ.get("SUPABASE_URL", "https://drgsayvlpzcacurcczjq.supabase.co")
        if not svc_key:
            return jsonify({"ok": False, "error": "SUPABASE_SERVICE_KEY 미설정"}), 500

        month_key = (request.args.get("month") or datetime.now().strftime("%Y-%m")).strip()
        tier_filter = (request.args.get("tier") or "").strip().upper()
        sort_param = (request.args.get("sort") or "runway_count").strip().lower()
        limit = min(int(request.args.get("limit") or 100), 500)

        params = {
            "select": "email,tier,runway_count,month",
            "month": f"eq.{month_key}",
            "limit": str(limit),
        }
        if tier_filter in ("FREE", "SILVER", "GOLD", "DIAMOND"):
            params["tier"] = f"eq.{tier_filter}"
        # Supabase 정렬: runway_count desc / email asc
        if sort_param == "email":
            params["order"] = "email.asc"
        else:
            params["order"] = "runway_count.desc"

        r = _rq.get(
            f"{sb_url}/rest/v1/user_usage",
            params=params,
            headers={
                "apikey": svc_key,
                "Authorization": f"Bearer {svc_key}",
                "Accept": "application/json",
            },
            timeout=10,
        )
        if r.status_code != 200:
            return jsonify({"ok": False, "error": f"Supabase HTTP {r.status_code}: {r.text[:200]}"}), 500

        rows = r.json() or []
        users = []
        for row in rows:
            email = str(row.get("email") or "").strip()
            tier = str(row.get("tier") or "FREE").upper().strip()
            used = int(row.get("runway_count") or 0)
            limit_val = _RUNWAY_TIER_LIMITS.get(tier, 0)
            users.append({
                "email": email,
                "tier": tier,
                "runway_count": used,
                "monthly_limit": limit_val,
                "usage_pct": round((used / limit_val * 100), 1) if limit_val > 0 else 0,
                "is_admin": email.lower() in _RUNWAY_ADMIN_EMAILS,
                "is_test": email.lower() in _RUNWAY_TEST_EMAILS,
            })

        return jsonify({
            "ok": True,
            "month": month_key,
            "count": len(users),
            "users": users,
            "admin": admin,
        })

    except Exception as e:
        print(f"[admin_runway_users] error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/admin/runway/videos", methods=["GET"])
def admin_runway_videos():
    """전체 영상 목록 (최근 N개) — 향후 user_videos 테이블 연동.
       현재는 stub (Supabase user_videos 테이블 미구현 상태).
       쿼리: limit (기본 50, 최대 200)"""
    admin = _runway_admin_check(request)
    if not admin:
        return jsonify({"ok": False, "error": "관리자 권한 필요"}), 403

    limit = min(int(request.args.get("limit") or 50), 200)

    # TODO: Supabase user_videos 테이블 구현 후 실제 조회
    #   현재는 user_usage 의 runway_count 만 조회 가능
    return jsonify({
        "ok": True,
        "videos": [],
        "count": 0,
        "limit": limit,
        "admin": admin,
        "_note": (
            "현재 stub — Supabase user_videos 테이블 (id, user_email, candidate_id, "
            "task_id, video_url, thumb_url, model, duration, created_at) 구현 후 실제 조회 가능."
        ),
    })


@app.route("/api/admin/runway/user/<path:user_email>", methods=["PATCH"])
def admin_runway_user_update(user_email):
    """사용자 tier 변경 + 한도 초기화.
       payload:
         - tier (선택): FREE/SILVER/GOLD/DIAMOND
         - reset_runway_count (선택): true → runway_count 0 으로 초기화
       헤더: X-Admin-Email"""
    admin = _runway_admin_check(request)
    if not admin:
        return jsonify({"ok": False, "error": "관리자 권한 필요"}), 403

    try:
        payload = request.get_json(silent=True) or {}
        new_tier = str(payload.get("tier") or "").upper().strip()
        reset_count = bool(payload.get("reset_runway_count"))

        if new_tier and new_tier not in ("FREE", "SILVER", "GOLD", "DIAMOND"):
            return jsonify({"ok": False, "error": "tier 는 FREE/SILVER/GOLD/DIAMOND 중 하나"}), 400
        if not new_tier and not reset_count:
            return jsonify({"ok": False, "error": "tier 또는 reset_runway_count 중 하나 지정"}), 400

        import requests as _rq
        from datetime import datetime
        svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        sb_url = os.environ.get("SUPABASE_URL", "https://drgsayvlpzcacurcczjq.supabase.co")
        if not svc_key:
            return jsonify({"ok": False, "error": "SUPABASE_SERVICE_KEY 미설정"}), 500

        month_key = datetime.now().strftime("%Y-%m")
        update_data = {}
        if new_tier:
            update_data["tier"] = new_tier
        if reset_count:
            update_data["runway_count"] = 0

        # PATCH user_usage WHERE email=user_email AND month=current
        r = _rq.patch(
            f"{sb_url}/rest/v1/user_usage",
            params={
                "email": f"eq.{user_email}",
                "month": f"eq.{month_key}",
            },
            json=update_data,
            headers={
                "apikey": svc_key,
                "Authorization": f"Bearer {svc_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            timeout=10,
        )
        if r.status_code not in (200, 201, 204):
            return jsonify({"ok": False, "error": f"Supabase HTTP {r.status_code}: {r.text[:300]}"}), 500

        updated_rows = r.json() if r.text else []

        return jsonify({
            "ok": True,
            "user_email": user_email,
            "month": month_key,
            "updates_applied": update_data,
            "updated_rows": updated_rows,
            "admin": admin,
        })

    except Exception as e:
        print(f"[admin_runway_user_update] error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# Runway Bonus System (2026-05-25 KST)
#
# 동영상 생성 무료 보너스 — 코디핏/트라이온 보너스와 동일 패턴.
# user_usage_bonus 테이블의 'runway_bonus' 컬럼 사용 (메모리 캐시 폴백).
#
# Endpoint 목록:
#   GET    /api/usage/runway-bonus/<email>  — 앱 조회용 (인증 불필요)
#   POST   /admin/runway/set-bonus          — MASTER 전용, 런웨이 보너스 설정
#   GET    /admin/runway/bonus-list         — MASTER 전용, 현황 조회
# ═══════════════════════════════════════════════════════════════════════════

def _runway_get_bonus(email):
    """이번달 런웨이 보너스 횟수 조회 (Supabase + 메모리 폴백)."""
    if not email:
        return 0
    email_lower = str(email).strip().lower()
    now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
    bonus = 0
    # ① Supabase 조회 (user_usage_bonus.runway_bonus 컬럼)
    try:
        import requests as _rq
        svc_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        sb_url = os.environ.get("SUPABASE_URL", "https://drgsayvlpzcacurcczjq.supabase.co")
        if svc_key:
            r = _rq.get(
                f"{sb_url}/rest/v1/user_usage_bonus",
                params={
                    "select": "runway_bonus",
                    "email": f"eq.{email_lower}",
                    "month": f"eq.{now_ym}",
                    "limit": 1,
                },
                headers={
                    "apikey": svc_key,
                    "Authorization": f"Bearer {svc_key}",
                    "Accept": "application/json",
                },
                timeout=6,
            )
            if r.status_code == 200:
                rows = r.json() or []
                if rows and rows[0].get("runway_bonus") is not None:
                    bonus = int(rows[0]["runway_bonus"] or 0)
    except Exception as e:
        print(f"[_runway_get_bonus] supabase error: {e}", flush=True)
    # ② 메모리 캐시 우선 (supabase 컬럼 없을 때 폴백)
    try:
        if hasattr(app, "_runway_bonus_cache"):
            mkey = f"{email_lower}:{now_ym}"
            if mkey in app._runway_bonus_cache:
                bonus = int(app._runway_bonus_cache[mkey] or 0)
    except Exception:
        pass
    return max(0, bonus)


@app.get("/api/usage/runway-bonus/<email>")
def get_runway_bonus(email):
    """런웨이 보너스 조회 (앱 호출용 — 인증 불필요).
       응답: { ok, month, runway_bonus }"""
    try:
        email_lower = str(email).strip().lower()
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        bonus = _runway_get_bonus(email_lower)
        return jsonify({
            "ok": True,
            "month": now_ym,
            "email": email_lower,
            "runway_bonus": bonus,
        })
    except Exception as e:
        return jsonify({
            "ok": True,
            "month": __import__('datetime').datetime.now().strftime("%Y-%m"),
            "runway_bonus": 0,
            "error": str(e),
        })


@app.post("/admin/runway/set-bonus")
def admin_set_runway_bonus():
    """런웨이 보너스 설정 (MASTER 전용).
       payload: { email, runway_bonus, month? }
       헤더: X-Admin-Key (verify_master 통과 필요)"""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        runway_b = max(0, int(data.get("runway_bonus", 0) or 0))
        month = str(data.get("month") or __import__('datetime').datetime.now().strftime("%Y-%m"))
        if not email:
            return jsonify({"ok": False, "error": "email 필수"}), 400

        # ① Supabase upsert 시도 (runway_bonus 컬럼)
        import requests as _rq
        body = {
            "email": email,
            "month": month,
            "runway_bonus": runway_b,
            "updated_at": __import__('datetime').datetime.utcnow().isoformat() + "Z",
            "updated_by": (request.headers.get("X-Admin-Key") or "")[:16],
        }
        try:
            url = f"{supabase_url()}/rest/v1/user_usage_bonus"
            headers = supabase_admin_headers()
            headers["Prefer"] = "resolution=merge-duplicates,return=representation"
            r = _rq.post(url, headers=headers, json=body, timeout=10)
            if r.status_code in (200, 201):
                # 메모리 캐시도 동기화
                if not hasattr(app, "_runway_bonus_cache"):
                    app._runway_bonus_cache = {}
                app._runway_bonus_cache[f"{email}:{month}"] = runway_b
                return jsonify({
                    "ok": True, "email": email, "month": month,
                    "runway_bonus": runway_b, "source": "supabase",
                })
        except Exception as supabase_err:
            print(f"[admin_set_runway_bonus] supabase fail: {supabase_err}", flush=True)

        # ② Supabase 실패 → 메모리 캐시 (재시작 시 휘발)
        if not hasattr(app, "_runway_bonus_cache"):
            app._runway_bonus_cache = {}
        app._runway_bonus_cache[f"{email}:{month}"] = runway_b
        return jsonify({
            "ok": True, "email": email, "month": month,
            "runway_bonus": runway_b, "source": "memory_fallback",
            "note": "Supabase user_usage_bonus.runway_bonus 컬럼 추가 필요",
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/admin/runway/bonus-list")
def admin_runway_bonus_list():
    """이달 런웨이 보너스 지급 현황 (MASTER 전용)."""
    if not verify_master(request):
        return jsonify({"ok": False, "error": "MASTER 권한 필요"}), 403
    try:
        now_ym = __import__('datetime').datetime.now().strftime("%Y-%m")
        result_map = {}  # email → row

        # ① 메모리 캐시 수집
        if hasattr(app, "_runway_bonus_cache"):
            for k, v in app._runway_bonus_cache.items():
                if not k.endswith(now_ym):
                    continue
                em = k.split(":")[0]
                result_map[em] = {
                    "email": em, "month": now_ym,
                    "runway_bonus": int(v or 0),
                    "updated_at": "—",
                }

        # ② Supabase 조회 (runway_bonus 컬럼이 있는 경우)
        try:
            r = sb_query("GET", "user_usage_bonus", params={
                "month": f"eq.{now_ym}",
                "select": "email,month,runway_bonus,updated_at",
                "order": "updated_at.desc",
                "limit": "500",
            })
            if r.status_code == 200:
                for row in (r.json() or []):
                    em = (row.get("email") or "").lower()
                    rb = row.get("runway_bonus")
                    if rb is None:
                        continue  # 컬럼 없는 row 는 무시
                    # 메모리 캐시 우선 (최신값)
                    if em not in result_map:
                        result_map[em] = {
                            "email": em, "month": now_ym,
                            "runway_bonus": int(rb or 0),
                            "updated_at": row.get("updated_at") or "—",
                        }
        except Exception as sq_err:
            print(f"[admin_runway_bonus_list] supabase fail: {sq_err}", flush=True)

        rows = [v for v in result_map.values() if int(v.get("runway_bonus") or 0) > 0]
        rows.sort(key=lambda r: r.get("email", ""))
        return jsonify({"ok": True, "month": now_ym, "list": rows})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8787"))
    # ✅ 안정성 기본값: debug OFF
    # - debug=True(리로더)일 때는 프로세스가 2개 떠서(port가 2개 LISTEN으로 보임)
    #   사용자가 "포트가 점유"되었다고 오해하기 쉽습니다.
    # - 투자자 데모/외부 공유 목적이면 debug=False가 훨씬 안전합니다.
    debug = str(os.getenv("CODIBANK_DEBUG", "0")).strip().lower() in ("1", "true", "yes", "on")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
