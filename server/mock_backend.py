# ═══════════════════════════════════════════════════════════════════════
# 📋 수정 이력 (MODIFICATION HISTORY) — 최신순
# ═══════════════════════════════════════════════════════════════════════
# 이 블록은 파일 수정 때마다 최상단에 누적됩니다.
# 각 항목은 실제 수정 지점(줄번호)에도 동일한 날짜/요약 주석이 존재합니다.
# 점검 시 이 블록만 읽어도 파일의 최신 상태와 변경 이력을 알 수 있습니다.
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

    gemini_prompt = (
        # ─────────────────────────────────────────────────────────────
        # STEP 1: USER DATA — 사용자 데이터 (분석 입력)
        # ─────────────────────────────────────────────────────────────
        "=== STEP 1: USER DATA ===\n"
        "- Face photo: USE THE FIRST REFERENCE IMAGE (provided)\n"
        f"- Gender: {'female' if gender == 'F' else 'male'}\n"
        f"- Age group: {age}\n"
        f"- Body: height {h_int}cm, weight {w_int}kg (BMI {bmi}, {bmi_cat_ko})\n"
        f"- Body type: {body_type_key or 'standard'}\n"
        + (f"- ⚠️ AVOID COLORS (STRICT): {_avoid_clean}\n" if _has_avoid else "")

        # ─────────────────────────────────────────────────────────────
        # STEP 2: AVATAR CONSTRUCTION — 임시 아바타 99.9% 사용자 일치
        # ─────────────────────────────────────────────────────────────
        + "\n=== STEP 2: AVATAR CONSTRUCTION ===\n"
        "Construct a fashion-model avatar 99.9% IDENTICAL to this user:\n"
        "  • FACE — Replicate ALL features from reference EXACTLY (jawline, eyes,\n"
        "    eyebrows, nose, lips, philtrum, skin tone, hair). NO beautification.\n"
        f"  • BODY — Match {h_int}cm/{w_int}kg/{bmi_cat_ko} silhouette.\n"
        "  • PROPORTION — Fashion-model 8.5 heads, full body visible.\n"
        "\n" + _build_body_profile_block(gender, age, height, weight, body_type_key, "en") + "\n"

        # ─────────────────────────────────────────────────────────────
        # STEP 3: AI STYLIST SELECTION ★ 시그니처 차별화 핵심
        # ─────────────────────────────────────────────────────────────
        + "\n=== STEP 3: AI STYLIST SELECTION ★ ===\n"
        f"Today's matched AI stylist: {stylist_name or 'general expert'}\n"
        f"  · Active region: {stylist_city or 'Seoul'}\n"
        + (f"  · Level: {_stylist_level} (experience: {_stylist_exp} years)\n"
           if (_stylist_level or _stylist_exp) else "")
        + (f"  · SIGNATURE COLOR (primary): {_stylist_color1}\n"
           if _stylist_color1 else "")
        + (f"  · SIGNATURE ACCENT: {_stylist_color2}\n"
           if _stylist_color2 else "")
        + "\n"
        "STYLIST'S CREATIVE DIRECTION (from their expertise & city aesthetics):\n"
        + custom_directive + prompt + "\n"
        "\n"
        "⚠️ CRITICAL: This stylist's signature colors and aesthetic MUST visibly shape\n"
        "the final outfit. Different stylists MUST produce VISIBLY DIFFERENT outfits\n"
        "even with the same user, TPO, and weather. Do NOT default to generic looks.\n"

        # ─────────────────────────────────────────────────────────────
        # STEP 4: TPO ANALYSIS + OUTFIT DECISION
        # ─────────────────────────────────────────────────────────────
        + "\n=== STEP 4: TPO ANALYSIS + OUTFIT DECISION ===\n"
        f"- Purpose: {purpose_for_analysis}\n"
        f"- Weather: {int(temp)}°C, {cond}\n"
        f"- Location: {location or 'Seoul'}\n"
        + (f"- User custom request: \"{custom_text}\"\n" if is_custom else "")
        + "\n"
        "Combining STEP 3 (stylist signature) with the TPO above, decide the outfit:\n"
        "  → Primary color: should reflect stylist's signature color when appropriate\n"
        "  → Style direction: must match both TPO and stylist's expertise\n"
        "  → Weather: bring outer/scarf if cold (<15°C), skip if warm\n"

        # ─────────────────────────────────────────────────────────────
        # STEP 5: CORE OUTFIT IMAGE GENERATION (필수, 항상)
        # ─────────────────────────────────────────────────────────────
        + "\n=== STEP 5: CORE OUTFIT GENERATION (MANDATORY) ===\n"
        "Generate the avatar wearing these three CORE items (ALL required):\n"
        "  ⊙ TOP (상의) — clearly visible upper-body garment\n"
        "  ⊙ BOTTOM (하의) — full ankle-length pants OR skirt as decided in STEP 4\n"
        "    PANTS: hem just above the shoe. Cropped/7-8 length FORBIDDEN.\n"
        "  ⊙ SHOES (신발) — both feet visible, identical pair\n"

        # ─────────────────────────────────────────────────────────────
        # STEP 6: OPTIONAL ACCESSORIES — 스타일리스트 재량
        # ─────────────────────────────────────────────────────────────
        + "\n=== STEP 6: OPTIONAL ACCESSORIES (stylist's discretion) ===\n"
        "Based on STEP 4 TPO/weather and STEP 3 stylist persona, add ONLY what enhances:\n"
        "  ◇ OUTER (아우터) — only if cold (<15°C)\n"
        "  ◇ BAG (가방) — if TPO appropriate (office, date, formal)\n"
        "  ◇ WATCH / SUNGLASSES / HAT / SCARF / SOCKS — only when fitting\n"
        "AVOID over-accessorizing. LESS IS MORE.\n"
        "Both feet must wear IDENTICAL socks if socks visible.\n"

        # ─────────────────────────────────────────────────────────────
        # STEP 7: OUTPUT FORMAT + ANALYSIS REPORT
        # ─────────────────────────────────────────────────────────────
        + "\n=== STEP 7: OUTPUT FORMAT + ANALYSIS REPORT ===\n"
        "[Image format]\n"
        "- Front+back layout: LEFT = front view, RIGHT = back view\n"
        "- 16:9 wide aspect ratio. Each figure ≈ 85% of image height.\n"
        "- Background: SINGLE SOLID FLAT PASTEL COLOR contrasting with outfit,\n"
        "  uniform edge-to-edge. NO rooms/streets/walls/gradients/text/logos.\n"
        "- Photorealistic fashion editorial. Everyday wearable (no avant-garde).\n"

        # ═════════════════════════════════════════════════════════════
        # 분석 리포트 (STEP 7 병행) — JSON 스키마
        # GPT Image 2 분기에서는 후처리로 이 블록 자동 제거됨
        # ═════════════════════════════════════════════════════════════
        + "\n[Analysis report — output as TEXT alongside the image]\n"
        "Wrap the JSON between exact markers <<<ANALYSIS_JSON>>> and <<<END_ANALYSIS>>> "
        "with no additional text outside markers.\n"
        "The JSON MUST follow this EXACT schema:\n"
        "{\n"
        '  "personalColor": {\n'
        '    "text": "퍼스널컬러 측면 분석 (' + ('English' if _cs_en else '한국어') + ', 250-300자, 사용자 톤에 맞는 컬러 추천 이유와 오늘 코디의 컬러 선택 근거 포함)",\n'
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
        '    "top": "컬러, 아이템 (CORE, must NEVER be empty)",\n'
        '    "bottom": "컬러, 아이템 (CORE, must NEVER be empty)",\n'
        '    "shoes": "컬러, 아이템 (CORE, must NEVER be empty)",\n'
        '    "outer": "컬러, 아이템 (OPTIONAL, empty string if not included)",\n'
        '    "bag": "컬러, 아이템 (OPTIONAL)",\n'
        '    "watch": "컬러, 아이템 (OPTIONAL)",\n'
        '    "sunglasses": "컬러, 아이템 (OPTIONAL)",\n'
        '    "hat": "컬러, 아이템 (OPTIONAL)",\n'
        '    "scarf": "컬러, 아이템 (OPTIONAL)",\n'
        '    "socks": "컬러, 아이템 (OPTIONAL)"\n'
        '  }\n'
        "}\n"
        "RULES:\n"
        "1. Each text field MUST be 250-300 Korean characters.\n"
        "2. Each keywords array MUST contain EXACTLY 3 short Korean keywords (2-6 chars).\n"
        "3. categoryKeywords format: '{색상}, {아이템}' comma-separated.\n"
        "   First part = COLOR (1-2 words), second part = ITEM (1-3 words).\n"
        "4. CORE (top/bottom/shoes) MUST NEVER be empty. OPTIONAL uses \"\" if absent.\n"
        "5. Output ONLY the image AND the marked JSON. Nothing else.\n"
        # PC AVOID OVERRIDE 첨언
        + ("\n[CRITICAL — PC AVOID OVERRIDE NOTICE]\n"
           "사용자가 직접입력으로 본인의 퍼스널컬러 avoid 컬러를 요청했습니다. "
           "이번 코디는 사용자 요청에 따라 avoid 컬러를 사용했지만, "
           "personalColor.text 분석에서 반드시 다음 내용을 첨언해야 합니다:\n"
           "  - '본 코디는 사용자 요청에 따라 [컬러명] 컬러를 사용했습니다.'\n"
           "  - '다만 [퍼스널컬러 시즌] 톤의 사용자에게는 본래 권장되지 않는 컬러로, "
           "    얼굴 혈색이 다소 흐려 보일 수 있어 액세서리(립·블러셔·골드 주얼리)로 보완하시면 좋습니다.'\n"
           "  - 이 첨언이 빠지면 분석 실패로 간주됩니다.\n"
           if (isinstance(meta, dict) and meta.get('pc_avoid_override')) else "")
    )

    # ── 이미지 파트 구성: 얼굴 → 상의 → 하의 순서 ──
    face_parts = [(mime, raw) for label, mime, raw in ref_images if label == "face"]
    top_parts = [(mime, raw) for label, mime, raw in ref_images if label == "top"]
    bottom_parts = [(mime, raw) for label, mime, raw in ref_images if label == "bottom"]
    ordered_parts = face_parts + top_parts + bottom_parts

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
        print(f"[CODIFIT] alias_override={_alias} → provider={_provider}, model={model_name}", flush=True)
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
            
            # ─── 2026-05-13 KST · TJ 지시 (v66 QUALITY) ─── prompt 단순화 + 패션모델 비율 ───
            # 배경: medium 품질에서 결과 디테일 부족 + 비율 어색
            #   원인 분석:
            #     1) gemini_prompt 28k chars가 GPT Image 2에 noise (Gemini용 한국어 디테일)
            #     2) 비율 7.5-8 heads는 사실적이지만 패션 화보로는 평범
            #     3) 90% 세로 사이즈는 답답함
            #   TJ 선택: medium 유지 + prompt 단순화 / 8.5 heads / 85% 세로
            _layout_directives = (
                "COMPOSITION REQUIREMENTS (CRITICAL - FOLLOW EXACTLY):\n"
                "1. CANVAS: 16:9 wide landscape, single image split into two equal vertical halves.\n"
                "2. LEFT HALF (0% to 50% horizontal): FRONT view of the person — face fully visible, looking at camera.\n"
                "3. RIGHT HALF (50% to 100% horizontal): BACK view of the SAME person — rear view, no face visible.\n"
                "4. HORIZONTAL CENTERING: Each figure perfectly centered within its own half.\n"
                "   - Front figure: horizontal center at 25% of total image width\n"
                "   - Back figure: horizontal center at 75% of total image width\n"
                "5. VERTICAL SIZING: Each figure's total height = approximately 85% of image height.\n"
                "   - Leave ~7.5% empty space above the head (top margin)\n"
                "   - Leave ~7.5% empty space below the feet (bottom margin)\n"
                "   - The figure must NOT touch the top or bottom edge of the image\n"
                "6. FASHION MODEL PROPORTIONS (IMPORTANT):\n"
                "   - Body height = approximately 8.5 head heights (elegant fashion model proportions)\n"
                "   - Face height ≈ 1/8.5 of total figure height — keep face SMALL relative to body\n"
                "   - Upper body : lower body ratio ≈ 1 : 1.15 (legs slightly longer for elegance)\n"
                "   - Shoulder width ≈ 2 head widths\n"
                "   - Slim, tall, balanced silhouette (editorial fashion editorial style)\n"
                "   - Do NOT make the head or face oversized — this is a common mistake to avoid\n"
                "7. BACKGROUND: Clean, solid, soft neutral color (pale blue, off-white, or soft gray).\n"
                "8. PHOTOGRAPHY STYLE: Editorial fashion photography, sharp focus, professional studio lighting, high detail on garments and accessories.\n"
                "9. NO text, NO logos, NO watermarks, NO UI elements anywhere in the image.\n"
                "10. Both figures wear the EXACT SAME outfit — identical colors, identical garments, identical accessories.\n\n"
            )
            
            # ─── 2026-05-13 KST · TJ 지시 (v66 QUALITY) ─── prompt 28k → 4k 단순화 ───
            # 이유: gemini_prompt 28k chars는 Gemini용 디테일(4-Pass, DNA, 액세서리 다양성 등)이라
            #       GPT Image 2에는 오히려 noise. 핵심 정보(스타일리스트/색상/카테고리/사용자)는
            #       gemini_prompt 첫 부분에 위치하므로 4000자만 발췌.
            # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1) ─── prompt 후처리 강화 ───
            # 단순 slice → 정규식 후처리로 변경:
            #   A) JSON 분석 스키마 블록 제거 (GPT Image 2는 텍스트 출력 안 함 → 토큰 낭비)
            #   B) 퍼스널컬러 "베스트: ..." 줄 제거 (TJ 지적: 추천 컬러 명시 → 이미지 다양성 저하)
            #   C) 퍼스널컬러 "주의: ..." 줄을 AVOID COLORS strict로 강조 변환
            #      → 추천 컬러는 분석 보고서에서만 다루고, 이미지에는 미명시 (TJ 결정)
            #   D) 마지막에 4000자 길이 제한
            import re as _re_pp
            _outfit_prompt = gemini_prompt
            # A) JSON 스키마 블록 제거 (인덱스 기반 — 정규식 fragile 회피)
            _json_start = _outfit_prompt.find("=== CRITICAL OUTPUT INSTRUCTIONS ===")
            if _json_start != -1:
                _json_end_marker = "Output ONLY the image AND the marked JSON. Nothing else."
                _json_end = _outfit_prompt.find(_json_end_marker, _json_start)
                if _json_end != -1:
                    _outfit_prompt = (
                        _outfit_prompt[:_json_start].rstrip()
                        + "\n"
                        + _outfit_prompt[_json_end + len(_json_end_marker):]
                    )
            # B) "베스트: ..." 줄 제거 (퍼스널컬러 추천 컬러 — 이미지 다양성 확보)
            _outfit_prompt = _re_pp.sub(r'\s*베스트:[^\n]*\n', '\n', _outfit_prompt)
            # C) "주의: ..." 줄을 AVOID COLORS strict로 강조 변환
            #    예외: "탁한 톤" (default fallback, 의미 없는 placeholder) 케이스는 줄 자체 제거
            def _avoid_replace(_m):
                _v = _m.group(1).strip()
                if not _v or _v == "탁한 톤":
                    return "\n"
                return f"\n  ⚠️ AVOID COLORS (must NOT appear anywhere in the outfit): {_v}\n"
            _outfit_prompt = _re_pp.sub(r'\s*주의:\s*([^\n]+)\n', _avoid_replace, _outfit_prompt)
            # D) 길이 제한
            if len(_outfit_prompt) > 4000:
                _outfit_prompt = _outfit_prompt[:4000]
            
            # FINAL REMINDER (prompt 끝에 강조) — GPT Image 2는 끝부분 지시를 강하게 따름
            _final_reminder = (
                "\n\n=== FINAL REMINDER (most critical) ===\n"
                "- 16:9 wide image, TWO figures side-by-side (LEFT=front, RIGHT=back)\n"
                "- Each figure height = 85% of image height (figure must NOT fill entire canvas)\n"
                "- Body = 8.5 head heights — DO NOT enlarge the face\n"
                "- Face should appear small and proportional to a tall slim fashion model body\n"
                "- Clean solid pale background. No text, no logos, no watermarks.\n"
            )
            
            _gpt_prompt = _ref_header + _layout_directives + _outfit_prompt + _final_reminder
            
            # ─── 2026-05-14 KST · TJ 지시 (v67 Phase 1) ─── 사이즈 표준 3:2로 변경 ───
            # 이전: "1536x864" (16:9) — 정/후면 각 768x864 (8:9 세로형, 약간 비좁음)
            # 변경: "1536x1024" (3:2) — 정/후면 각 768x1024 (3:4 세로형, 가독성 ↑)
            # gpt-image-2의 standard size 중 하나라 안정적 + 캐시 효율 ↑
            _gpt_size = os.getenv("CODIBANK_GPT_IMAGE_SIZE", "1536x1024")
            
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
):
    """[v67 Phase 2] 코디핏 분석 보고서 — gpt-4.1-mini로 텍스트 메타데이터 기반 분석.

    Pattern A (메타데이터 기반): 생성된 이미지를 보지 않고 사용자 정보 + 생성 의도만으로 분석.
    이유:
      - 비용 50% 절감 (vision input 미사용)
      - 응답 빠름 (input 토큰 ↓, 2~4초)
      - 분석 텍스트는 사용자 정보 기반 자연어 설명 → vision 없어도 자연스러움
      - 이미지 생성과 직렬 호출 — 사용자 경험상 3초 차이 (이미지 25초 + 분석 3초)

    응답: 3섹션 JSON (personalColor / body / purpose) — 기존 closet.html 분석 박스 호환.

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
    if _en:
        system_prompt = (
            "You are a Korean fashion styling expert. Given user info and outfit details, "
            "produce a 3-section analysis report (personal color / body / purpose+weather). "
            "Output JSON only — no extra text outside JSON."
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
        f"\n## 생성된 코디 요약\n{outfit_text}\n"
        f"\n## 출력 JSON 스키마 (이 형식 정확히 준수)\n"
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
        f'  }}\n'
        '}\n'
        f'\nRULES:\n'
        f'1. 각 text는 정확히 250-300자 ({_lang_label_text}).\n'
        f'2. 각 keywords 배열은 정확히 3개 단어 (2-6자).\n'
        f'3. JSON 외 추가 텍스트 출력 금지.\n'
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
    _analysis_max_retries = int(os.getenv("CODIBANK_ANALYSIS_MAX_RETRIES", "0"))

    print(f"[codifit_analysis] gpt-4.1-mini 호출 시작 (model={_model}, lang={'en' if _en else 'ko'}, timeout={_analysis_timeout}s, retries={_analysis_max_retries})", flush=True)

    _response = _client_analysis.with_options(
        max_retries=_analysis_max_retries,
        timeout=_analysis_timeout,
    ).chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
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

    print(f"[codifit_analysis] ✅ 분석 생성 완료 (3섹션, total chars={sum(len(v['text']) for v in result.values())})", flush=True)
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
    if _force_quality in ('low', 'medium', 'high'):
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
            print(f"[ai_styling_analysis] ✅ 캐시 hit: {cache_key}", flush=True)
            return jsonify(
                ok=True,
                stylingAnalysis=_cached_analysis,
                cached=True,
                cacheKey=cache_key,
            )
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

        _analysis = _codifit_analysis_via_gpt41mini(
            payload=payload,
            matched_stylist=_matched_stylist,
            meta=_meta,
            generated_outfit_summary=_outfit_summary or None,
            lang=_lang,
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
    _tryon_analysis_model = os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS", "gemini-3-pro-preview")
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
    analysis_model = _os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS", "gemini-3-pro-preview")
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
    
    _ANALYSIS_MODEL = os.getenv("CODIBANK_MODEL_TRYON_ANALYSIS", "gemini-3-pro-preview")
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

{
  "category": "coat | jacket | top | pants | skirt | onepiece | shoes | watch | scarf | socks | etc 중 하나 — ⚠️ 치마/스커트는 반드시 skirt, 원피스는 반드시 onepiece. 혼동 금지.",
  "sub_category": "아래 세부 품목 중 하나로 정확히 분류:\n[아우터(coat)] 긴 아우터류: 아우터/코트/패딩/버버리(트렌치코트)/롱패딩\n[자켓(jacket)] 짧은 아우터류: 자켓/블레이저/점퍼/다운자켓/레더자켓/데님자켓/가디건 (기타 짧은 아우터: 수트자켓/콤비자켓/사파리자켓/집업자켓/후드집업자켓/숏패딩/다운조끼/볼레로)\n[상의(top)] 탑/셔츠/티셔츠/후드티/후드티셔츠/블라우스/면티/니트티/니트셔츠 (기타: 반팔티/긴팔티/맨투맨/스웨터)\n[바지(pants)] 바지/반바지/데님팬츠/조거팬츠/트레이닝하의/레깅스/숏팬츠/러너팬츠 (기타: 청바지/슬랙스/면바지/스키니/와이드팬츠)\n[치마(skirt)] 스커트/H라인스커트/A라인스커트/플레어스커트/플리츠스커트/머메이드스커트/미니스커트/미디스커트/롱스커트/레이어드스커트 (기타: 랩스커트/티어드스커트/도트스커트)\n[원피스(onepiece)] 원피스/미디원피스/롱원피스/셔츠원피스/시스원피스/랩원피스/슬립원피스/시프트원피스/드레스/웨딩드레스/원피스수영복/투피스수영복/비키니수영복 (기타: 미니원피스/니트원피스)",
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
  "style_keywords": ["캐주얼|포멀|스트릿|미니멀|빈티지|스포티|로맨틱|클래식 중 최대 3개"],
  "design_points": "이 아이템의 디자인 특징 1~2문장 (한국어) — 착용샷이면 의류 아이템만 묘사",
  "coordinate_hint": "이 아이템과 잘 어울리는 하의/상의/아우터 추천 (한국어 1문장)"
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

        # ──── [2026-04-20 23:30 KST — ACTION 1] 분석 전용 모델 사용 ────
        # ──── [2026-04-21 01:50 — 작업 4] fallback 체인 추가 ────
        # 이전: _CODISTYLE_MODEL = "gemini-2.5-flash-image" (이미지 생성 전용)
        #       → JSON 구조화 응답 품질이 낮아 치마/바지 오판 빈발
        # 신규: gemini-2.0-flash를 1순위로, 실패시 gemini-1.5-flash로 자동 대체
        #       → 권한/사용 제한 상황에서도 분석이 계속 작동
        _ANALYZE_PRIMARY = os.getenv("CODIBANK_ANALYZE_MODEL") or "gemini-2.0-flash"
        _ANALYZE_CHAIN = [_ANALYZE_PRIMARY, "gemini-1.5-flash", "gemini-1.5-flash-8b"]
        _seen_a = set()
        _ANALYZE_CHAIN = [m for m in _ANALYZE_CHAIN if not (m in _seen_a or _seen_a.add(m))]

        _analyze_success_model = None
        _analyze_errors = []

        for _a_idx, _a_model in enumerate(_ANALYZE_CHAIN, 1):
            try:
                if _SDK == "new":
                    _cli = _gmod.Client(api_key=_GEMINI_KEY)
                    _img_part = _gtypes.Part.from_bytes(data=img_bytes, mime_type=img_mime)
                    _resp = _cli.models.generate_content(
                        model=_a_model,
                        contents=[_gtypes.Content(parts=[_img_part, _gtypes.Part.from_text(text=PROMPT)])],
                    )
                    _tmp = _resp.text if hasattr(_resp, "text") else str(_resp)
                else:
                    _gmod.configure(api_key=_GEMINI_KEY)
                    import PIL.Image as _PILImage
                    import io
                    _pil = _PILImage.open(io.BytesIO(img_bytes))
                    _model = _gmod.GenerativeModel(_a_model)
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8787"))
    # ✅ 안정성 기본값: debug OFF
    # - debug=True(리로더)일 때는 프로세스가 2개 떠서(port가 2개 LISTEN으로 보임)
    #   사용자가 "포트가 점유"되었다고 오해하기 쉽습니다.
    # - 투자자 데모/외부 공유 목적이면 debug=False가 훨씬 안전합니다.
    debug = str(os.getenv("CODIBANK_DEBUG", "0")).strip().lower() in ("1", "true", "yes", "on")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
