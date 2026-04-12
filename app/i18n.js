/* ══════════════════════════════════════════
   CodiBank i18n (한국어 기본 / English 선택)
   - localStorage('codibank_lang')에 'ko' 또는 'en' 저장
   - 각 페이지에서 <script src="i18n.js"></script> 추가
   - DOMContentLoaded 시 자동 적용
══════════════════════════════════════════ */
(function(){
'use strict';

var LANG_KEY = 'codibank_lang';

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
    '저장하기':                               'Save',
    '✅ 프로필이 저장되었습니다.':               '✅ Profile saved.',
    '저장에 실패했습니다. 다시 시도해주세요.':   'Save failed. Please try again.',
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

// ── 현재 페이지 감지 ──
function detectPage() {
  var path = location.pathname.toLowerCase();
  if (path.includes('closet'))    return 'closet';
  if (path.includes('codistyle')) return 'codistyle';
  if (path.includes('camera'))    return 'camera';
  if (path.includes('mypage'))    return 'mypage';
  if (path.includes('profile'))   return 'profile';
  if (path.includes('album'))     return 'album';
  if (path.includes('item'))      return 'closet';
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
function getMergedDict() {
  var page = detectPage();
  var merged = {};
  // 공통
  var c = DICT._common || {};
  for (var k in c) merged[k] = c[k];
  // 페이지별
  var p = DICT[page] || {};
  for (var k2 in p) merged[k2] = p[k2];
  return merged;
}

// ── 현재 언어 ──
function getLang() {
  try { return localStorage.getItem(LANG_KEY) || 'ko'; } catch(e) { return 'ko'; }
}
function setLang(lang) {
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

  var dict = getMergedDict();
  // 키를 길이 내림차순으로 정렬 (긴 텍스트 우선 매칭)
  var keys = Object.keys(dict).sort(function(a, b) { return b.length - a.length; });

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
    // 부분 매칭
    for (var i = 0; i < keys.length; i++) {
      if (text.indexOf(keys[i]) !== -1) {
        text = text.replace(keys[i], dict[keys[i]]);
      }
    }
    if (text !== orig) node.textContent = text;
  });

  // title 번역
  if (!document._origTitle) document._origTitle = document.title;
  var tt = document.title;
  for (var j = 0; j < keys.length; j++) {
    if (tt.indexOf(keys[j]) !== -1) tt = tt.replace(keys[j], dict[keys[j]]);
  }
  document.title = tt;

  // placeholder 번역
  document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(function(el) {
    if (!el._origPh) el._origPh = el.placeholder;
    var ph = el._origPh;
    for (var i = 0; i < keys.length; i++) {
      if (ph.indexOf(keys[i]) !== -1) ph = ph.replace(keys[i], dict[keys[i]]);
    }
    el.placeholder = ph;
  });
}

// ── 언어 토글 버튼 삽입 (랜딩페이지 + 마이페이지에서만) ──
function insertLangToggle() {
  if (document.getElementById('cb-lang-toggle')) return;
  var page = detectPage();
  if (page !== 'index' && page !== 'mypage') return;

  var lang = getLang();
  var div = document.createElement('div');
  div.id = 'cb-lang-toggle';
  div.style.cssText = 'position:fixed;top:10px;right:10px;z-index:999999;display:flex;border-radius:9999px;overflow:hidden;background:rgba(7,19,42,.65);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(76,219,206,.2);font-family:Inter,Noto Sans KR,sans-serif;font-size:11px;font-weight:700;';

  var koBtn = document.createElement('button');
  koBtn.textContent = '한국어';
  koBtn.id = 'cb-lang-ko';
  koBtn.style.cssText = 'padding:5px 12px;cursor:pointer;transition:all .2s;border:none;font-family:inherit;font-size:inherit;font-weight:inherit;letter-spacing:.03em;background:none;color:rgba(216,226,255,.5);';

  var enBtn = document.createElement('button');
  enBtn.textContent = 'EN';
  enBtn.id = 'cb-lang-en';
  enBtn.style.cssText = koBtn.style.cssText;

  function updateBtns(l) {
    if (l === 'ko') {
      koBtn.style.background = 'linear-gradient(135deg,#4cdbce,#13bbaf)';
      koBtn.style.color = '#003733';
      koBtn.style.borderRadius = '9999px';
      enBtn.style.background = 'none';
      enBtn.style.color = 'rgba(216,226,255,.5)';
      enBtn.style.borderRadius = '0';
    } else {
      enBtn.style.background = 'linear-gradient(135deg,#4cdbce,#13bbaf)';
      enBtn.style.color = '#003733';
      enBtn.style.borderRadius = '9999px';
      koBtn.style.background = 'none';
      koBtn.style.color = 'rgba(216,226,255,.5)';
      koBtn.style.borderRadius = '0';
    }
  }

  koBtn.onclick = function() { setLang('ko'); updateBtns('ko'); applyTranslation(); };
  enBtn.onclick = function() { setLang('en'); updateBtns('en'); applyTranslation(); };

  div.appendChild(koBtn);
  div.appendChild(enBtn);
  document.body.appendChild(div);
  updateBtns(lang);
}

// ── 공개 API ──
window.CodiBankI18n = {
  getLang: getLang,
  setLang: function(lang) { setLang(lang); applyTranslation(); },
  apply: applyTranslation,
  t: function(ko, en) { return getLang() === 'en' ? (en || ko) : ko; },
  isEn: function() { return getLang() === 'en'; },
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
