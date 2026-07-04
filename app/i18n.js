/* ══════════════════════════════════════════
   CodiBank i18n (한국어 기본 / English 선택)
   - localStorage('codibank_lang')에 'ko' 또는 'en' 저장
   - 각 페이지에서 <script src="i18n.js"></script> 추가
   - DOMContentLoaded 시 자동 적용
══════════════════════════════════════════ */
(function(){
'use strict';

var LANG_KEY = 'codibank_lang';

/* ─── 2026-07-04 KST · TJ 지시 ─── 다국어 코어 v2 ─────────────────────────
   구조: 한국어 키 고정 + 언어 레이어. DICT(영어)는 무변경, DICT_JA/DICT_ZH 추가.
   폴백: ja/zh 미번역 키 → 영어 값 사용 (외국 사용자에게 한글 노출 금지).
   전환: 원본맵(_origMap) 기반 재적용이라 ko↔en↔ja↔zh 자유 전환. */
var LANGS = {
  ko: { label: '한국어',  short: 'KO' },
  en: { label: 'English', short: 'EN' },
  ja: { label: '日本語',   short: 'JA' },
  zh: { label: '中文',     short: 'ZH' },
  es: { label: 'Español',  short: 'ES' },  // 2026-07-04 KST · TJ 지시 — 스페인어 추가
};

// ── 번역 사전 (페이지별) ──
var DICT = {

  // 공통 (풋바, 토스트 등)
  _common: {
    '내옷장':          'Closet',
    '코디앨범':        'Album',
    'ITEM등록':        'Add Item',
    '코디하기':        'Style It',
    '전체삭제':        'Delete All',
    '저장':            'Save',
    '공유':            'Share',
    '삭제':            'Delete',
    '로그인':          'Log In',
    '회원가입':        'Sign Up',
    '로그아웃':        'Log Out',
    '취소':            'Cancel',
    '확인':            'OK',
    '닫기':            'Close',
    '필수':            'Required',
    '선택':            'Optional',
    '기타':            'Other',
    '비즈니스':        'Business',
    '주말여행':        'Weekend Trip',
    '코디':            'Outfit',
  },

  // closet.html
  closet: {
    '내옷장 - 코디뱅크':                    'My Closet - CodiBank',
    '내옷장':                               'My Closet',
    '위치 확인 중…':                        'Checking location…',
    '로딩중':                               'Loading',
    '오늘':                                 'Today',
    '코디 목적 선택':                        'Select Purpose',
    '직접입력 (최대 30자)':                  'Custom input (max 30 chars)',
    '직접입력':                              'Custom',
    '30자 이내로 입력해주세요.':              'Please enter within 30 characters.',
    '코디 날짜 선택':                        'Select Date',
    '코디를 생성할 날짜를 선택하세요':        'Choose a date for your outfit',
    '오늘의 코디':                           "Today's Outfit",
    '내일의 코디':                           "Tomorrow's Outfit",
    'AI 스타일리스트 호출':                  'Call AI Stylist',
    '목적과 날짜를 먼저 선택하세요':          'Select purpose and date first',
    '코디 목적별 AI 스타일리스트가 수 백명씩 준비돼있다.': 'Hundreds of AI stylists ready for each purpose.',
    '키워드로 코디 스타일을 분석해준다.':      'Analyzes your style with keywords.',
    '모바일 옷장에서 쉽게 코디할 수 있는 해법을 제공한다.': 'Easy outfit solutions from your mobile closet.',
    'AI 추천코디 이야기':                    'AI Styling Story',
    '목적을 선택하면 AI가 날씨에 맞는 코디를 추천해요.': 'Select a purpose and AI recommends weather-appropriate outfits.',
    '✦ AI 스타일링 포인트':                  '✦ AI Styling Points',
    '스타일 키워드':                         'Style Keywords',
    '카테고리별 코디 포인트':                 'Category Styling Points',
    '↓ 아래 모바일 옷장과 AI 매칭 분석 중':  '↓ Matching with your mobile closet',
    '코디추천 AI 스타일링':                  'AI Styling Recommendation',
    '추천 이미지 생성중':                    'Generating outfit image',
    '초기화 중…':                            'Initializing…',
    '얼굴 사진 불러오는 중…':                'Loading face photo…',
    // 코디 목적
    '출퇴근':                               'Commute',
    '비즈니스':                              'Business',
    '캐주얼':                               'Casual',
    '데이트':                               'Date',
    '여행':                                 'Travel',
    '주말여행':                              'Weekend Trip',
    '국내여행':                              'Domestic Trip',
    '해외여행':                              'Overseas Trip',
    '운동/레저':                             'Sports/Leisure',
    '결혼식/행사':                           'Wedding/Event',
    '면접':                                 'Interview',
    '주말외출':                              'Weekend Out',
    '지인모임':                              'Social Gathering',
    '소개팅':                               'Blind Date',
    '파티':                                 'Party',
    '파티룩':                               'Party Look',
    '등산':                                 'Hiking',
    // 날씨/요일
    '맑음':                                 'Clear',
    '흐림':                                 'Cloudy',
    '비':                                   'Rain',
    '눈':                                   'Snow',
    '구름많음':                              'Mostly Cloudy',
    '예보 없음':                             'No forecast',
    '일':    'Sun', '월':    'Mon', '화':    'Tue',
    '수':    'Wed', '목':    'Thu', '금':    'Fri', '토':    'Sat',
    // AI 추천 / VTO
    '추천 이미지 없음':                      'No outfit image',
    '무제한':                                'Unlimited',
    '다시 코디':                             'Retry',
    '다시코디':                              'Retry',
    '얼굴 사진을 등록하면 내 얼굴로 스타일링!': 'Register face photo for personalized styling!',
    '마이페이지에서 얼굴 사진을 등록하면 내 얼굴에 코디를 입혀드려요.': 'Add a face photo in My Page to see outfits on you.',
    '등록':                                 'Register',
    '유료 구독 또는 플랜 업그레이드 후 계속 이용하실 수 있어요.': 'Upgrade your plan to continue.',
    // 모바일 옷장
    '모바일 옷장':                           'Mobile Closet',
    '클릭하면 AI가 추천한 코디를 내 옷에서 찾아드립니다': 'Tap to find AI-recommended outfits from your closet',
    'AI 추천코디 × 내 옷장 유사도 분석':     'AI Outfit × Closet Similarity',
    'AI 코디를 먼저 생성하면 유사도를 분석해드려요.': 'Generate AI outfit first to analyze similarity.',
    '카테고리 추가':                         'Add Category',
    '어느 카테고리에 추가할까요?':            'Which category?',
    '추가하기':                              'Add',
    '추가':                                 'Add',
    '등록된 아이템 없음 — 추가해보세요':      'No items — add some!',
    'AI 코디 키워드 없음':                   'No AI keywords yet',
    '이 아이템은 추천코디와 매칭점수':        'This item matches the outfit score',
    '스와이프해서 AI 추천 아이템을 확인하세요': 'Swipe to see AI-recommended items',
    '← 스와이프로 아이템을 탐색하세요':       '← Swipe to browse items',
    '아이템 없음':                           'No items',
    '카테고리별 AI 추천 키워드가 아직 없어요.': 'No AI category keywords yet.',
    '검색 결과가 없어요':                     'No search results',
    '아이템':                                'Item',
    '개':                                   '',
    // 카테고리
    '코트':     'Coat',    '자켓':     'Jacket',
    '탑/셔츠/블라우스': 'Top/Shirt', '바지/스커트': 'Pants/Skirt',
    '양말':     'Socks',   '구두/운동화': 'Shoes',
    '시계':     'Watch',   '스카프/목도리': 'Scarf',
    '기타':     'Other',
  },

  // codistyle.html
  codistyle: {
    '코디하기 - 코디뱅크':                   'Style It - CodiBank',
    '지금은 가장 안정적인 방식부터 확인합니다.': 'Starting with the most stable method.',
    '링크/얼굴/체형은 잠시 빼고,':            'Setting aside links/face/body type,',
    '상의 사진 1장 + 하의 사진 1장':          '1 top photo + 1 bottom photo',
    '만으로 AI 착장 이미지를 생성합니다.':     ' to generate AI outfit images.',
    '상의':                                 'Top',
    '하의':                                 'Bottom',
    '상의 이미지':                           'Top Image',
    '하의 이미지':                           'Bottom Image',
    '사진촬영':                              'Camera',
    '사진선택':                              'Gallery',
    '촬영':                                 'Camera',
    '링크':                                 'Link',
    '준비중':                               'Coming Soon',
    '준비 중…':                             'Preparing…',
    '상의 삭제':                             'Remove Top',
    '하의 삭제':                             'Remove Bottom',
    '얼굴 사진':                             'Face Photo',
    '(선택)':                                '(Optional)',
    '내 얼굴로 착장 이미지를 만들어요.':       'Create outfit images with your face.',
    '프로필 사진 자동 불러오기':               'Auto-load profile photo',
    '✓ 등록됨':                              '✓ Registered',
    '이미지 준비중…':                         'Preparing image…',
    '서버에 업로드중…':                       'Uploading…',
    '업로드중…':                             'Uploading…',
    '업로드 완료':                            'Upload complete',
    '착장 이미지 생성':                       'Generate Outfit',
    'AI 착장 이미지 생성':                    'AI Generate Outfit',
    '상의와 하의를 모두 업로드하면 생성이 가능합니다': 'Upload both top and bottom to generate',
    '준비 완료 — 생성 버튼을 눌러주세요':      'Ready — tap Generate',
    'Gemini가 착장 이미지를 생성하고 있어요…': 'Gemini is generating your outfit…',
    '(10~25초 소요)':                         '(10-25 seconds)',
    '1차 안정화:':                            'Phase 1:',
    '선택한 상의/하의 사진만':                 'Selected top/bottom photos only',
    '으로 Gemini 착장 이미지를 생성합니다.':    ' — generating Gemini outfit images.',
    '착장 이미지가 여기에 생성됩니다':          'Your outfit image will appear here',
    '착장 이미지 생성에 실패했어요':            'Failed to generate outfit image',
    '다시':                                  'Retry',
    // AI 스타일링 진행 상태
    '한도 초과':                             'Limit exceeded',
    '남은 0회':                              '0 remaining',
    '회 가능':                               ' remaining',
    '잠시만 기다려주세요…':                   'Please wait…',
    'AI 스타일링 작업중':                    'AI styling in progress',
    'AI 스타일링 호출 완료':                 'AI styling complete',
    '다시코디 버튼으로 새 스타일리스트 호출': 'Tap Retry for a new stylist',
    'AI 코디 분석 중…':                      'Analyzing AI outfit…',
    '추천 스타일링 완료 ✨':                  'Recommended styling done ✨',
    '스타일링 이미지 생성 중…':               'Generating styling image…',
    '새로운 코디를 준비 중…':                 'Preparing new outfit…',
    '얼굴 없이 다시 생성 중…':               'Regenerating without face…',
    'OpenAI 이미지 생성 중…':                'OpenAI generating image…',
    'OpenAI 업데이트 중…':                   'OpenAI updating…',
    '캐시 표시중':                           'Showing cache',
    'OpenAI 생성중…':                        'OpenAI generating…',
    '날씨 정보 없음':                        'No weather info',
    '코디를 준비 중이에요. AI 스타일리스트가 최적의 룩을 선정하고 있어요.': 'Preparing outfit. AI stylist is selecting the best look.',
    '체형 커버 코디':                        'Body-flattering outfit',
    '추천코디 요약':                         'Outfit Summary',
    '코디 목적을 먼저 선택하세요':           'Select outfit purpose first',
    '오늘 날짜':                             "Today's date",
    '가 자동으로 선택됩니다.':               ' is auto-selected.',
    '선택 가능:':                            'Available:',
    '이후':                                  'onward',
    '실시간 AI':                             'Real-time AI',
    '스타일링':                              'Styling',
    '개인정보처리방침':                       'Privacy Policy',
    '이용약관':                              'Terms of Use',
  },

  // camera.html
  camera: {
    '아이템 등록 - 코디뱅크':                 'Add Item - CodiBank',
    '내 옷 장':                              'My Closet',
    '아이템 등록':                            'Add Item',
    '당신의 오프라인 패션아이템을 촬영하세요':  'Photograph your fashion items',
    '전면 아이템':                            'Front Item',
    '1장(필수)':                              '1 photo (required)',
    '아이템의 전면(최소 1장)을 촬영하는 것은 필수입니다.': 'At least 1 front photo is required.',
    '전면 사진을 추가해주세요':                'Please add a front photo',
    '촬영':                                  'Capture',
    '사진 선택':                              'Gallery',
    '후면 아이템':                            'Back Item',
    '후면은 선택 촬영입니다. 가능하면 촬영해두면 확인이 쉬워져요.': 'Back photo is optional but helpful.',
    '후면 사진(선택)':                         'Back photo (optional)',
    '브랜드/기타':                            'Brand/Other',
    '로고/택/브랜드 정보는 선택입니다. 자동 인식 정확도가 올라가요.': 'Brand info is optional. Improves auto-recognition.',
    '브랜드/택/기타 정보(선택)':               'Brand/tag/other info (optional)',
    '전면 촬영 후 등록':                      'Register after front photo',
    '카테고리':                               'Category',
    '촬영 또는':                              'Capture or',
    '이미 촬영한 사진 선택':                   'select existing photos',
    '도 가능합니다.':                          '.',
    '만 있어도 등록할 수 있어요.':             ' is enough to register.',
    '기본은':                                'Default is',
    'AI 자동':                               'AI Auto',
    '분류 · 필요하면 직접 선택':               'classification · manual if needed',
    '* 등록하기를 누르면 AI가':                '* When you tap Register, AI will',
    '카테고리/컬러/브랜드':                    'Category/Color/Brand',
    '를 자동 인식해 아이템으로 저장합니다.':     ' auto-detect and save the item.',
    '분석 중…':                               'Analyzing…',
    '카테고리/컬러/브랜드를 인식하고 있어요.':  'Recognizing category/color/brand.',
    '대기':                                   'Standby',
    '컬러':                                   'Color',
    '브랜드':                                 'Brand',
    '잠시만요…':                               'Please wait…',
    '후면/브랜드·기타 정보는 선택입니다.':       'Back/brand info is optional.',
  },

  // mypage.html
  mypage: {
    '마이페이지 - 코디뱅크':                  'My Page - CodiBank',
    '마이페이지':                             'My Page',
    '사용자':                                'User',
    '계정 관리':                              'Account',
    '프로필 수정':                            'Edit Profile',
    '구독 플랜':                              'Subscription',
    '서비스':                                'Services',
    '내 옷장 바로가기':                       'Go to My Closet',
    '공유·판매 관리':                          'Share & Sell',
    '기타':                                  'Others',
    '이용약관':                               'Terms of Service',
    '이용약관 준비 중입니다.':                  'Terms of Service coming soon.',
    '개인정보처리방침':                         'Privacy Policy',
    '개인정보처리방침 준비 중입니다.':           'Privacy Policy coming soon.',
    '환불정책':                                 'Refund Policy',
    '플랜':                                   ' Plan',
    '로그아웃':                                'Log Out',
    '회원탈퇴':                                'Delete Account',
    '코디쌤':                                 'Codissam',
    'Ai 옷장':                                'AI Closet',
    '회 가능':                                ' remaining',
    '아이템':                                  'Items',
    '개':                                     '',
    '주식회사 종로신사 | 대표이사 신용남':      'Jongno Sinsa Inc. | CEO Shin Yong-nam',
    '서울시 종로구 종로 223, 우교빌딩 4층':    '4F Ugyo Bldg, 223 Jongno, Seoul',
    '운영책임자 백태섭 | 02-743-1850':         'Manager: Baek Tae-seop | 02-743-1850',
    '플랜':                                   ' Plan',
  },

  // profile.html
  profile: {
    '프로필 수정 - 코디뱅크':                  'Edit Profile - CodiBank',
    '프로필 수정':                             'Edit Profile',
    '프로필 사진 변경':                        'Change Photo',
    '기본 정보':                               'Basic Info',
    '닉네임':                                 'Nickname',
    '이메일 (아이디)':                         'Email (ID)',
    '휴대폰 번호':                             'Phone',
    '체형 정보':                               'Body Info',
    '(AI 코디 정확도 향상)':                   '(Improves AI accuracy)',
    '성별':                                   'Gender',
    '남성':                                   'Male',
    '여성':                                   'Female',
    '연령대':                                 'Age Group',
    '10대':                                   'Teens',
    '20대':                                   '20s',
    '30대':                                   '30s',
    '40대':                                   '40s',
    '50대+':                                  '50s+',
    '키':                                     'Height',
    '몸무게':                                 'Weight',
    '비밀번호 변경':                           'Change Password',
    '(변경 시에만 입력)':                      '(Only when changing)',
    '새 비밀번호':                             'New Password',
    '영문+숫자 4자 이상':                      '4+ chars, letters & numbers',
    '비밀번호 확인':                           'Confirm Password',
    '비밀번호 재입력':                         'Re-enter password',
    '사진 삭제':                               'Delete Photo',
    '사진 변경':                               'Change Photo',
    '퍼스널컬러 분석':                          'Analyze Personal Color',
    '나의 신체정보':                            'My Body Info',
    '리포트 다운로드':                          'Download Report',
    '리셋':                                    'Reset',
    '저장하기':                                'Save',
    '새 비밀번호':                              'New Password',
    '50대':                                    '50s',
    '60대+':                                   '60s+',
    '닉네임 입력':                              'Enter nickname',
    '어울리는 컬러':                            'Best Colors',
    '어울리는 컬러 (Best)':                     'Best Colors',
    '피해야 할 컬러':                           'Colors to Avoid',
    '피해야 할 컬러 (Worst)':                   'Colors to Avoid',
    '상의 매칭 컬러':                           'Top Match Colors',
    '하의 매칭 컬러':                           'Bottom Match Colors',
    '이미지 생성':                              'Image Gen',
    '아이템 등록':                              'Item Reg',
    'AI 코디 정확도 향상':                      'Improves AI styling accuracy',
    '변경 시에만 입력':                         'Only when changing',
    '성별 선택 후 표시':                        'Shown after selecting gender',
    '퍼스널컬러 분석 중입니다':                  'Analyzing Personal Color...',
    '저장하기':                               'Save',
    '✅ 프로필이 저장되었습니다.':               '✅ Profile saved.',
    '저장에 실패했습니다. 다시 시도해주세요.':   'Save failed. Please try again.',
    '체형 선택':                               'Select Body Type',
    '(성별 선택 후 표시)':                     '(Select gender first)',
    '성별을 먼저 선택해주세요':                 'Please select gender first',
    '스타일 가이드':                            'Style Guide',
    '추천하는 컬러':                            'Recommended Colors',
    '퍼스널 컬러 분석':                        'Personal Color Analysis',
    '퍼스널컬러 분석 중…':                     'Analyzing personal color…',
    '프로필 사진을 선택한 후 분석을 시작하세요': 'Select a profile photo to start analysis',
    '피해야 할 컬러':                           'Colors to Avoid',
    '🎨 퍼스널컬러 분석':                      '🎨 Analyze Personal Color',
    '5MB 이하 이미지를 선택해주세요.':          'Please select an image under 5MB.',
    '비밀번호가 일치하지 않습니다.':             'Passwords do not match.',
    '비밀번호는 4자 이상 입력해주세요.':         'Password must be 4+ characters.',
    '비밀번호 변경 실패: ':                     'Password change failed: ',
    '비밀번호가 변경되었습니다.':               'Password changed.',
    'Ai 옷장':                                'AI Closet',
    '코디쌤':                                 'Codissam',
    '(AI 피부톤 분석)':                        '(AI Skin Tone Analysis)',
  },

  // index.html (랜딩페이지)
  index: {
    'AI가 매일':                     'Every day, AI crafts',
    '완벽한 코디':                   'the perfect outfit',
    '제안해드려요':                   'just for you',
    '날씨·목적·체형을 분석해서 당신만을 위한 스타일링을 추천합니다.': 'We analyze weather, occasion & body type to recommend your personalized styling.',
    'AI 코디 추천':                  'AI Styling',
    '맞춤형 스타일링 제안':           'Personalized style recommendations',
    '디지털 옷장':                    'Digital Closet',
    '내 옷을 디지털화하여 관리':       'Digitize and manage your wardrobe',
    '코디하기':                      'Style It',
    'AI가 추천하는 나만의 코디':      'AI-powered outfit coordination',
    '옷은 넘치는데':                  'Your closet is full,',
    '오늘 입을 옷은 없다!':          'but nothing to wear!',
    'codibank에서 ':                 'Solved with ',
    'AI서비스':                      'AI Service',
    '로 해결합니다.':                 ' by CodiBank.',
    '지금 시작하기':                  'Get Started',
    '코디뱅크 로그인':                'Log In to CodiBank',
    '날씨·목적·체형을 분석해서 당신만을 위한': 'Analyzing weather, occasion & body type',
    '퍼스널 스타일링을 실시간으로 추천합니다.': 'for real-time personal styling.',
    '핸드폰에 AI 패션 스타일리스트 수 천명이 준비되어 있습니다.': 'Thousands of AI stylists ready in your phone.',
    '오프라인 옷장에 방치된 옷들을 AI가 모바일 옷장에서 추천코디에 맞게 추천합니다.': 'AI recommends outfits from your offline closet.',
    '당신의 취향과 TPO를 분석해 매일 아침 새로운 스타일링을 제안합니다.': 'Analyzes your taste and TPO for daily styling.',
    '내 모든 옷을 스마트폰 속으로. 언제 어디서든 옷장을 확인하고 관리하세요.': 'All your clothes in your phone. Manage anytime, anywhere.',
    'AI 스타일리스트가 당신의 옷장과 체형에 맞는 최적의 코디를 추천합니다.': 'AI recommends the best outfits for you.',
    '더 알아보기':                    'Learn More',
    '옷장 속 옷은 넘치는데':          'Your closet is overflowing,',
    '항상':                          'yet',
    ' 입을 옷은 없다 !!':            ' nothing to wear !!',
    'codibank에서 AI 추천코디 서비스로 해결해드립니다.': "CodiBank's AI styling has you covered.",
    '서울특별시':      'Seoul',
    '흐림':           'Cloudy',
    '출퇴근':          'Commute',
    '비즈니스':        'Business',
    '지인모임':        'Social',
    '주말외출':        'Weekend',
    '코디 날짜 선택':  'Select date',
    '저장하기':        'Save',
    '다시 코디':       'Retry',
  },

  // album.html
  album: {
    '코디앨범 - 코디뱅크':                     'Outfit Album - CodiBank',
    '앨범 불러오는 중…':                       'Loading album…',
    '저장된 코디가 없어요':                     'No saved outfits',
    '내옷장에서 AI 코디를 추천받고':            'Get AI outfit recommendations',
    '저장하기를 눌러보세요!':                   'and save them!',
    'AI 코디 추천 받기':                       'Get AI Styling',
    '이미지를 불러올 수 없습니다.':             'Unable to load image.',
    '이 코디를 삭제할까요?':                    'Delete this outfit?',
    '장을 모두 삭제할까요?':                    ' outfits?',
    '코디':                                   'Outfit',
    '장':                                     '',
  },

  // login.html
  login: {
    '로그인':                        'Log In',
    '코디뱅크 계정으로 시작하세요':    'Sign in with your CodiBank account',
    '이메일':                        'Email',
    '비밀번호':                      'Password',
    '계정이 없으신가요?':             "Don't have an account?",
    '이메일을 입력해주세요.':          'Please enter your email.',
    '비밀번호를 입력해주세요.':        'Please enter your password.',
    '로그인에 실패했습니다.':          'Login failed.',
    '처음 화면으로':                  'Back to Home',
  },

  // signup.html
  signup: {
    '회원가입':                      'Sign Up',
    'STEP 1 / 3 — 계정 정보':       'STEP 1 / 3 — Account Info',
    'STEP 2 / 3 — 이메일 인증':     'STEP 2 / 3 — Email Verification',
    'STEP 3 / 3 — 체형 정보':       'STEP 3 / 3 — Body Info',
    '이메일 (아이디)':               'Email (ID)',
    '비밀번호 (영문+숫자 6자 이상)':  'Password (6+ chars, letters & numbers)',
    '비밀번호 (영문+숫자 4자 이상)':  'Password (4+ chars, letters & numbers)',
    '비밀번호 확인':                 'Confirm Password',
    '이메일 인증 요청 →':            'Send Verification →',
    '인증 이메일을 보냈습니다':       'Verification email sent',
    '으로 인증 링크를 보냈습니다.':    ' — check your inbox.',
    '이메일을 확인하고':             'Check your email and',
    '인증하기 버튼':                 'click the verify button',
    '을 클릭해주세요.':              '.',
    '메일이 안 보이면 스팸함을 확인해주세요.': "Can't find it? Check your spam folder.",
    '✓ 인증 완료했어요':             '✓ Verified',
    '인증 메일 재발송':              'Resend Email',
    '이메일 인증 완료!':             'Email Verified!',
    '성별':                          'Gender',
    '남성':                          'Male',
    '여성':                          'Female',
    '연령대':                        'Age Group',
    '10대':    'Teens', '20대':    '20s', '30대':    '30s',
    '40대':    '40s',   '50대+':   '50s+',
    '키 (cm)':                       'Height (cm)',
    '몸무게 (kg)':                   'Weight (kg)',
    '가입 완료':                     'Complete Sign Up',
    '이미 계정이 있으신가요?':        'Already have an account?',
    '처음 화면으로':                 'Back to Home',
    '올바른 이메일을 입력해주세요.':   'Please enter a valid email.',
    '이미 가입된 이메일입니다. 로그인해주세요.': 'Email already registered. Please log in.',
    '잠시 후 다시 시도해주세요.':      'Please try again later.',
    '오류가 발생했습니다.':           'An error occurred.',
    '아직 인증이 완료되지 않았습니다. 이메일을 확인해주세요.': 'Not verified yet. Check your email.',
    '인증 이메일을 재발송했습니다. 메일함을 확인해주세요.': 'Verification email resent. Check your inbox.',
    '회원가입에 실패했습니다.':       'Sign up failed.',
    '발송 중…':                      'Sending…',
  },

  // aicloset.html
  aicloset: {
    '추천코디와 유사한 아이템 찾기':         'Find similar items to recommended outfit',
    '터치하면 AI가 내 옷장에서 유사 아이템을 찾아드려요': 'Tap to find similar items in your closet',
    'AI 코디를 먼저 생성해주세요':            'Generate AI outfit first',
    '추천코디와 유사한 아이템을 분석했습니다': 'Analyzed items similar to recommended outfit',
    '코디쌤에서 생성한 추천코디와 가장 유사한 내 옷을 찾아줍니다': 'Find your clothes most similar to AI styling',
    '아이템 등록':                           'Add Item',
    '아이템 없음':                           'No items',
    '카테고리 추가':                         'Add Category',
    '어느 카테고리에 추가할까요?':            'Which category?',
    '이 카테고리에 등록':                     'Add to this category',
    '추가하기':                              'Add',
    '검색 결과가 없어요':                     'No search results',
    '카테고리':                              'Category',
    '아우터':                                'Outerwear',
    '탑/셔츠':                               'Top/Shirt',
    '신발':                                  'Shoes',
    '스카프·포인트':                          'Scarf/Accent',
    '가방':                                  'Bag',
    '시계':                                  'Watch',
    '양말':                                  'Socks',
    '컬러 분석':                             'Color analysis',
    '소재 분석':                             'Material analysis',
    '시즌 분석':                             'Season analysis',
    '컬러 정보 없음':                         'No color info',
    '소재 정보 없음':                         'No material info',
    '스타일 키워드':                          'Style keywords',
    '코디 조합':                             'Outfit combo',
    '카테고리별 코디 포인트':                  'Styling points by category',
    '카테고리별 AI 추천 키워드가 아직 없어요.': 'No AI keywords yet.',
    '← 스와이프로 아이템을 탐색하세요':        '← Swipe to browse items',
    '스와이프해서 AI 추천 아이템을 확인하세요': 'Swipe to check AI recommended items',
    '등록된 아이템 없음 — 추가해보세요':       'No items — add some',
    '오프라인 옷장의 옷들을 디지털 옷장에 저장하면 코디를 추천해드립니다!': 'Save your clothes digitally and get outfit recommendations!',
    '마이페이지에서 얼굴 사진을 등록하면 내 얼굴에 코디를 입혀드려요.': 'Register a face photo in My Page to try on outfits.',
    '얼굴 사진을 등록하면 내 얼굴로 스타일링!': 'Register face photo for personal styling!',
    '유료 구독 또는 플랜 업그레이드 후 계속 이용하실 수 있어요.': 'Upgrade your plan to continue.',
    '먼저 스타일링을 생성해주세요.':           'Please generate styling first.',
    '저장 실패:':                             'Save failed:',
    '스타일링 추천받기':                      'Get styling',
    '초기화 중…':                             'Initializing…',
    '예보 없음':                              'No forecast',
    '개':                                    '',
  },

  // item.html
  item: {
    '아이템 상세 - 코디뱅크':                 'Item Detail - CodiBank',
    '아이템':                                'Item',
    '컬러 미정':                             'Color TBD',
    '아이템 설명이 아직 없습니다. "수정"에서 특징을 추가해보세요.': 'No description yet. Add features in "Edit".',
    '수정':                                  'Edit',
    '삭제':                                  'Delete',
    '아이템 수정':                            'Edit Item',
    '카테고리':                              'Category',
    '브랜드':                                'Brand',
    '컬러':                                  'Color',
    '아이템 설명':                            'Description',
    '저장':                                  'Save',
    '취소':                                  'Cancel',
    '삭제되었습니다.':                        'Deleted.',
    '이 아이템을 삭제할까요?':                 'Delete this item?',
    '삭제에 실패했습니다.':                    'Delete failed.',
    '저장에 실패했습니다.':                    'Save failed.',
    '공유할 이미지가 없습니다.':               'No image to share.',
    '공유/저장에 실패했습니다.':               'Share/save failed.',
    '아이템 ID가 없습니다.':                   'Item ID not found.',
    '아이템을 찾을 수 없습니다.':              'Item not found.',
    '이미지 없음':                            'No image',
    '전면':                                  'Front',
    '후면':                                  'Back',
    '브랜드·기타':                            'Brand/Other',
    '코디뱅크 아이템':                        'CodiBank Item',
    'AI 분석':                               'AI Analysis',
  },

  // pricing.html
  pricing: {
    '코디뱅크 구독 플랜':            'CodiBank Subscription Plans',
    '← 앱으로':                     '← Back to App',
    '현재 플랜':                     'Current Plan',
    '무료':                          'Free',
    '실버':                          'Silver',
    '골드':                          'Gold',
    '다이아':                        'Diamond',
    '추천':                          'Best',
    '선택':                          'Select',
    '코디 생성':                     'Outfit Generation',
    '• 코디 생성':                   '• Outfit Generation',
    '총 6회':                        '6 total',
    '월 40회':                       '40/month',
    '월 150회':                      '150/month',
    '일일 한도':                     'Daily Limit',
    '• 일일 한도: 당일 소진 시 종료': '• Daily Limit: Until depleted',
    '• 일일 한도:':                  '• Daily Limit:',
    '당일 소진 시 종료':              'Until depleted',
    '소진 시 종료':                   'Until depleted',
    '7일간':                         '7 days',
    '30일간':                        '30 days',
    '영구 저장':                     'Permanent',
    '영구':                          'Permanent',
    '저장':                          'storage',
    '• 데이터':                      '• Data',
    '데이터':                        'Data',
    '데이터 보관':                   'Data Retention',
    '기능':                          'Feature',
    '월 요금':                       'Monthly Fee',
    '플랜별 권한 요약':               'Plan Comparison',
    '코디 생성 (AI 통합권)':          'Outfit Gen (AI Combined)',
    '일일 사용 한도':                 'Daily Limit',
    '자유 선택':                     'Any',
    '• API: 자유 선택':              '• API: Any',
    '• API: DIY(Gemini) 위주':       '• API: DIY(Gemini) focused',
    '• API: 추천(OpenAI) 강화':      '• API: Recommended(OpenAI)',
    '• API: 모든 AI 무제한':         '• API: All AI unlimited',
    '추천(OpenAI)':                  'Recommended(OpenAI)',
    '모든 AI':                       'All AI',
    '위주':                          ' focused',
    '강화':                          '',
    'API 상세 비율':                  'API Details',
    '사용량 로딩 중…':               'Loading usage…',
    '플랜이 저장되었습니다.':         ' plan saved.',
    '이번 달':                       'This month',
    '회 사용':                       ' used',
    '오늘':                          'Today',
    '(최초)':                        '(initial)',
    '/월':                           '/mo',
    '3회/일':                        '3/day',
    '10회/일':                       '10/day',
    '30회/일':                       '30/day',
    '일 3회':                        '3/day',
    '일 10회':                       '10/day',
    '일 30회':                       '30/day',
    '무제한(FUP)':                   'Unlimited(FUP)',
    '무제한':                        'Unlimited',
    '무료 (Free)':                   'Free',
    '실버 (Silver)':                 'Silver',
    '골드 (Gold)':                   'Gold',
    '다이아 (Diamond)':              'Diamond',
    '7일':                           '7 days',
    '30일':                          '30 days',
    '로 시작하고, 사용량이 늘어날수록': '. Start free, upgrade as you grow to',
    '실버/골드/다이아':               ' Silver/Gold/Diamond',
    '로 확장합니다.':                 '.',
    '에서 사용하는 AI 코디 생성 횟수가': ' AI outfit generation count is',
    '통합':                          'combined',
    '으로 관리됩니다.':               '.',
    '과':                            ' and',
    '* 코디 생성 횟수는 내옷장 + 코디하기 통합 사용 기준입니다.': '* Outfit count is combined usage from Closet + Style It.',
    '코디 생성 총 6회':              'Outfit Generation: 6 total',
    '코디 생성 총 6회 (최초)':       'Outfit Gen: 6 total (initial)',
    '코디 생성 월 40회':             'Outfit Gen: 40/month',
    '코디 생성 월 150회':            'Outfit Gen: 150/month',
    '코디 생성 무제한(FUP)':         'Outfit Gen: Unlimited(FUP)',
    '당일 소진 시 종료':              'Until depleted',
    '7일간 저장':                    '7 days storage',
    '30일간 저장':                   '30 days storage',
    '플랜':                          ' Plan',
  },

};

/* ─── 2026-07-04 KST · TJ 지시 ─── 일본어/중국어 레이어 (한국어 키 → 현지어) ───
   시드 범위: 공통 UI + 코디핏(목적·날씨·요일·핵심 상태) + 마이페이지 + 앨범.
   여기 없는 키는 자동으로 영어 폴백. 추후 키만 추가하면 즉시 반영. */
var DICT_JA = {
  _common: {
    '내옷장':'マイクローゼット', '코디앨범':'コーデアルバム', 'ITEM등록':'アイテム登録',
    '코디하기':'コーデする', '전체삭제':'すべて削除', '저장':'保存', '공유':'共有',
    '삭제':'削除', '로그인':'ログイン', '회원가입':'会員登録', '로그아웃':'ログアウト',
    '취소':'キャンセル', '확인':'OK', '닫기':'閉じる', '필수':'必須', '선택':'任意',
    '기타':'その他', '비즈니스':'ビジネス', '주말여행':'週末旅行', '코디':'コーデ',
  },
  closet: {
    '내옷장 - 코디뱅크':'マイクローゼット - CodiBank', '내옷장':'マイクローゼット',
    '위치 확인 중…':'位置情報を確認中…', '로딩중':'読み込み中', '오늘':'今日',
    '코디 목적 선택':'コーデ目的を選択', '직접입력':'直接入力',
    '코디 날짜 선택':'コーデ日付を選択', '코디를 생성할 날짜를 선택하세요':'コーデを作成する日付を選んでください',
    '오늘의 코디':'今日のコーデ', '내일의 코디':'明日のコーデ',
    '목적과 날짜를 먼저 선택하세요':'目的と日付を先に選択してください',
    'AI 추천코디 이야기':'AIスタイリングストーリー',
    '스타일 키워드':'スタイルキーワード', '카테고리별 코디 포인트':'カテゴリ別コーデポイント',
    '추천 이미지 생성중':'コーデ画像を生成中', '초기화 중…':'初期化中…',
    '얼굴 사진 불러오는 중…':'顔写真を読み込み中…',
    '출퇴근':'通勤', '캐주얼':'カジュアル', '데이트':'デート', '여행':'旅行',
    '국내여행':'国内旅行', '해외여행':'海外旅行', '운동/레저':'スポーツ/レジャー',
    '결혼식/행사':'結婚式/イベント', '면접':'面接', '주말외출':'週末おでかけ',
    '지인모임':'友人との集まり', '소개팅':'お見合いデート', '파티':'パーティー',
    '파티룩':'パーティールック', '등산':'登山',
    '맑음':'晴れ', '흐림':'くもり', '비':'雨', '눈':'雪', '구름많음':'曇りがち',
    '예보 없음':'予報なし',
    '일':'日', '월':'月', '화':'火', '수':'水', '목':'木', '금':'金', '토':'土',
    '추천 이미지 없음':'コーデ画像なし', '무제한':'無制限', '다시 코디':'再コーデ', '다시코디':'再コーデ',
    '등록':'登録', '모바일 옷장':'モバイルクローゼット',
    '카테고리 추가':'カテゴリ追加', '추가하기':'追加', '추가':'追加',
    '아이템 없음':'アイテムなし', '검색 결과가 없어요':'検索結果がありません', '아이템':'アイテム',
    '코트':'コート', '자켓':'ジャケット', '탑/셔츠/블라우스':'トップス/シャツ',
    '바지/스커트':'パンツ/スカート', '양말':'ソックス', '구두/운동화':'シューズ',
    '시계':'時計', '스카프/목도리':'スカーフ/マフラー',
  },
  mypage: {
    '마이페이지 - 코디뱅크':'マイページ - CodiBank', '마이페이지':'マイページ',
    '사용자':'ユーザー', '계정 관리':'アカウント管理', '프로필 수정':'プロフィール編集',
    '구독 플랜':'サブスクプラン', '서비스':'サービス', '내 옷장 바로가기':'マイクローゼットへ',
    '이용약관':'利用規約', '개인정보처리방침':'プライバシーポリシー', '환불정책':'返金ポリシー',
    '플랜':'プラン', '회원탈퇴':'退会', 'Ai 옷장':'AIクローゼット',
    '회 가능':'回可能', '아이템':'アイテム',
  },
  album: {
    '코디앨범 - 코디뱅크':'コーデアルバム - CodiBank', '앨범 불러오는 중…':'アルバムを読み込み中…',
    '저장된 코디가 없어요':'保存されたコーデがありません',
    'AI 코디 추천 받기':'AIコーデをもらう', '이미지를 불러올 수 없습니다.':'画像を読み込めません。',
    '이 코디를 삭제할까요?':'このコーデを削除しますか？',
  },
};

var DICT_ZH = {
  _common: {
    '내옷장':'我的衣橱', '코디앨범':'穿搭相册', 'ITEM등록':'添加单品',
    '코디하기':'开始穿搭', '전체삭제':'全部删除', '저장':'保存', '공유':'分享',
    '삭제':'删除', '로그인':'登录', '회원가입':'注册', '로그아웃':'退出登录',
    '취소':'取消', '확인':'确认', '닫기':'关闭', '필수':'必填', '선택':'可选',
    '기타':'其他', '비즈니스':'商务', '주말여행':'周末旅行', '코디':'穿搭',
  },
  closet: {
    '내옷장 - 코디뱅크':'我的衣橱 - CodiBank', '내옷장':'我的衣橱',
    '위치 확인 중…':'正在获取位置…', '로딩중':'加载中', '오늘':'今天',
    '코디 목적 선택':'选择穿搭场合', '직접입력':'自定义输入',
    '코디 날짜 선택':'选择穿搭日期', '코디를 생성할 날짜를 선택하세요':'请选择生成穿搭的日期',
    '오늘의 코디':'今日穿搭', '내일의 코디':'明日穿搭',
    '목적과 날짜를 먼저 선택하세요':'请先选择场合和日期',
    'AI 추천코디 이야기':'AI穿搭故事',
    '스타일 키워드':'风格关键词', '카테고리별 코디 포인트':'分类穿搭要点',
    '추천 이미지 생성중':'正在生成穿搭图片', '초기화 중…':'初始化中…',
    '얼굴 사진 불러오는 중…':'正在加载面部照片…',
    '출퇴근':'通勤', '캐주얼':'休闲', '데이트':'约会', '여행':'旅行',
    '국내여행':'国内旅行', '해외여행':'海外旅行', '운동/레저':'运动/休闲',
    '결혼식/행사':'婚礼/活动', '면접':'面试', '주말외출':'周末外出',
    '지인모임':'朋友聚会', '소개팅':'相亲', '파티':'派对',
    '파티룩':'派对造型', '등산':'登山',
    '맑음':'晴', '흐림':'阴', '비':'雨', '눈':'雪', '구름많음':'多云',
    '예보 없음':'暂无预报',
    '일':'日', '월':'一', '화':'二', '수':'三', '목':'四', '금':'五', '토':'六',
    '추천 이미지 없음':'暂无穿搭图片', '무제한':'不限次数', '다시 코디':'重新穿搭', '다시코디':'重新穿搭',
    '등록':'注册', '모바일 옷장':'移动衣橱',
    '카테고리 추가':'添加分类', '추가하기':'添加', '추가':'添加',
    '아이템 없음':'暂无单品', '검색 결과가 없어요':'没有搜索结果', '아이템':'单品',
    '코트':'大衣', '자켓':'夹克', '탑/셔츠/블라우스':'上衣/衬衫',
    '바지/스커트':'裤子/裙子', '양말':'袜子', '구두/운동화':'鞋子',
    '시계':'手表', '스카프/목도리':'围巾',
  },
  mypage: {
    '마이페이지 - 코디뱅크':'我的主页 - CodiBank', '마이페이지':'我的主页',
    '사용자':'用户', '계정 관리':'账号管理', '프로필 수정':'编辑资料',
    '구독 플랜':'订阅方案', '서비스':'服务', '내 옷장 바로가기':'前往我的衣橱',
    '이용약관':'服务条款', '개인정보처리방침':'隐私政策', '환불정책':'退款政策',
    '플랜':'方案', '회원탈퇴':'注销账号', 'Ai 옷장':'AI衣橱',
    '회 가능':'次可用', '아이템':'单品',
  },
  album: {
    '코디앨범 - 코디뱅크':'穿搭相册 - CodiBank', '앨범 불러오는 중…':'正在加载相册…',
    '저장된 코디가 없어요':'暂无保存的穿搭',
    'AI 코디 추천 받기':'获取AI穿搭', '이미지를 불러올 수 없습니다.':'无法加载图片。',
    '이 코디를 삭제할까요?':'要删除这套穿搭吗？',
  },
};

/* ─── 2026-07-04 KST · TJ 지시 ─── 스페인어 레이어 (한국어 키 → 스페인어) ───
   시드 범위: JA/ZH 와 동일 (공통 UI + 코디핏 + 마이페이지 + 앨범).
   여기 없는 키는 자동으로 영어 폴백. */
var DICT_ES = {
  _common: {
    '내옷장':'Mi Armario', '코디앨범':'Álbum de Looks', 'ITEM등록':'Añadir Prenda',
    '코디하기':'Crear Look', '전체삭제':'Eliminar Todo', '저장':'Guardar', '공유':'Compartir',
    '삭제':'Eliminar', '로그인':'Iniciar Sesión', '회원가입':'Registrarse', '로그아웃':'Cerrar Sesión',
    '취소':'Cancelar', '확인':'OK', '닫기':'Cerrar', '필수':'Obligatorio', '선택':'Opcional',
    '기타':'Otros', '비즈니스':'Negocios', '주말여행':'Viaje de Fin de Semana', '코디':'Look',
  },
  closet: {
    '내옷장 - 코디뱅크':'Mi Armario - CodiBank', '내옷장':'Mi Armario',
    '위치 확인 중…':'Comprobando ubicación…', '로딩중':'Cargando', '오늘':'Hoy',
    '코디 목적 선택':'Elige la Ocasión', '직접입력':'Entrada Manual',
    '코디 날짜 선택':'Elige la Fecha', '코디를 생성할 날짜를 선택하세요':'Elige la fecha para crear tu look',
    '오늘의 코디':'Look de Hoy', '내일의 코디':'Look de Mañana',
    '목적과 날짜를 먼저 선택하세요':'Primero elige ocasión y fecha',
    'AI 추천코디 이야기':'Historia de Estilo IA',
    '스타일 키워드':'Palabras Clave de Estilo', '카테고리별 코디 포인트':'Puntos de Look por Categoría',
    '추천 이미지 생성중':'Generando imagen del look', '초기화 중…':'Inicializando…',
    '얼굴 사진 불러오는 중…':'Cargando foto de rostro…',
    '출퇴근':'Trabajo', '캐주얼':'Casual', '데이트':'Cita', '여행':'Viaje',
    '국내여행':'Viaje Nacional', '해외여행':'Viaje al Extranjero', '운동/레저':'Deporte/Ocio',
    '결혼식/행사':'Boda/Evento', '면접':'Entrevista', '주말외출':'Salida de Fin de Semana',
    '지인모임':'Reunión con Amigos', '소개팅':'Cita a Ciegas', '파티':'Fiesta',
    '파티룩':'Look de Fiesta', '등산':'Senderismo',
    '맑음':'Despejado', '흐림':'Nublado', '비':'Lluvia', '눈':'Nieve', '구름많음':'Muy Nublado',
    '예보 없음':'Sin pronóstico',
    '일':'Dom', '월':'Lun', '화':'Mar', '수':'Mié', '목':'Jue', '금':'Vie', '토':'Sáb',
    '추천 이미지 없음':'Sin imagen del look', '무제한':'Ilimitado', '다시 코디':'Reintentar', '다시코디':'Reintentar',
    '등록':'Registrar', '모바일 옷장':'Armario Móvil',
    '카테고리 추가':'Añadir Categoría', '추가하기':'Añadir', '추가':'Añadir',
    '아이템 없음':'Sin prendas', '검색 결과가 없어요':'Sin resultados', '아이템':'Prenda',
    '코트':'Abrigo', '자켓':'Chaqueta', '탑/셔츠/블라우스':'Top/Camisa',
    '바지/스커트':'Pantalón/Falda', '양말':'Calcetines', '구두/운동화':'Zapatos',
    '시계':'Reloj', '스카프/목도리':'Bufanda',
  },
  mypage: {
    '마이페이지 - 코디뱅크':'Mi Página - CodiBank', '마이페이지':'Mi Página',
    '사용자':'Usuario', '계정 관리':'Gestión de Cuenta', '프로필 수정':'Editar Perfil',
    '구독 플랜':'Plan de Suscripción', '서비스':'Servicios', '내 옷장 바로가기':'Ir a Mi Armario',
    '이용약관':'Términos de Servicio', '개인정보처리방침':'Política de Privacidad', '환불정책':'Política de Reembolso',
    '플랜':'Plan', '회원탈퇴':'Eliminar Cuenta', 'Ai 옷장':'Armario IA',
    '회 가능':'usos disponibles', '아이템':'Prendas',
  },
  album: {
    '코디앨범 - 코디뱅크':'Álbum de Looks - CodiBank', '앨범 불러오는 중…':'Cargando álbum…',
    '저장된 코디가 없어요':'No hay looks guardados',
    'AI 코디 추천 받기':'Obtener Look IA', '이미지를 불러올 수 없습니다.':'No se puede cargar la imagen.',
    '이 코디를 삭제할까요?':'¿Eliminar este look?',
  },
};

// ── 현재 페이지 감지 ──
function detectPage() {
  var path = location.pathname.toLowerCase();
  if (path.includes('aicloset'))  return 'aicloset';
  if (path.includes('closet'))    return 'closet';
  if (path.includes('codistyle')) return 'codistyle';
  if (path.includes('camera'))    return 'camera';
  if (path.includes('mypage'))    return 'mypage';
  if (path.includes('profile'))   return 'profile';
  if (path.includes('album'))     return 'album';
  if (path.includes('item'))      return 'item';
  if (path.includes('login'))     return 'login';
  if (path.includes('signup'))    return 'signup';
  if (path.includes('pricing'))   return 'pricing';
  if (path.includes('refund'))    return 'refund';
  if (path.includes('terms'))     return 'terms';
  if (path.includes('privacy'))   return 'privacy';
  if (path === '/' || path.includes('index')) return 'index';
  return '';
}

// ── 병합된 사전 생성 ──
function getMergedDict(lang) {
  // ─── 2026-07-04 KST · TJ 지시 ─── 다국어 병합: ja/zh 는 EN 베이스 + 현지어 오버레이 ───
  lang = lang || getLang();
  var page = detectPage();
  function mergeFrom(SRC, into) {
    if (!SRC) return into;
    var c = SRC._common || {};
    for (var k in c) into[k] = c[k];
    if (page === 'aicloset') {                 // 코디쌤 생성 코드 공유
      var cl = SRC.closet || {};
      for (var k3 in cl) into[k3] = cl[k3];
    }
    var p = SRC[page] || {};
    for (var k2 in p) into[k2] = p[k2];
    return into;
  }
  var merged = mergeFrom(DICT, {});            // 1) 영어 베이스 (전체 커버리지)
  if (lang === 'ja') mergeFrom(typeof DICT_JA !== 'undefined' ? DICT_JA : null, merged);
  if (lang === 'zh') mergeFrom(typeof DICT_ZH !== 'undefined' ? DICT_ZH : null, merged);
  if (lang === 'es') mergeFrom(typeof DICT_ES !== 'undefined' ? DICT_ES : null, merged);  // 2026-07-04 KST · TJ 지시
  return merged;
}

// ── 현재 언어 ──
function getLang() {
  try { return localStorage.getItem(LANG_KEY) || 'ko'; } catch(e) { return 'ko'; }
}
function setLang(lang) {
  if (!LANGS[lang]) lang = 'ko';  // 2026-07-04 KST · TJ 지시 — 미등록 언어 방어
  try { localStorage.setItem(LANG_KEY, lang); } catch(e) {}
}

// ── 텍스트 노드 수집 ──
var _origMap = new WeakMap();
function collectTextNodes(root) {
  var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
  var nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  return nodes;
}

// ── 번역 적용 ──
function applyTranslation() {
  var lang = getLang();
  if (lang === 'ko') {
    // 원본 복원
    collectTextNodes(document.body).forEach(function(node) {
      if (_origMap.has(node)) node.textContent = _origMap.get(node);
    });
    // title 복원
    if (document._origTitle) document.title = document._origTitle;
    return;
  }

  var dict = getMergedDict(lang);  // 2026-07-04 KST · TJ 지시 — 현재 언어 병합
  // 키를 길이 내림차순으로 정렬 (긴 텍스트 우선 매칭)
  var keys = Object.keys(dict).sort(function(a, b) { return b.length - a.length; });

  /* ─── 2026-07-03 KST · TJ 지시 ─── 부분치환 안전 가드 (본문 오염 수정) ────────
     문제: 부분 매칭이 '일'→Sun, '코디'→Outfit 같은 단문 키를 문장 중간에 적용해
           '스타일링'→'스타Sun링', '목적'→'Thu적', '화이트'→'Tue이트' 등 본문 파괴.
           오염된 텍스트는 exact 사전 키와도 불일치해 정상 번역까지 차단됨.
     해결: ① 3글자 미만 키는 부분치환 금지 (exact 전용 — 버튼/라벨 단독 노출은 유지)
           ② 한글 경계 가드 — 키 앞뒤가 한글이면 단어 중간이므로 치환 금지
           ③ exact 우선은 기존 유지. 치환 횟수(1회)·정렬 등 기존 동작 보존. */
  function _isHangul(ch){ return ch >= '\uAC00' && ch <= '\uD7A3'; }
  function safePartialReplace(text, key, val){
    if (key.length < 3) return text;                       // ① 단문 키 배제
    var idx = text.indexOf(key);
    while (idx !== -1) {
      var pre  = idx > 0 ? text.charAt(idx - 1) : '';
      var post = (idx + key.length < text.length) ? text.charAt(idx + key.length) : '';
      var okPre  = !_isHangul(key.charAt(0)) || !_isHangul(pre);              // ② 경계 가드
      var okPost = !_isHangul(key.charAt(key.length - 1)) || !_isHangul(post);
      if (okPre && okPost) {
        return text.slice(0, idx) + val + text.slice(idx + key.length);      // 기존과 동일: 1회 치환
      }
      idx = text.indexOf(key, idx + 1);
    }
    return text;
  }

  collectTextNodes(document.body).forEach(function(node) {
    if (!_origMap.has(node)) _origMap.set(node, node.textContent);
    var orig = _origMap.get(node);
    var text = orig;
    var trimmed = text.trim();

    // 정확히 일치
    if (dict[trimmed] !== undefined) {
      node.textContent = text.replace(trimmed, dict[trimmed]);
      return;
    }
    // 부분 매칭 (안전 가드 적용)
    for (var i = 0; i < keys.length; i++) {
      if (text.indexOf(keys[i]) !== -1) {
        text = safePartialReplace(text, keys[i], dict[keys[i]]);
      }
    }
    if (text !== orig) node.textContent = text;
  });

  // title 번역 — exact 우선 + 안전 가드 (원본 기준: ja↔zh 등 직접 전환 대응)
  if (!document._origTitle) document._origTitle = document.title;
  var tt = document._origTitle;
  if (dict[tt.trim()] !== undefined) {
    tt = dict[tt.trim()];
  } else {
    for (var j = 0; j < keys.length; j++) {
      if (tt.indexOf(keys[j]) !== -1) tt = safePartialReplace(tt, keys[j], dict[keys[j]]);
    }
  }
  document.title = tt;

  // placeholder 번역 — exact 우선 + 안전 가드
  document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(function(el) {
    if (!el._origPh) el._origPh = el.placeholder;
    var ph = el._origPh;
    if (dict[ph.trim()] !== undefined) {
      ph = dict[ph.trim()];
    } else {
      for (var i = 0; i < keys.length; i++) {
        if (ph.indexOf(keys[i]) !== -1) ph = safePartialReplace(ph, keys[i], dict[keys[i]]);
      }
    }
    el.placeholder = ph;
  });
}

// ── 언어 토글 버튼 삽입 (랜딩페이지 + 마이페이지에서만) ──
function insertLangToggle() {
  if (document.getElementById('cb-lang-toggle')) return;
  var page = detectPage();
  if (page !== 'index' && page !== 'mypage') return;

  /* ─── 2026-07-04 KST · TJ 지시 ─── 4언어 필 토글 (LANGS 레지스트리 구동) ───
     KO · EN · JA · ZH — 언어 추가 시 LANGS 에 항목만 넣으면 자동 확장. */
  var lang = getLang();
  var div = document.createElement('div');
  div.id = 'cb-lang-toggle';
  div.style.cssText = 'position:fixed;top:10px;right:10px;z-index:999999;display:flex;border-radius:9999px;overflow:hidden;background:rgba(7,19,42,.65);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(76,219,206,.2);font-family:Inter,Noto Sans KR,sans-serif;font-size:11px;font-weight:700;';

  var btns = {};
  function updateBtns(active) {
    Object.keys(btns).forEach(function(l) {
      var b = btns[l];
      if (l === active) {
        b.style.background = 'linear-gradient(135deg,#4cdbce,#13bbaf)';
        b.style.color = '#003733';
        b.style.borderRadius = '9999px';
      } else {
        b.style.background = 'none';
        b.style.color = 'rgba(216,226,255,.5)';
        b.style.borderRadius = '0';
      }
    });
  }

  Object.keys(LANGS).forEach(function(l) {
    var b = document.createElement('button');
    b.textContent = LANGS[l].short;
    b.id = 'cb-lang-' + l;
    b.setAttribute('aria-label', LANGS[l].label);
    b.title = LANGS[l].label;
    b.style.cssText = 'padding:5px 11px;cursor:pointer;transition:all .2s;border:none;font-family:inherit;font-size:inherit;font-weight:inherit;letter-spacing:.03em;background:none;color:rgba(216,226,255,.5);';
    b.onclick = function() { setLang(l); updateBtns(l); applyTranslation(); };
    btns[l] = b;
    div.appendChild(b);
  });

  document.body.appendChild(div);
  updateBtns(lang);
}

// ── 공개 API ──
window.CodiBankI18n = {
  getLang: getLang,
  setLang: function(lang) { setLang(lang); applyTranslation(); },
  apply: applyTranslation,
  // t(ko, en): 기존 호출부 하위호환 — ja/zh 는 사전 조회 후 en 폴백
  t: function(ko, en) {
    var l = getLang();
    if (l === 'ko') return ko;
    if (l === 'en') return (en || ko);
    try { var d = getMergedDict(l); if (d[ko] !== undefined) return d[ko]; } catch(e) {}
    return (en || ko);
  },
  isEn: function() { return getLang() === 'en'; },
  // ─── 2026-07-04 KST · TJ 지시 ─── 다국어 확장 API ───
  isForeign: function() { return getLang() !== 'ko'; },
  getLangs: function() { return LANGS; },
  langLabel: function(l) { return (LANGS[l || getLang()] || {}).label || ''; },
};

// ── 자동 초기화 ──
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    insertLangToggle();
    if (getLang() !== 'ko') applyTranslation();
  });
} else {
  insertLangToggle();
  if (getLang() !== 'ko') applyTranslation();
}

// MutationObserver: 동적 콘텐츠에도 번역 적용
var _applyTimer = null;
var observer = new MutationObserver(function() {
  if (getLang() === 'ko') return;
  clearTimeout(_applyTimer);
  _applyTimer = setTimeout(applyTranslation, 200);
});
if (document.body) {
  observer.observe(document.body, { childList: true, subtree: true });
} else {
  document.addEventListener('DOMContentLoaded', function() {
    observer.observe(document.body, { childList: true, subtree: true });
  });
}

})();
