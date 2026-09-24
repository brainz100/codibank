/* ═══════════════════════════════════════════════════════════════════════
   📋 수정 이력 (MODIFICATION HISTORY) — 최신순
   ═══════════════════════════════════════════════════════════════════════
   이 블록은 파일 수정 때마다 최상단에 누적됩니다.
   각 항목은 실제 수정 지점(줄번호)에도 동일한 날짜/요약 주석이 존재합니다.
   점검 시 이 블록만 읽어도 파일의 최신 상태와 변경 이력을 알 수 있습니다.

   ─── 2026-09-24 KST (🔐 서비스 이용 동의 · 회원탈퇴 — TJ 지시) ─────────────
     [동의] 파일 끝 _cbConsentModule → window.CodiBankConsent
       · 필수 5종(만14세·약관·개인정보·신체데이터·국외이전) + 선택 1종(서비스 개선)
       · 신체데이터 동의 전문은 체크박스 아래 항상 펼쳐서 표시
       · signup.html STEP1 에서 build() 사용 / 기록: user_metadata.consent + /api/consent/log
       · 기존 회원: _cbAutoValidateSession 이 서버 검증 후 ensure() → 현재 버전(2026-09-24)
         동의가 없으면 동의 시트 (필수 미동의 시 로그아웃·탈퇴만 가능)
       · _sbUserToCb 에 consent 필드 추가
     [탈퇴] deleteUserAccount: 서버 /api/user/withdraw(토큰 검증) 성공 후에만 로컬 정리
       (이전: 없는 /api/user/delete 를 토큰 없이 호출 → 서버 계정이 남음)

   ─── 2026-09-22 KST (👕 카테고리 체계 개편 v2 — TJ 지시) ─────────────────
     [새 체계 11종 · TJ 지정 순서]
       겉옷(outer) · 상의(top) · 바지(pants) · 스커트(skirt)F · 원피스(onepiece)F
       · 신발 · 가방 · 양말/타이즈(socks) · 시계 · 스카프/머플러(scarf) · 패션소품(etc)
       F = 여성 전용 표시. 남성 로그인은 스커트·원피스 제외(엄격). 성별 미설정 = 전체.
     [기존 데이터 자동 변환 — migrateItemCategoryV2 / migrateAllItemsCategoryV2]
       · coat·jacket → outer  (단, 가디건/카디건·니트/정장 베스트 → top)
       · scarf 중 넥타이/보타이 → etc(패션소품)
       · pants 중 점프수트/오버올 → onepiece, 치마바지 → skirt
       · 판단 근거: meta.gemini.sub_category / outer_type / note
       · 내용 기반 재분류는 아이템당 1회(meta.catSchema=2) — 이후 사용자가 직접 바꾼 값은 존중
       · 원래 키는 meta.legacyCategoryKey 에 보존(롤백·추적용). 아이템 유실 0.
       · ⚠️ migrateUserItemsCategories 의 '허용 안 된 키 → 기타' 폴백보다 반드시 먼저 실행
            (순서가 바뀌면 모든 코트/자켓이 '기타'로 버려짐)
     [레거시 키 호환 — LEGACY_CATEGORY_ALIAS]
       · getItemsByUserAndCategory / getCategoryMetaByKey / addItem / updateItem 에서
         coat·jacket 이 들어와도 outer 로 해석 (옛 캐시 페이지 대비)
     [신규 export] normalizeGender, getCategoryKeysForGender, legacyCategoryToV2,
                   migrateAllItemsCategoryV2, LEGACY_CATEGORY_ALIAS
     [검증] jsdom 시뮬레이션 50/50 — 17종 레거시 아이템 변환·성별 목록·멱등성·사용자 수정 존중

   ─── 2026-04-23 13:00 KST (🧦 양말 위치 이동) ────────────────────────
     [TJ님 지시]
       양말(socks) 카테고리를 신발(shoes) 바로 다음으로 이동.
       이전: shoes → watch → scarf → socks → etc
       이후: shoes → socks → watch → scarf → etc
     ensureUserCategories()가 DEFAULT_CATEGORIES 순서를 강제하므로
     기존 사용자도 즉시 새 순서가 반영됨.

   ─── 2026-04-23 05:45 KST (🔁 카테고리 순서/라벨 조정) ────────────────
     [TJ님 지시]
       ① coat 라벨: "코트" → "아우터" (긴 아우터류 통합 명칭)
          - 포함: 아우터/코트/패딩/버버리/롱패딩
       ② jacket 그대로 유지 (짧은 아우터)
          - 포함: 자켓/블레이저/점퍼/다운자켓/레더자켓/데님자켓/가디건 등
       ③ 원피스 위치: 맨 위 → 상의(top)와 바지(pants) 사이로 이동
          - aicloset.html 카테고리 그리드에서도 같은 순서 반영 필요

     [최종 순서 — 11종]
       아우터(coat) → 자켓(jacket) → 상의(top) → 원피스(onepiece)
       → 바지(pants) → 치마(skirt) → 신발 → 시계 → 스카프 → 양말 → 기타

     [변경 위치]
       ▸ DEFAULT_CATEGORIES 배열 (~line 291)
       ▸ key는 모두 유지 → 기존 사용자 데이터 0 영향

   ─── 2026-04-23 03:00 KST (📦 카테고리 개편 — 원피스/치마 독립 + 아이콘) ──
     [TJ님 지시]
       ① 원피스 카테고리 독립 추가 (기존엔 'bottom'의 pants에 섞임)
       ② 치마 카테고리 독립 추가 (기존 pants label에 '스커트' 포함돼 있던 것 분리)
       ③ 각 카테고리에 이모지 아이콘 추가
       ④ 순서: 원피스 맨 위(트라이온 전용 강조) → 나머지 기존 순서

     [변경 내역]
       ▸ DEFAULT_CATEGORIES 재작성 (~line 283)
         - 기존 9종 → 신규 11종 (onepiece, skirt 추가)
         - 모든 항목에 icon 필드 신규 추가 (이모지)
         - pants label: "바지/스커트" → "바지" (스커트는 skirt로 독립)
         - top label: "탑/셔츠/블라우스" → "상의" (단순화, 영문 i18n 호환)
         - coat label: "코트" 유지, jacket label: "자켓" 유지
         - shoes label: "구두/운동화" → "신발" (단순화)
         - scarf label: "스카프/목도리" → "스카프" (단순화)
         - 최종 순서: onepiece, coat, jacket, top, pants, skirt, shoes,
                      watch, scarf, socks, etc

     [기존 사용자 하위호환 — 자동 마이그레이션]
       ▸ ensureUserCategories() (line ~445)가 이미 구현되어 있음
         - `next = [...defaultKeys, ...user.categories.filter(k => !defaultKeys.includes(k))]`
         - DEFAULT_CATEGORIES에 onepiece/skirt 추가 → 모든 사용자 다음 접속 시
           자동으로 두 카테고리가 상단에 추가됨
         - 사용자가 추가한 커스텀 카테고리는 그대로 보존됨

       ▸ migrateUserItemsCategories() (line ~427)가 허용 키셋 기반으로
         동작하므로, 신규 키(onepiece, skirt)가 자동으로 허용됨
         - 기존에 'pants'로 잘못 분류된 원피스/치마는 자동 이동되지 않음
           (사용자가 수동으로 item.html에서 카테고리 변경 필요)

   ─── 2026-04-20 01:19 KST ────────────────────────────────────────────────
     [수정 이력 블록 도입 — 코드 변경 없음]
       - 파일 관리 정책: 모든 수정 시 상단 이력 누적 + 인라인 주석

   ─── 2026-04-19 (이전 배포본 반영) ─────────────────────────────────────
     [getUserFaceImageSrc 함수 복원 FACE]
       - IIFE 내부에 async function getUserFaceImageSrc(user) 구현
       - avatarFace(IDB 원본) 우선, photo(썸네일) 폴백
       - window.CodiBank exports 목록에 등록
   ═══════════════════════════════════════════════════════════════════════
*/
/*
  CodiBank Prototype Core
  - LocalStorage 기반 (서버/DB 없이) 임시 테스트가 가능한 수준의 동작을 제공
  - 로그인/회원가입/세션
  - 카테고리/아이템 저장
  - 구독 플랜(카테고리별 업로드 제한) 체크

  v3 패치
  - 이미지 저장 안정화: localStorage 용량 제한을 피하기 위해 IndexedDB(이미지 저장) 지원
  - 위치/날씨 정확도 개선: GPS(가능 시) + IP fallback(BigDataCloud) + Open-Meteo
  - 프로필 업데이트 API 추가
*/

(function () {
  'use strict';

  // ==============================
  // Runtime config (optional)
  // - You can override by creating app/config.js (see config.example.js)
  // - IMPORTANT: Do NOT embed real API keys in client-side code for production.
  // ==============================
  function getConfig() {
    const cfg = (typeof window !== 'undefined' && window.CODIBANK_CONFIG) ? window.CODIBANK_CONFIG : {};
    return {
      // Backend (proxy) base URL, e.g. "http://192.168.0.12:8787".
      // If empty, calls are made to the current origin.
      backendBase: String(cfg.backendBase || cfg.BACKEND_BASE || '').trim(),

      // Weather provider: "KMA" (data.go.kr) recommended for commercial, "OPEN_METEO_DEV" for prototype only.
      weatherProvider: String(cfg.weatherProvider || cfg.WEATHER_PROVIDER || 'OPEN_METEO_DEV').trim(),
      allowOpenMeteoDev: cfg.allowOpenMeteoDev !== undefined ? !!cfg.allowOpenMeteoDev : (cfg.ALLOW_OPEN_METEO_DEV_ONLY !== undefined ? !!cfg.ALLOW_OPEN_METEO_DEV_ONLY : true),

      // KMA (data.go.kr) service key (DEV ONLY; for production use backend proxy)
      kmaServiceKey: String(cfg.kmaServiceKey || cfg.KMA_SERVICE_KEY || '').trim(),

      // AI styling provider: "REMOTE" (backend) or "LOCAL" (browser canvas).
      aiProvider: String(cfg.aiProvider || cfg.AI_PROVIDER || 'LOCAL').trim(),

      // Optional: separate AI base (defaults to backendBase)
      aiBase: String(cfg.aiBase || cfg.AI_BASE || '').trim(),

      // Optional: separate storage/assets base for uploaded images
      storageBase: String(cfg.storageBase || cfg.STORAGE_BASE || '').trim(),
    };
  }

  function resolveBaseUrl(base, path) {
    const b = String(base || '').trim();
    if (!b) return path;
    const p = String(path || '').trim();
    if (!p) return b;
    return b.replace(/\/$/, '') + '/' + p.replace(/^\//, '');
  }

// ==============================
// Backend base helper
// - Many prototype features call the local proxy server (port 8787).
// - If backendBase is not set in config.js, we derive it from current hostname.
//   (This is important for mobile testing over Wi‑Fi.)
// ==============================

function _uniqueStrings(arr) {
  return Array.from(new Set((arr || []).map(v => String(v || '').trim()).filter(Boolean)));
}

function getStorageBasesResolved() {
  const cfg = getConfig();
  const out = [];
  const push = (v) => { if (v) out.push(String(v).trim().replace(/\/$/, '')); };
  try {
    push(cfg.storageBase);
    push(cfg.backendBase);
    push(cfg.aiBase);
    const loc = (typeof window !== 'undefined' && window.location) ? window.location : null;
    const host = loc && loc.hostname ? String(loc.hostname).trim() : '';
    const origin = loc && loc.origin ? String(loc.origin).trim() : '';
    if (origin && !/localhost|127\.0\.0\.1/.test(host)) push(origin);
    // 운영 도메인 기본 폴백: 이미지는 주로 메인 백엔드(codibank.onrender.com)에 있고,
    // 일부는 분리 API(codibank-api.onrender.com)에 저장될 수 있어 둘 다 시도합니다.
    if (/codibank\.kr$/i.test(host)) {
      push('https://codibank.onrender.com');
      push('https://codibank-api.onrender.com');
    }
  } catch (_) {}
  return _uniqueStrings(out);
}

function _probeImageUrl(url, timeoutMs) {
  return new Promise((resolve) => {
    try {
      const img = new Image();
      let done = false;
      const t = setTimeout(() => {
        if (done) return;
        done = true;
        try { img.src = ''; } catch (_) {}
        resolve(false);
      }, Number(timeoutMs || 6000));
      img.onload = () => {
        if (done) return;
        done = true;
        clearTimeout(t);
        resolve(true);
      };
      img.onerror = () => {
        if (done) return;
        done = true;
        clearTimeout(t);
        resolve(false);
      };
      img.src = url;
    } catch (_) { resolve(false); }
  });
}

function getBackendBaseResolved() {
  const cfg = getConfig();
  const raw = String(cfg.backendBase || '').trim();

  try {
    const locHost = (typeof window !== 'undefined' && window.location && window.location.hostname)
      ? String(window.location.hostname).trim()
      : '';

    if (raw) {
      let b = raw.replace(/\/$/, '');

      // ✅ 초보자 실수 방지:
      // - config.js에 127.0.0.1/localhost를 넣어두면,
      //   모바일(같은 Wi‑Fi)에서는 "휴대폰 자신"을 가리키게 되어 업로드/AI 호출이 실패합니다.
      // - 현재 접속 호스트가 LAN IP라면, localhost/127.0.0.1을 자동으로 교정합니다.
      if (locHost && locHost !== '127.0.0.1' && locHost !== 'localhost') {
        if (b.includes('127.0.0.1') || b.includes('localhost')) {
          try {
            const u = new URL(b);
            u.hostname = locHost;
            b = u.toString().replace(/\/$/, '');
          } catch (_) {
            b = b.replace('127.0.0.1', locHost).replace('localhost', locHost);
          }
        }
      }

      return b;
    }

    if (locHost) return `http://${locHost}:8787`;
  } catch (_) {
    // ignore
  }

  return raw ? raw.replace(/\/$/, '') : '';
}


  const KEYS = {
    USERS:   'codibank_users',    // 로컬 캐시용 (Supabase 세션에서 채워짐)
    SESSION: 'codibank_session',  // 로컬 세션 캐시
    ITEMS:   'codibank_items',    // 아이템 데이터 (로컬 유지)
    PLAN:    'codibank_plan',     // pricing.html 호환
  };

  // ══════════════════════════════════════════════════════
  // Supabase 클라이언트 초기화
  // config.js → window.CODIBANK_CONFIG.supabaseUrl / supabaseAnonKey
  // ══════════════════════════════════════════════════════
  const _SB_URL  = (typeof window !== 'undefined' && window.CODIBANK_CONFIG && window.CODIBANK_CONFIG.supabaseUrl)
    ? window.CODIBANK_CONFIG.supabaseUrl
    : 'https://drgsayvlpzcacurcczjq.supabase.co';

  const _SB_ANON = (typeof window !== 'undefined' && window.CODIBANK_CONFIG && window.CODIBANK_CONFIG.supabaseAnonKey)
    ? window.CODIBANK_CONFIG.supabaseAnonKey
    : '';

  let _sbClient = null;
  function _getSupabase() {
    if (_sbClient) return _sbClient;
    if (!_SB_ANON) {
      console.warn('[CodiBank] supabaseAnonKey 미설정 — config.js에서 설정하세요.');
      return null;
    }
    try {
      // Supabase JS SDK v2 (UMD: window.supabase.createClient)
      const factory = (typeof window !== 'undefined' && window.supabase && window.supabase.createClient)
        ? window.supabase.createClient
        : (typeof supabase !== 'undefined' && supabase.createClient ? supabase.createClient : null);
      if (!factory) { console.warn('[CodiBank] Supabase SDK 미로드'); return null; }
      _sbClient = factory(_SB_URL, _SB_ANON, {
        auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
      });
      return _sbClient;
    } catch (e) {
      console.warn('[CodiBank] Supabase 초기화 실패:', e);
      return null;
    }
  }

  // 현재 Supabase 세션 캐시 (동기 접근용)
  let _cachedSession  = null;
  let _cachedUser     = null;    // Supabase user → CodiBank user 형태로 변환한 캐시
  let _sessionFetched = false;

  // Supabase user → CodiBank user 형태로 변환
  function _sbUserToCb(sbUser) {
    if (!sbUser) return null;
    const m = sbUser.user_metadata || {};

    // ─── 2026-05-25 KST 패치: 관리자/테스트 계정 자동 DIAMOND plan 처리 ───
    //   대상:
    //     · admin@codibank.kr   (총괄 관리자)
    //     · prowizard@naver.com (테스트 계정)
    //   효과: 두 계정은 모든 페이지에서 user.plan='DIAMOND' 로 처리됨.
    //         코디핏(∞), 트라이온(100/월), 아이템(∞), 런웨이(50/월) 모두
    //         DIAMOND tier 한도로 적용. pricing.html '현재 플랜'도 다이아 표시.
    //   백엔드 _RUNWAY_ADMIN_EMAILS / _RUNWAY_TEST_EMAILS 와 일치.
    const _email = (sbUser.email || '').toLowerCase().trim();
    const _ADMIN_PLAN_EMAILS = ['admin@codibank.kr', 'prowizard@naver.com'];
    const _forceAdminPlan = _ADMIN_PLAN_EMAILS.indexOf(_email) >= 0;
    const _resolvedPlan = _forceAdminPlan ? 'DIAMOND' : (m.plan || 'FREE');

    return {
      email:            sbUser.email || '',
      gender:           m.gender     || '',
      ageGroup:         m.ageGroup   || '',
      height:           m.height     || '',
      weight:           m.weight     || '',
      location:         m.location   || '',
      nickname:         m.nickname   || m.name || '',
      avatarFace:       m.avatarFace || '',
      plan:             _resolvedPlan,
      categories:       m.categories || DEFAULT_CATEGORIES.map((c) => c.key),
      customCategories: m.customCategories || [],
      createdAt:        sbUser.created_at  || nowIso(),
      updatedAt:        m.updatedAt  || nowIso(),
      sbId:             sbUser.id,
      consent:          m.consent    || null,   // 2026-09-24 KST · TJ 지시 — 서비스 이용 동의 기록 {v, at, items}
    };
  }

  // ✅ 기본 카테고리 (옷장 페이지 기준 고정 순서)
  // ─── 2026-04-23 05:45 KST [TJ 지시 — 카테고리 순서 조정 + 라벨 변경] ──
  //   ▸ coat 라벨: "코트" → "아우터" (무릎 이상 긴 아우터류 통합 명칭)
  //     포함 아이템: 아우터/코트/패딩/버버리/롱패딩
  //   ▸ jacket 그대로 유지 (짧은 아우터)
  //     포함 아이템: 자켓/블레이저/점퍼/다운자켓/레더자켓/데님자켓/가디건 등
  //   ▸ 원피스 위치 이동: 맨 위 → 상의(top)와 바지(pants) 사이
  //     최종 순서: 아우터 → 자켓 → 상의 → 원피스 → 바지 → 치마 → ...
  //     (트라이온 강조 맨 위 배치는 직관적 옷장 UX와 충돌 — 의류는 겉→안, 상→하 순이 자연스러움)
  // ─── 2026-04-23 03:00 KST [TJ 지시 — 카테고리 개편 (onepiece/skirt 신규)] ──
  //   ▸ 원피스(onepiece) 독립 추가
  //   ▸ 치마(skirt) 독립 추가 — 기존 pants label에서 "스커트" 제거
  //   ▸ 각 항목에 이모지 아이콘(icon) 필드 추가
  //   ▸ 기존 사용자는 ensureUserCategories()가 자동으로 신규 키 병합
  // ────────────────────────────────────────────────────────────────────
  // ─── 2026-09-22 KST · TJ 지시 — 카테고리 체계 개편 (schema v2) ─────────────
  //   ① 겉옷(outer) 신설: 기존 아우터(coat) + 자켓(jacket) 통합
  //      포함: 재킷·블레이저·코트·점퍼·패딩·바람막이·레인웨어·겉옷용 베스트(패딩/다운/퀼팅)
  //   ② 상의(top): 티셔츠·셔츠·블라우스·니트티·카디건·맨투맨·후드티·민소매·베스트(니트/정장)
  //      ※ 카디건은 이제 상의 (이전 규칙 '가디건=자켓' 폐기)
  //   ③ 바지(pants): 슬랙스·청바지·면바지·쇼츠·조거·레깅스
  //   ④ 스커트(skirt): 스커트·치마바지            ← 여성 전용 표시
  //   ⑤ 원피스(onepiece): 원피스·드레스·점프수트·오버올 ← 여성 전용 표시
  //   ⑥ 신발 / ⑦ 가방 / ⑧ 양말/타이즈 / ⑨ 시계 / ⑩ 스카프/머플러
  //   ⑪ 패션소품(etc 키 유지): 모자·벨트·넥타이·장갑·액세서리  ← 넥타이는 스카프에서 이동
  //   순서 = TJ 지정 순서. gender:'F' 항목은 남성 로그인 시 목록에서 제외(엄격 적용).
  //   기존 데이터는 아래 migrateItemCategoryV2() 가 1회 자동 변환 (유실 0, 원래 키 보존).
  const DEFAULT_CATEGORIES = [
    { key: 'outer',    label: '겉옷',          icon: '🧥' },
    { key: 'top',      label: '상의',          icon: '👕' },
    { key: 'pants',    label: '바지',          icon: '👖' },
    { key: 'skirt',    label: '스커트',        icon: '🎀', gender: 'F' },
    { key: 'onepiece', label: '원피스',        icon: '👗', gender: 'F' },
    { key: 'shoes',    label: '신발',          icon: '👟' },
    { key: 'bag',      label: '가방',          icon: '👜' },
    { key: 'socks',    label: '양말/타이즈',   icon: '🧦' },
    { key: 'watch',    label: '시계',          icon: '⌚' },
    { key: 'scarf',    label: '스카프/머플러', icon: '🧣' },
    { key: 'etc',      label: '패션소품',      icon: '🧢' },
  ];

  // 레거시 키(이전 체계) → 새 키. 조회·표시·입력 어디서 들어와도 새 키로 해석.
  //   (옛 캐시 페이지가 'coat' 로 저장을 시도해도 '기타'로 떨어지지 않게 하는 안전망)
  const LEGACY_CATEGORY_ALIAS = { coat: 'outer', jacket: 'outer' };
  const CATEGORY_SCHEMA_VERSION = 2;

  // 성별 값 정규화: 'M'/'F'/'male'/'female'/'남성'/'여성' 등 → 'M' | 'F' | ''
  function normalizeGender(g) {
    const v = String(g || '').trim().toLowerCase();
    if (['m', 'male', 'man', 'men', '남', '남성', '남자'].indexOf(v) >= 0) return 'M';
    if (['f', 'female', 'woman', 'women', '여', '여성', '여자'].indexOf(v) >= 0) return 'F';
    return '';
  }

  // 아이템 내용(AI 분석 세부품목·설명)으로 레거시 키의 새 카테고리를 결정
  function _catText(it) {
    const g = (it && it.meta && it.meta.gemini) || {};
    return [g.sub_category, g.outer_type, it && it.note].filter(Boolean).join(' ');
  }
  function legacyCategoryToV2(key, it) {
    const k = String(key || '');
    if (k === 'coat' || k === 'jacket') {
      const t = _catText(it);
      if (/가디건|카디건|cardigan/i.test(t)) return 'top';
      if (/(니트|스웨터|정장|수트)\s*(베스트|조끼)|knit\s*vest/i.test(t)) return 'top';
      return 'outer';
    }
    return LEGACY_CATEGORY_ALIAS[k] || k;
  }

  // 아이템 1개를 schema v2 로 변환 (내용 기반 재분류는 아이템당 딱 1회)
  //   반환: true = 변경됨
  function migrateItemCategoryV2(it) {
    if (!it || typeof it !== 'object') return false;
    const before = String(it.categoryKey || '');
    if (!it.meta || typeof it.meta !== 'object') it.meta = {};
    const done = Number(it.meta.catSchema || 0) >= CATEGORY_SCHEMA_VERSION;
    let next = before;
    if (!done) {
      const t = _catText(it);
      next = legacyCategoryToV2(before, it);
      // 이번 개편으로 소속이 바뀐 품목 (최초 1회만 — 이후 사용자가 직접 바꾼 값은 존중)
      if (next === 'scarf' && /넥타이|보타이|necktie|bow\s*tie/i.test(t)) next = 'etc';
      if (next === 'pants' && /점프\s*수트|점프슈트|오버올|멜빵\s*바지|jumpsuit|overall/i.test(t)) next = 'onepiece';
      if (next === 'pants' && /치마\s*바지|스커트\s*팬츠|skort/i.test(t)) next = 'skirt';
      it.meta.catSchema = CATEGORY_SCHEMA_VERSION;
    } else if (LEGACY_CATEGORY_ALIAS[before]) {
      next = legacyCategoryToV2(before, it);          // 변환 후 다시 들어온 레거시 키 방어
    }
    if (next !== before) {
      if (!it.meta.legacyCategoryKey) it.meta.legacyCategoryKey = before;   // 롤백·추적용 원래 키
      it.categoryKey = next;
    }
    return (next !== before) || !done;
  }

  // ── [2026-09-22] AI 분석 결과(category/sub_category) → v2 카테고리 키 (등록 페이지 공용) ──
  //   camera.html / camera_register.html 이 각자 들고 있던 catMap(서로 조금씩 달랐음)을 여기로 일원화.
  //   ① 서버가 준 v2 키(etc 제외)는 그대로 신뢰 — 서버가 세부품목으로 이미 교정한 값
  //   ② 그 외(구 서버 응답·영문·etc)는 세부품목→카테고리 문자열 순으로 키워드 매핑
  //   ⚠️ 순서가 곧 정확도: 구체적인 단어를 먼저 (서버 _SUB2CAT_RULES 와 동일 원칙)
  const _ANALYZED_CAT_RULES = [
    ['드레스셔츠', 'top'], ['dress shirt', 'top'], ['waistcoat', 'top'], ['bootcut', 'pants'],
    ['원피스', 'onepiece'], ['드레스', 'onepiece'], ['점프수트', 'onepiece'], ['점프슈트', 'onepiece'],
    ['오버올', 'onepiece'], ['멜빵바지', 'onepiece'], ['올인원', 'onepiece'], ['jumpsuit', 'onepiece'],
    ['overall', 'onepiece'], ['one-piece', 'onepiece'], ['one piece', 'onepiece'], ['onepiece', 'onepiece'], ['dress', 'onepiece'],
    ['치마바지', 'skirt'], ['스커트', 'skirt'], ['치마', 'skirt'], ['skirt', 'skirt'],
    ['백팩', 'bag'], ['클러치', 'bag'], ['가방', 'bag'], ['배낭', 'bag'], ['backpack', 'bag'], ['clutch', 'bag'],
    ['handbag', 'bag'], ['tote', 'bag'], ['crossbody', 'bag'], ['bag', 'bag'], ['백', 'bag'],
    ['레인부츠', 'shoes'], ['rain boot', 'shoes'],
    ['넥타이', 'etc'], ['보타이', 'etc'], ['necktie', 'etc'], ['bow tie', 'etc'], ['모자', 'etc'], ['비니', 'etc'],
    ['버킷햇', 'etc'], ['캡', 'etc'], ['벨트', 'etc'], ['장갑', 'etc'], ['목걸이', 'etc'], ['귀걸이', 'etc'],
    ['반지', 'etc'], ['팔찌', 'etc'], ['선글라스', 'etc'], ['안경', 'etc'], ['헤어', 'etc'], ['액세서리', 'etc'],
    ['패딩베스트', 'outer'], ['다운베스트', 'outer'], ['퀼팅베스트', 'outer'], ['패딩조끼', 'outer'], ['다운조끼', 'outer'],
    ['down vest', 'outer'], ['puffer vest', 'outer'],
    ['카디건', 'top'], ['가디건', 'top'], ['cardigan', 'top'],
    ['재킷', 'outer'], ['자켓', 'outer'], ['블레이저', 'outer'], ['코트', 'outer'], ['점퍼', 'outer'], ['패딩', 'outer'],
    ['바람막이', 'outer'], ['윈드브레이커', 'outer'], ['레인웨어', 'outer'], ['레인코트', 'outer'], ['우비', 'outer'],
    ['집업', 'outer'], ['볼레로', 'outer'], ['버버리', 'outer'], ['트렌치', 'outer'], ['아우터', 'outer'], ['파카', 'outer'],
    ['jacket', 'outer'], ['blazer', 'outer'], ['coat', 'outer'], ['parka', 'outer'], ['windbreaker', 'outer'],
    ['anorak', 'outer'], ['puffer', 'outer'], ['outer', 'outer'],
    ['스니커즈', 'shoes'], ['운동화', 'shoes'], ['구두', 'shoes'], ['로퍼', 'shoes'], ['부츠', 'shoes'], ['샌들', 'shoes'],
    ['슬리퍼', 'shoes'], ['슬립온', 'shoes'], ['펌프스', 'shoes'], ['워커', 'shoes'], ['힐', 'shoes'], ['신발', 'shoes'],
    ['sneaker', 'shoes'], ['loafer', 'shoes'], ['boot', 'shoes'], ['sandal', 'shoes'], ['heel', 'shoes'], ['shoe', 'shoes'],
    ['시계', 'watch'], ['워치', 'watch'], ['watch', 'watch'],
    ['스카프', 'scarf'], ['머플러', 'scarf'], ['목도리', 'scarf'], ['넥워머', 'scarf'], ['숄', 'scarf'], ['scarf', 'scarf'], ['muffler', 'scarf'],
    ['양말', 'socks'], ['삭스', 'socks'], ['타이즈', 'socks'], ['스타킹', 'socks'], ['덧신', 'socks'],
    ['sock', 'socks'], ['tights', 'socks'], ['stocking', 'socks'],
    ['레깅스', 'pants'], ['청바지', 'pants'], ['슬랙스', 'pants'], ['바지', 'pants'], ['팬츠', 'pants'], ['쇼츠', 'pants'],
    ['조거', 'pants'], ['스키니', 'pants'], ['jeans', 'pants'], ['trousers', 'pants'], ['shorts', 'pants'],
    ['leggings', 'pants'], ['pants', 'pants'],
    ['후드티', 'top'], ['맨투맨', 'top'], ['스웨터', 'top'], ['니트', 'top'], ['블라우스', 'top'], ['티셔츠', 'top'],
    ['셔츠', 'top'], ['면티', 'top'], ['민소매', 'top'], ['나시', 'top'], ['베스트', 'top'], ['조끼', 'top'], ['탑', 'top'],
    ['상의', 'top'], ['shirt', 'top'], ['blouse', 'top'], ['hoodie', 'top'], ['sweater', 'top'], ['knit', 'top'],
    ['vest', 'top'], ['top', 'top'],
  ];
  function resolveAnalyzedCategory(g) {
    if (!g) return 'etc';
    const valid = new Set(DEFAULT_CATEGORIES.map((c) => c.key));
    let cat = String(g.category || '').toLowerCase().trim();
    cat = LEGACY_CATEGORY_ALIAS[cat] || cat;
    if (valid.has(cat) && cat !== 'etc') return cat;
    const sub = String(g.sub_category || '').toLowerCase().trim();
    for (const src of [sub, cat]) {
      if (!src) continue;
      for (let i = 0; i < _ANALYZED_CAT_RULES.length; i++) {
        if (src.indexOf(_ANALYZED_CAT_RULES[i][0]) >= 0) return _ANALYZED_CAT_RULES[i][1];
      }
    }
    return valid.has(cat) ? cat : 'etc';
  }

  // 이 브라우저에 저장된 전체 아이템 일괄 변환 (페이지 로드 시 1회, 변경 있을 때만 저장)
  function migrateAllItemsCategoryV2() {
    try {
      const items = getAllItems();
      if (!Array.isArray(items) || !items.length) return 0;
      let changed = 0;
      items.forEach((it) => { if (migrateItemCategoryV2(it)) changed++; });
      if (changed) setAllItems(items);
      return changed;
    } catch (e) {
      console.warn('[category v2] migrate skipped', e);
      return 0;
    }
  }

  // (레거시/확장용) 기본 외 카테고리는 사용자 커스텀으로 추가하도록 유도
  const OPTIONAL_CATEGORIES = [];

  // 아이템 등록 한도 — 전체 합산 (카테고리별 아님)
  // FREE:10 / SILVER:100 / GOLD:500 / DIAMOND:무제한(일일 100개)
  const PLAN_LIMITS = {
    FREE: 10,
    SILVER: 100,
    GOLD: 500,
    DIAMOND: Infinity,
  };

  // DIAMOND 일일 아이템 등록 한도
  const DIAMOND_DAILY_ITEM_LIMIT = 100;

  // 운영 하드캡 (전체 기준)
  const CATEGORY_MAX_ITEMS = 200; // 레거시 호환용 유지

  // ==============================
  // AI 추천 스타일링 생성(이미지) 사용량 제한
  // - OpenAI 이미지 생성 비용을 고려한 월간 생성 횟수 제한
  // - Prototype: 로컬 저장(LocalStorage) 기반으로 "월" 단위 카운팅
  // ==============================
  const AI_STYLING_LIMITS = {
    FREE: 2,
    SILVER: 40,
    GOLD: 100,
    DIAMOND: Infinity,
  };

  // (UI/가격표용) 월 구독료(원)
  const PLAN_PRICES_KRW = {
    FREE: 0,
    SILVER: 4900,
    GOLD: 9900,
    DIAMOND: 29000,
  };

  function nowIso() {
    return new Date().toISOString();
  }

  function uid(prefix) {
    const p = prefix || 'id';
    return `${p}_${Math.random().toString(16).slice(2)}_${Date.now().toString(16)}`;
  }

  function safeJsonParse(str, fallback) {
    try {
      return JSON.parse(str);
    } catch (_) {
      return fallback;
    }
  }

  function loadJson(key, fallback) {
    const raw = localStorage.getItem(key);
    if (raw === null || raw === undefined) return fallback;
    return safeJsonParse(raw, fallback);
  }

  function saveJson(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return { ok: true };
    } catch (e) {
      console.error('LocalStorage save failed:', key, e);
      const name = String(e && e.name ? e.name : '').toLowerCase();
      const msg = name.includes('quota')
        ? '저장 공간이 부족합니다. 사진 용량을 줄이거나 기존 아이템을 삭제 후 다시 시도해주세요.'
        : '저장 중 오류가 발생했습니다. 브라우저 저장공간/권한을 확인해주세요.';
      return { ok: false, error: msg, rawError: String(e && (e.message || e)) };
    }
  }

  function normalizeEmail(email) {
    return String(email || '').trim().toLowerCase();
  }

  function passwordMeetsRule(pw) {
    // 4자리 이상 + 영문 1개 이상 + 숫자 1개 이상
    return /^(?=.*[A-Za-z])(?=.*\d).{4,}$/.test(String(pw || ''));
  }

  // ── 로컬 캐시용 (아이템/앨범 데이터는 로컬 유지)
  function getUsers() { return loadJson(KEYS.USERS, {}); }
  function setUsers(users) { saveJson(KEYS.USERS, users); }

  function getUser(email) {
    if (_cachedUser && normalizeEmail(_cachedUser.email) === normalizeEmail(email)) return _cachedUser;
    const users = getUsers();
    return users[normalizeEmail(email)] || null;
  }

  function upsertUser(user) {
    const e = normalizeEmail(user.email);
    if (!e) return;
    const users = getUsers();
    users[e] = Object.assign({}, users[e] || {}, user, { email: e });
    saveJson(KEYS.USERS, users);
    if (_cachedUser && normalizeEmail(_cachedUser.email) === e) {
      _cachedUser = Object.assign({}, _cachedUser, user);
    }
  }

  // ── Supabase 기반 프로필 업데이트
  async function updateUserProfile(email, patch) {
    const e = normalizeEmail(email);
    const u = getUser(e);
    const next = Object.assign({}, u || { email: e }, patch || {}, { updatedAt: nowIso() });
    upsertUser(next);
    if (_cachedUser && normalizeEmail(_cachedUser.email) === e) _cachedUser = next;
    try {
      const sb = _getSupabase();
      if (sb) await sb.auth.updateUser({ data: Object.assign({}, patch, { updatedAt: nowIso() }) });
    } catch (_) {}
    return { ok: true, user: next };
  }

  // ── 세션 캐시
  function getSession() { return _cachedSession || loadJson(KEYS.SESSION, null); }
  function setSession(s) { _cachedSession = s; saveJson(KEYS.SESSION, s); }
  function clearSession() {
    _cachedSession = null; _cachedUser = null; _sessionFetched = false;
    try{ localStorage.removeItem(KEYS.SESSION); }catch(_){}
    // ─── 2026-05-09 KST · TJ 지시 (v48) ─── Supabase 토큰도 명시적으로 정리
    //   배경: clearSession이 codibank 자체 키만 지웠음.
    //          Supabase JS SDK가 'sb-{projectRef}-auth-token' 키에 access_token 저장 →
    //          서버에서 사용자 삭제해도 이 토큰이 남아있으면 자동 로그인되는 현상 발생.
    //   처리: codibank-* / sb-* / supabase.* 접두 키 모두 제거.
    try{
      var keysToRemove = [];
      for(var i = 0; i < localStorage.length; i++){
        var k = localStorage.key(i);
        if(!k) continue;
        if(k.indexOf('sb-') === 0 && k.indexOf('-auth-token') !== -1) keysToRemove.push(k);
        if(k.indexOf('supabase.auth.token') === 0) keysToRemove.push(k);
      }
      keysToRemove.forEach(function(k){ try{ localStorage.removeItem(k); }catch(_){} });
    }catch(_){}
  }

  // ─── 2026-05-09 KST · TJ 지시 (v48) ─── 서버 측 세션 유효성 검증 ───
  //   배경: Supabase에서 사용자를 삭제해도 클라이언트 access_token은 만료 전까지 유효.
  //          codibank.js는 _cachedUser/localStorage만 보고 로그인 상태로 판단 → 자동 로그인 버그.
  //   처리: 페이지 진입 시 sb.auth.getUser() 호출 (서버 측 검증).
  //          - error 또는 user null 반환 시: 사용자 삭제됨 → clearSession + sb.auth.signOut + reload
  //          - 정상 user 반환 시: 캐시 동기화 (Supabase가 최신 정보)
  //   효과: 서버에서 삭제된 계정은 다음 페이지 진입 즉시 자동 로그아웃됨.
  async function validateSession(){
    try{
      const sb = _getSupabase();
      if(!sb) return { ok: true, reason: 'no_supabase' };
      // 캐시된 토큰이 없으면 검증할 것도 없음
      if(!_cachedUser && !getSession()){
        return { ok: true, reason: 'no_session' };
      }
      const { data, error } = await sb.auth.getUser();
      if(error || !data || !data.user){
        // 사용자 삭제됨 또는 토큰 무효 — 즉시 정리
        console.warn('[CodiBank][v48] Session invalid — clearing local tokens', error && error.message);
        try{ await sb.auth.signOut({ scope: 'local' }); }catch(_){}
        clearSession();
        return { ok: false, reason: 'invalid_user', cleared: true };
      }
      // 정상 — 캐시 동기화
      _cachedUser = _sbUserToCb(data.user);
      _cachedSession = { email: data.user.email, loggedInAt: nowIso() };
      try{ upsertUser(_cachedUser); }catch(_){}
      return { ok: true, user: _cachedUser };
    }catch(e){
      console.warn('[CodiBank][v48] validateSession error', e);
      return { ok: true, reason: 'error', error: e };
    }
  }

  // ── 현재 로그인 유저 (동기 — 캐시 기반)
  function getCurrentUser() {
    if (_cachedUser) return _cachedUser;
    const sess = getSession();
    if (sess && sess.email) {
      const u = getUser(sess.email);
      if (u) { _cachedUser = u; return u; }
    }
    return null;
  }

  // ── 인증 가드 (동기 + Supabase 세션 비동기 확인)
  // ─── 2026-05-09 KST · TJ 지시 (v45) ─── 작은 인라인 토스트 ───
  //   배경: v39 풀스크린 모달은 backdrop+blur로 서비스 화면을 가려 "독립적"으로 떠있음.
  //          TJ는 코디뱅크 서비스가 그대로 보이는 상태에서 작은 안내만 원함.
  //   변경: backdrop 제거 + 풋바 위 작은 토스트 카드.
  //          [회원가입] [로그인] 버튼 작게 + X 닫기.
  //          5초 후 자동 사라짐(닫기 버튼은 즉시 닫음).
  //          페이지 인터랙션은 그대로 가능 (토스트 외부 영역).
  //   호출: 사용자가 [data-requires-auth] 버튼 클릭 시에만 표시 (자동 표시 제거).
  function showAuthRequiredModal(opts){
    opts = opts || {};
    // 이미 떠 있으면 중복 생성 안 함 (재호출 시 자동-사라짐 타이머만 리셋)
    var existing = document.getElementById('cbAuthToast');
    if(existing){
      try{
        if(existing._cbHideTimer) clearTimeout(existing._cbHideTimer);
        existing._cbHideTimer = setTimeout(function(){
          try{ existing.remove(); }catch(_){}
        }, 5000);
      }catch(_){}
      return;
    }

    var en = (window.CodiBankI18n && CodiBankI18n.isEn());
    var msgTxt    = en ? 'Please sign up or log in' : '회원가입 또는 로그인을 해주세요';
    var signupTxt = en ? 'Sign up' : '회원가입';
    var loginTxt  = en ? 'Log in'  : '로그인';

    // 페이지 경로 보정 (app/ 안 vs 루트)
    function _resolveAuthPath(name){
      var p = window.location.pathname || '';
      if(p.indexOf('/app/') !== -1) return name;
      return 'app/' + name;
    }
    var signupHref = _resolveAuthPath('signup.html');
    var loginHref  = _resolveAuthPath('login.html');

    // 토스트 카드 — 풋바 위(bottom:96px)에 작게 표시. 화면 가리지 않음.
    var toast = document.createElement('div');
    toast.id = 'cbAuthToast';
    toast.style.cssText = 'position:fixed;left:50%;bottom:96px;transform:translateX(-50%);'
      + 'max-width:340px;width:calc(100% - 32px);z-index:2147483640;'
      + 'background:linear-gradient(135deg,rgba(10,31,79,0.96),rgba(7,25,82,0.96));'
      + 'border:1px solid rgba(151,254,237,0.28);border-radius:14px;'
      + 'box-shadow:0 12px 32px rgba(0,0,0,0.35),0 4px 12px rgba(0,0,0,0.2);'
      + 'padding:12px 14px;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);'
      + 'animation:cbAuthToastIn .25s cubic-bezier(.16,1,.3,1);'
      + 'pointer-events:auto;';
    toast.innerHTML = ''
      + '<div style="display:flex;align-items:center;gap:10px;">'
      +   '<span class="material-symbols-outlined" style="font-size:20px;color:#97FEED;flex-shrink:0;">login</span>'
      +   '<div style="flex:1;font-size:13px;font-weight:700;color:#fff;letter-spacing:-.01em;line-height:1.35;">' + msgTxt + '</div>'
      +   '<button type="button" id="cbAuthToastClose" aria-label="close" style="background:none;border:none;color:rgba(255,255,255,0.5);cursor:pointer;padding:2px;display:flex;align-items:center;font-family:inherit;">'
      +     '<span class="material-symbols-outlined" style="font-size:18px;">close</span>'
      +   '</button>'
      + '</div>'
      + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:10px;">'
      +   '<button type="button" id="cbAuthToastSignup" style="padding:8px;border-radius:9px;border:1px solid rgba(151,254,237,0.4);background:rgba(151,254,237,0.10);color:#97FEED;font-weight:800;font-size:12px;cursor:pointer;font-family:inherit;letter-spacing:.01em;">' + signupTxt + '</button>'
      +   '<button type="button" id="cbAuthToastLogin"  style="padding:8px;border-radius:9px;border:none;background:linear-gradient(135deg,#0B666A,#35A29F);color:#fff;font-weight:800;font-size:12px;cursor:pointer;font-family:inherit;letter-spacing:.01em;">' + loginTxt + '</button>'
      + '</div>';

    // 키프레임 1회 주입
    if(!document.getElementById('cbAuthToastKeyframes')){
      var st = document.createElement('style');
      st.id = 'cbAuthToastKeyframes';
      st.textContent = '@keyframes cbAuthToastIn{0%{opacity:0;transform:translateX(-50%) translateY(8px)}100%{opacity:1;transform:translateX(-50%) translateY(0)}}'
        + '@keyframes cbAuthToastOut{0%{opacity:1;transform:translateX(-50%) translateY(0)}100%{opacity:0;transform:translateX(-50%) translateY(8px)}}';
      document.head.appendChild(st);
    }

    document.body.appendChild(toast);

    function _close(){
      try{
        toast.style.animation = 'cbAuthToastOut .2s ease forwards';
        setTimeout(function(){ try{ toast.remove(); }catch(_){} }, 220);
      }catch(_){ try{ toast.remove(); }catch(_){} }
    }
    document.getElementById('cbAuthToastClose').onclick  = _close;
    document.getElementById('cbAuthToastSignup').onclick = function(){ window.location.href = signupHref; };
    document.getElementById('cbAuthToastLogin').onclick  = function(){ window.location.href = loginHref; };

    // 5초 후 자동 사라짐
    toast._cbHideTimer = setTimeout(_close, 5000);
  }

  function requireAuth(redirectTo) {
    // ─── 2026-05-09 KST · TJ 지시 (v39) ─── 동작 변경: redirect → 모달
    //   이전: 비로그인 → window.location.replace(redirectTo) (login.html)
    //   변경: 비로그인 → 페이지에 머물고 모달 표시 + false 반환
    //          호출처(closet/aicloset 등)는 false 받아도 페이지 init 계속 진행 가능.
    //          단 페이지 코드가 user 의존 부분에서 try-catch로 이미 가드되어야 안전.
    if (getCurrentUser()) return true;
    const sb = _getSupabase();
    if (sb) {
      sb.auth.getSession().then(({ data }) => {
        if (data && data.session && data.session.user) {
          _cachedSession = { email: data.session.user.email, loggedInAt: nowIso() };
          _cachedUser    = _sbUserToCb(data.session.user);
          upsertUser(_cachedUser);
          localStorage.setItem(KEYS.PLAN, _cachedUser.plan || 'FREE');
        } else {
          // Supabase 세션도 없음 → 모달 표시 (redirect 대신)
          try{ showAuthRequiredModal(); }catch(_){}
        }
      }).catch(() => { try{ showAuthRequiredModal(); }catch(_){} });
    } else {
      try{ showAuthRequiredModal(); }catch(_){}
    }
    return false;
  }

  // ── 로그아웃
  async function logout(redirectTo) {
    try { const sb = _getSupabase(); if (sb) await sb.auth.signOut(); } catch (_) {}
    clearSession();
    localStorage.setItem(KEYS.PLAN, 'FREE');
    if (redirectTo) window.location.href = redirectTo;
  }


  function migrateUserItemsCategories(email, allowedSet) {
    const e = normalizeEmail(email);
    if (!e) return;

    const items = getAllItems();
    let changed = false;

    items.forEach((it) => {
      if (normalizeEmail(it.userEmail) !== e) return;
      // [2026-09-22] ⚠️ 반드시 v2 변환을 먼저 — 안 그러면 coat/jacket 아이템이
      //   '허용되지 않은 키'로 판정돼 전부 '기타'로 버려짐.
      if (migrateItemCategoryV2(it)) changed = true;
      const key = String(it.categoryKey || '');
      if (!allowedSet.has(key)) {
        if (!it.meta) it.meta = {};
        if (!it.meta.legacyCategoryKey) it.meta.legacyCategoryKey = key;
        it.categoryKey = 'etc';
        changed = true;
      }
    });

    if (changed) setAllItems(items);
  }

  function ensureUserCategories(user) {
    const defaultKeys = DEFAULT_CATEGORIES.map((c) => c.key);

    // 커스텀 카테고리(사용자 입력)
    if (!Array.isArray(user.customCategories)) user.customCategories = [];
    user.customCategories = user.customCategories
      .filter((c) => c && typeof c.key === 'string' && typeof c.label === 'string')
      .map((c) => ({ key: String(c.key), label: String(c.label) }));

    // 유저 카테고리 키 배열
    if (!Array.isArray(user.categories)) user.categories = [];

    const customKeys = user.customCategories.map((c) => c.key);
    const allowed = new Set([...defaultKeys, ...customKeys]);

    // 허용된 카테고리만 유지
    let next = user.categories.filter((k) => allowed.has(k));

    // 기본 9개 카테고리는 항상 앞(고정 순서)
    next = [...defaultKeys, ...next.filter((k) => !defaultKeys.includes(k))];

    // 커스텀 카테고리는 마지막(추가된 순서)
    customKeys.forEach((k) => {
      if (!next.includes(k)) next.push(k);
    });

    if (next.length === 0) next = [...defaultKeys];

    user.categories = next;

    // 구버전 데이터 호환: 알 수 없는 카테고리 아이템은 '기타'로 이동
    try {
      migrateUserItemsCategories(user.email, allowed);
    } catch (e) {
      console.warn('category migrate failed', e);
    }

    // 항상 저장(구버전 사용자에 customCategories 필드 부여)
    upsertUser(user);
  }

  function getCategoryMetaByKey(key, email) {
    const k = LEGACY_CATEGORY_ALIAS[String(key || '')] || String(key || '');   // [2026-09-22] coat/jacket → 겉옷
    const all = [...DEFAULT_CATEGORIES, ...OPTIONAL_CATEGORIES];
    const found = all.find((c) => c.key === k);
    if (found) return found;

    // 커스텀 카테고리는 사용자별로 저장되어 있으므로 email이 있을 때만 조회
    if (email) {
      const u = getUser(email);
      if (u && Array.isArray(u.customCategories)) {
        const cc = u.customCategories.find((c) => c.key === k);
        if (cc) return cc;
      }
    }

    return { key: k, label: k };
  }

  function getCategoriesForUser(email) {
    const u = getUser(email);
    if (!u) return DEFAULT_CATEGORIES;
    ensureUserCategories(u);
    // [2026-09-22 TJ 지시] 성별별 카테고리 — 남성은 스커트·원피스 제외(엄격 적용).
    //   성별 미설정/알 수 없음 → 전체(여성 목록과 동일).
    const g = normalizeGender(u.gender);
    return u.categories
      .map((k) => getCategoryMetaByKey(k, email))
      .filter((c) => !(g === 'M' && c && c.gender === 'F'));
  }

  // [2026-09-22] 성별로 카테고리 키 목록 (로그인 전 화면·외부 모듈용)
  function getCategoryKeysForGender(gender) {
    const g = normalizeGender(gender);
    return DEFAULT_CATEGORIES.filter((c) => !(g === 'M' && c.gender === 'F')).map((c) => c.key);
  }

  function addCategoriesToUser(email, categoryKeys) {
    const u = getUser(email);
    if (!u) return;
    ensureUserCategories(u);
    const set = new Set(u.categories);
    (categoryKeys || []).forEach((k) => set.add(k));
    u.categories = Array.from(set);
    upsertUser(u);
  }

  function addCustomCategoryToUser(email, label) {
    const e = normalizeEmail(email);
    const u = getUser(e);
    if (!u) return { ok: false, error: '사용자를 찾을 수 없습니다.' };

    ensureUserCategories(u);

    const raw = String(label || '').trim();
    const clean = raw.replace(/\s+/g, ' ');
    if (!clean) return { ok: false, error: '카테고리 이름을 입력해주세요.' };
    if (clean.length > 20) return { ok: false, error: '카테고리 이름은 20자 이내로 입력해주세요.' };

    const norm = (s) => String(s || '').replace(/\s+/g, '').toLowerCase();
    const existing = getCategoriesForUser(e);
    if (existing.some((c) => norm(c.label) === norm(clean))) {
      return { ok: false, error: '이미 존재하는 카테고리입니다.' };
    }

    const key = `custom_${uid('cat')}`;
    const meta = { key, label: clean };

    if (!Array.isArray(u.customCategories)) u.customCategories = [];
    u.customCategories.push(meta);
    upsertUser(u);

    // 카테고리 목록의 맨 아래로 추가
    addCategoriesToUser(e, [key]);

    return { ok: true, category: meta };
  }


  function setUserPlan(email, plan) {
    const p = String(plan || 'FREE').toUpperCase();
    const u = getUser(email);
    if (!u) return;
    u.plan = p;
    upsertUser(u);
    // pricing.html 호환
    localStorage.setItem(KEYS.PLAN, p);
  }

  function getUserPlan(email) {
    const u = getUser(email);
    if (u && u.plan) return String(u.plan).toUpperCase();
    const p = localStorage.getItem(KEYS.PLAN);
    return (p || 'FREE').toUpperCase();
  }

  function getPlanLimit(plan) {
    const p = String(plan || 'FREE').toUpperCase();
    return PLAN_LIMITS[p] ?? 5;
  }

  // ==============================
  // AI 추천 스타일링 월 사용량
  // - user.aiStylingUsage = { period: 'YYYY-MM', used: number }
  // - period가 바뀌면 자동 리셋
  // ==============================
  function currentPeriodKey() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    return `${y}-${m}`;
  }

  function getAiStylingLimit(plan) {
    const p = String(plan || 'FREE').toUpperCase();
    return AI_STYLING_LIMITS[p] ?? AI_STYLING_LIMITS.FREE;
  }

  function getPlanPriceKrw(plan) {
    const p = String(plan || 'FREE').toUpperCase();
    return PLAN_PRICES_KRW[p] ?? 0;
  }

  function ensureAiUsage(user) {
    if (!user) return;
    const cur = currentPeriodKey();
    if (!user.aiStylingUsage || typeof user.aiStylingUsage !== 'object') {
      user.aiStylingUsage = { period: cur, used: 0 };
      upsertUser(user);
      return;
    }
    const period = String(user.aiStylingUsage.period || '').trim();
    if (period !== cur) {
      user.aiStylingUsage = { period: cur, used: 0 };
      upsertUser(user);
      return;
    }
    if (!Number.isFinite(Number(user.aiStylingUsage.used))) {
      user.aiStylingUsage.used = 0;
      upsertUser(user);
    }
  }

  function getAiStylingUsage(email) {
    const e = normalizeEmail(email);
    const u = getUser(e);
    const plan = u ? getUserPlan(e) : (localStorage.getItem(KEYS.PLAN) || 'FREE');
    const limit = getAiStylingLimit(plan);
    if (!u) {
      return { ok: true, plan, period: currentPeriodKey(), used: 0, limit, remaining: limit === Infinity ? Infinity : limit };
    }

    ensureAiUsage(u);
    const used = Math.max(0, Math.floor(Number(u.aiStylingUsage.used || 0)));
    const remaining = (limit === Infinity) ? Infinity : Math.max(0, limit - used);
    return { ok: true, plan, period: String(u.aiStylingUsage.period || currentPeriodKey()), used, limit, remaining };
  }

  function getAiStylingRemaining(email) {
    const u = getAiStylingUsage(email);
    return (u && u.ok) ? u.remaining : 0;
  }

  function consumeAiStyling(email, amount) {
    const e = normalizeEmail(email);
    const n = Math.max(1, Math.floor(Number(amount || 1)));
    const u = getUser(e);
    if (!u) return { ok: false, error: '사용자 정보가 없습니다.' };

    ensureAiUsage(u);

    const plan = getUserPlan(e);
    const limit = getAiStylingLimit(plan);
    const used = Math.max(0, Math.floor(Number(u.aiStylingUsage.used || 0)));

    if (limit !== Infinity && (used + n) > limit) {
      return { ok: false, error: 'AI 추천 스타일링 이용 가능 횟수를 모두 사용했습니다.', remaining: 0, used, limit, plan };
    }

    // 무제한은 used만 증가시키지 않아도 되지만, 통계/테스트를 위해 기록은 남깁니다.
    u.aiStylingUsage.used = used + n;
    upsertUser(u);

    const remaining = (limit === Infinity) ? Infinity : Math.max(0, limit - u.aiStylingUsage.used);
    return { ok: true, remaining, used: u.aiStylingUsage.used, limit, plan, period: u.aiStylingUsage.period };
  }

  function getAllItems() {
    return loadJson(KEYS.ITEMS, []);
  }

  function setAllItems(items) {
    return saveJson(KEYS.ITEMS, items);
  }

  function getItemsByUser(email) {
    const e = normalizeEmail(email);
    return getAllItems().filter((it) => normalizeEmail(it.userEmail) === e);
  }

  function getItemsByUserAndCategory(email, categoryKey) {
    const k = LEGACY_CATEGORY_ALIAS[String(categoryKey || '')] || categoryKey;   // [2026-09-22] coat/jacket → outer
    return getItemsByUser(email).filter((it) => it.categoryKey === k);
  }

  function getItemById(id) {
    return getAllItems().find((it) => it.id === id) || null;
  }

  function addItem(email, item) {
    const e = normalizeEmail(email);
    const plan = getUserPlan(e);
    const planLimit = getPlanLimit(plan);

    // ── 아이템 보너스 읽기 (pricing/mypage에서 캐싱한 값)
    let itemBonus = 0;
    try {
      const cached = JSON.parse(localStorage.getItem('cb_item_plan_' + e) || '{}');
      itemBonus = parseInt(cached.bonus || 0);
    } catch (_) {}

    // ── 전체 아이템 합산 체크 (카테고리별 아님)
    const totalItems = getItemsByUser(e).length;
    const isUnlimited = planLimit === Infinity;
    const effectiveLimit = isUnlimited ? Infinity : (planLimit + itemBonus);

    if (!isUnlimited && totalItems >= effectiveLimit) {
      return {
        ok: false,
        error: `현재 플랜(${plan})의 아이템 등록 한도(${effectiveLimit}개)를 초과했습니다. 구독 업그레이드 또는 보너스 신청이 필요합니다.`,
        limit_exceeded: true,
      };
    }

    // ── DIAMOND 일일 등록 한도 체크
    if (isUnlimited) {
      try {
        const today = new Date().toISOString().slice(0, 10);
        const dayKey = 'cb_item_daily_' + e + '_' + today;
        const dayCount = parseInt(localStorage.getItem(dayKey) || '0');
        if (dayCount >= DIAMOND_DAILY_ITEM_LIMIT) {
          return {
            ok: false,
            error: `다이아몬드 플랜의 일일 아이템 등록 한도(${DIAMOND_DAILY_ITEM_LIMIT}개)를 초과했습니다. 내일 다시 시도해주세요.`,
          };
        }
        localStorage.setItem(dayKey, String(dayCount + 1));
      } catch (_) {}
    }

    // [2026-09-22] 옛 페이지·캐시가 레거시 키(coat/jacket)를 보내도 새 체계로 저장
    const categoryKey = legacyCategoryToV2(item.categoryKey, item);

    const items = getAllItems();
    const saved = {
      id: item.id || uid('item'),
      userEmail: e,
      categoryKey,
      color: item.color || '',
      brand: item.brand || '',
      note: item.note || item.description || '',
      images: item.images || {},
      createdAt: item.createdAt || nowIso(),
      meta: Object.assign({}, item.meta || {}, { catSchema: CATEGORY_SCHEMA_VERSION }),
    };

    items.unshift(saved);
    const saveRes = setAllItems(items);
    if (!saveRes || saveRes.ok !== true) {
      // 저장 실패 시 롤백
      try {
        items.shift();
      } catch (_) {}
      return {
        ok: false,
        error: (saveRes && saveRes.error) ? saveRes.error : '저장에 실패했습니다.',
      };
    }

    // 새 카테고리면 유저 카테고리에도 추가
    addCategoriesToUser(e, [categoryKey]);

    return { ok: true, item: saved };
  }

  

  // ==============================
  // Items: update / delete (v14)
  // ==============================
  function updateItem(email, itemId, patch) {
    const e = normalizeEmail(email);
    if (!e) return { ok: false, error: '이메일이 필요합니다.' };

    const id = String(itemId || '');
    if (!id) return { ok: false, error: '아이템 ID가 필요합니다.' };

    const items = getAllItems();
    const idx = items.findIndex((it) => it.id === id && normalizeEmail(it.userEmail) === e);
    if (idx < 0) return { ok: false, error: '아이템을 찾을 수 없습니다.' };

    const before = items[idx];
    const next = Object.assign({}, before);

    // 카테고리 변경 시: 카테고리만 업데이트 (전체 한도는 addItem에서 이미 체크됨)
    const _rawNext = (patch && patch.categoryKey !== undefined) ? String(patch.categoryKey || '') : String(before.categoryKey || '');
    const nextCategory = LEGACY_CATEGORY_ALIAS[_rawNext] || _rawNext;   // [2026-09-22] 레거시 키 방어
    if (nextCategory && nextCategory !== String(before.categoryKey || '')) {
      next.categoryKey = nextCategory;
      next.meta = Object.assign({}, before.meta || {}, { catSchema: CATEGORY_SCHEMA_VERSION });   // 사용자가 직접 정한 값 → 재분류 금지
      addCategoriesToUser(e, [nextCategory]);
    }

    if (patch && patch.color !== undefined) next.color = String(patch.color || '');
    if (patch && patch.brand !== undefined) next.brand = String(patch.brand || '');
    if (patch && patch.note !== undefined) next.note = String(patch.note || '');

    if (patch && patch.images) {
      next.images = Object.assign({}, before.images || {}, patch.images || {});
    }
    if (patch && patch.meta) {
      next.meta = Object.assign({}, before.meta || {}, patch.meta || {});
    }

    next.updatedAt = nowIso();

    items[idx] = next;
    const saveRes = setAllItems(items);

    if (!saveRes || saveRes.ok !== true) {
      // 저장 실패 시 롤백
      try { items[idx] = before; } catch (_) {}
      return { ok: false, error: (saveRes && saveRes.error) ? saveRes.error : '저장에 실패했습니다.' };
    }

    return { ok: true, item: next };
  }

  function deleteItem(email, itemId) {
    const e = normalizeEmail(email);
    if (!e) return { ok: false, error: '이메일이 필요합니다.' };

    const id = String(itemId || '');
    if (!id) return { ok: false, error: '아이템 ID가 필요합니다.' };

    const items = getAllItems();
    const idx = items.findIndex((it) => it.id === id && normalizeEmail(it.userEmail) === e);
    if (idx < 0) return { ok: false, error: '아이템을 찾을 수 없습니다.' };

    const removed = items.splice(idx, 1)[0];
    const saveRes = setAllItems(items);

    if (!saveRes || saveRes.ok !== true) {
      // 롤백
      try { items.splice(idx, 0, removed); } catch (_) {}
      return { ok: false, error: (saveRes && saveRes.error) ? saveRes.error : '삭제에 실패했습니다.' };
    }

    return { ok: true, item: removed };
  }


// ── Supabase 회원가입
  async function signup(payload) {
    const email = normalizeEmail(payload.email);
    if (!email) return { ok: false, error: '이메일을 입력해주세요.' };
    if (!passwordMeetsRule(payload.password)) {
      return { ok: false, error: '비밀번호 규칙(4자리 이상, 영문+숫자 포함)을 확인해주세요.' };
    }
    const sb = _getSupabase();
    if (!sb) return { ok: false, error: 'Supabase 연결 실패. config.js의 supabaseAnonKey를 확인하세요.' };

    const meta = {
      email,
      gender:           payload.gender    || '',
      ageGroup:         payload.ageGroup  || '',
      height:           payload.height    || '',
      weight:           payload.weight    || '',
      location:         payload.location  || '',
      nickname:         payload.nickname  || email.split('@')[0],
      avatarFace:       payload.avatarFace || '',
      plan:             'FREE',
      categories:       DEFAULT_CATEGORIES.map((c) => c.key),
      customCategories: [],
      createdAt:        nowIso(),
    };

    try {
      // ── 이미 Supabase 세션이 있는 경우 (signup.html STEP2에서 로그인 완료된 경우)
      // signUp 재호출 없이 user_metadata만 업데이트
      const { data: sessData } = await sb.auth.getSession();
      if (sessData && sessData.session && sessData.session.user) {
        // 이미 인증된 세션 — 프로필 메타데이터만 업데이트
        await sb.auth.updateUser({ data: meta });
        const cbUser = _sbUserToCb(
          Object.assign({}, sessData.session.user, { user_metadata: Object.assign({}, sessData.session.user.user_metadata, meta) })
        );
        _cachedUser    = cbUser;
        _cachedSession = { email, loggedInAt: nowIso() };
        upsertUser(cbUser);
        localStorage.setItem(KEYS.PLAN, cbUser.plan || 'FREE');
        setSession(_cachedSession);
        return { ok: true, user: cbUser };
      }

      // ── 세션 없음 — 신규 signUp
      // ─── 2026-05-09 KST · TJ 지시 (v41) ─── 이메일 확인 → login.html
      // 안전망: signup.html이 자체 sb.auth.signUp 호출하므로 이 경로는 잘 안 쓰지만,
      //        만약 외부에서 CodiBank.signup()을 직접 호출하는 경우에도 일관된 흐름 보장.
      const { data, error } = await sb.auth.signUp({
        email,
        password: String(payload.password),   // Supabase Auth 파라미터 (meta에는 저장 안 함)
        options: {
          data: meta,
          emailRedirectTo: 'https://codibank.kr/app/login.html?verified=true'
        },
      });
      if (error) {
        const msg = error.message || '';
        return { ok: false, error:
          msg.includes('already registered') ? '이미 가입된 이메일입니다.' :
          msg.includes('invalid') ? '유효하지 않은 이메일입니다.' : msg };
      }
      const cbUser = _sbUserToCb(data.user);
      _cachedUser    = cbUser;
      _cachedSession = { email, loggedInAt: nowIso() };
      upsertUser(cbUser);
      localStorage.setItem(KEYS.PLAN, 'FREE');
      setSession(_cachedSession);
      return { ok: true, user: cbUser };
    } catch (e) {
      return { ok: false, error: String(e && (e.message || e)) };
    }
  }

  // ── Supabase 로그인
  async function login(email, password) {
    const e = normalizeEmail(email);
    if (!e) return { ok: false, error: '이메일을 입력해주세요.' };
    const sb = _getSupabase();
    if (!sb) return { ok: false, error: 'Supabase 연결 실패. config.js의 supabaseAnonKey를 확인하세요.' };

    try {
      const { data, error } = await sb.auth.signInWithPassword({ email: e, password: String(password || '') });
      if (error) {
        const msg = error.message || '';
        return { ok: false, error:
          (msg.includes('Invalid login credentials') || msg.includes('invalid_credentials'))
            ? '이메일 또는 비밀번호가 올바르지 않습니다.' :
          msg.includes('Email not confirmed')
            ? '이메일 인증이 필요합니다. 이메일을 확인해주세요.' :
          msg.includes('User not found')
            ? '가입된 계정을 찾을 수 없습니다.' : msg };
      }
      // 세션 캐시 갱신
      const cbUser = _sbUserToCb(data.user);
      _cachedUser    = cbUser;
      _cachedSession = { email: e, loggedInAt: nowIso() };
      upsertUser(cbUser);
      localStorage.setItem(KEYS.PLAN, cbUser.plan || 'FREE');
      setSession(_cachedSession);
      return { ok: true, user: cbUser };
    } catch (e) {
      return { ok: false, error: String(e && (e.message || e)) };
    }
  }

  // ── 세션 초기화 (앱 로드 시 Supabase 세션 복원)
  // 세션 준비 완료 콜백 (closet/codistyle에서 user 재설정용)
  const _sessionCallbacks = [];
  function onSessionReady(fn) {
    if (_cachedUser) { try { fn(_cachedUser); } catch(_) {} }
    else _sessionCallbacks.push(fn);
  }

  async function _initSession() {
    try {
      const sb = _getSupabase();
      if (!sb) return;
      const { data } = await sb.auth.getSession();
      if (data && data.session && data.session.user) {
        const cbUser = _sbUserToCb(data.session.user);
        _cachedUser    = cbUser;
        _cachedSession = { email: cbUser.email, loggedInAt: nowIso() };
        upsertUser(cbUser);
        localStorage.setItem(KEYS.PLAN, cbUser.plan || 'FREE');
        setSession(_cachedSession);
        // 등록된 콜백 실행
        _sessionCallbacks.forEach(function(fn){ try { fn(cbUser); } catch(_) {} });
        _sessionCallbacks.length = 0;
      }
      _sessionFetched = true;
    } catch (_) {}
  }
  // 앱 로드 시 즉시 세션 복원 시도
  _initSession();

  function hasAnyUser() {
    return !!getCurrentUser();
  }

  // =============================
  // IndexedDB: 이미지 저장(로컬 DB)
  // - localStorage 용량(대략 5MB) 문제로 인해, 이미지는 IndexedDB에 저장하고
  //   아이템에는 imageId(참조)만 저장할 수 있도록 지원
  // - 기존 데이터(DataURL)도 그대로 표시될 수 있도록 호환 유지
  // =============================
  const IDB_CONF = {
    DB_NAME: 'codibank_idb',
    VERSION: 1,
    STORE_IMAGES: 'images',
  };

  let _idbPromise = null;
  const _imageUrlCache = new Map(); // imageId -> objectURL

  function idbSupported() {
    return typeof indexedDB !== 'undefined';
  }

  function openIdb() {
    if (!idbSupported()) return Promise.reject(new Error('IndexedDB not supported'));
    if (_idbPromise) return _idbPromise;

    _idbPromise = new Promise((resolve, reject) => {
      const req = indexedDB.open(IDB_CONF.DB_NAME, IDB_CONF.VERSION);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(IDB_CONF.STORE_IMAGES)) {
          db.createObjectStore(IDB_CONF.STORE_IMAGES, { keyPath: 'id' });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error || new Error('Failed to open IndexedDB'));
    });

    return _idbPromise;
  }

  function dataUrlToBlob(dataUrl) {
    const str = String(dataUrl || '');
    const parts = str.split(',');
    if (parts.length < 2) return new Blob();
    const meta = parts[0] || '';
    const b64 = parts[1] || '';
    const mime = (meta.match(/data:([^;]+);base64/i) || [])[1] || 'image/jpeg';
    const bin = atob(b64);
    const len = bin.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
    return new Blob([bytes], { type: mime });
  }

  function idbPut(storeName, value) {
    return openIdb().then(
      (db) =>
        new Promise((resolve, reject) => {
          const tx = db.transaction(storeName, 'readwrite');
          const store = tx.objectStore(storeName);
          store.put(value);
          tx.oncomplete = () => resolve(true);
          tx.onerror = () => reject(tx.error || new Error('IndexedDB put failed'));
        })
    );
  }

  function idbGet(storeName, key) {
    return openIdb().then(
      (db) =>
        new Promise((resolve, reject) => {
          const tx = db.transaction(storeName, 'readonly');
          const store = tx.objectStore(storeName);
          const req = store.get(key);
          req.onsuccess = () => resolve(req.result || null);
          req.onerror = () => reject(req.error || new Error('IndexedDB get failed'));
        })
    );
  }

  async function saveImage(dataUrl) {
    const str = String(dataUrl || '');
    if (!str) return '';

    // DataURL이 아니면(이미 imageId이거나 blob URL 등) 그대로 반환
    if (!str.startsWith('data:')) return str;

    if (!idbSupported()) return str;

    try {
      const blob = dataUrlToBlob(str);
      const id = uid('img');
      await idbPut(IDB_CONF.STORE_IMAGES, {
        id,
        blob,
        mime: blob.type || 'image/jpeg',
        createdAt: nowIso(),
      });
      return id;
    } catch (e) {
      console.warn('saveImage failed, fallback to dataURL', e);
      return str;
    }
  }

  async function getImageSrc(imageRef) {
    const ref = String(imageRef || '');
    if (!ref) return '';

    // 기존 데이터(DataURL)면 그대로 사용
    if (ref.startsWith('data:') || ref.startsWith('blob:')) return ref;

// 절대 URL(서버에 저장된 이미지 등)
if (ref.startsWith('http://') || ref.startsWith('https://')) return ref;

// 서버 업로드 경로(/uploads/...)는 현재 운영 백엔드/스토리지 호스트 후보를 순차 시도합니다.
if (ref.startsWith('/uploads/')) {
  const candidates = getStorageBasesResolved().map(b => resolveBaseUrl(b, ref));
  for (const url of candidates) {
    try {
      const ok = await _probeImageUrl(url, 4500);
      if (ok) return url;
    } catch (_) {}
  }
  return candidates[0] || ref;
}

    // 캐시된 objectURL
    if (_imageUrlCache.has(ref)) return _imageUrlCache.get(ref);

    if (!idbSupported()) return '';

    try {
      const rec = await idbGet(IDB_CONF.STORE_IMAGES, ref);
      if (!rec || !rec.blob) return '';
      const url = URL.createObjectURL(rec.blob);
      _imageUrlCache.set(ref, url);
      return url;
    } catch (e) {
      console.warn('getImageSrc failed', e);
      return '';
    }
  }

  // ==============================
  // [2026-04-19 FACE] 사용자 얼굴 이미지 전용 로더
  // - codistyle.html / closet.html에서 사용자의 avatarFace(원본 해상도)를 우선 로드
  // - avatarFace가 없으면 photo(300px 썸네일)로 폴백
  // - 얼굴 재현 정확도를 위해 IDB 원본 경로를 최우선 사용
  //
  // 호출처:
  // - codistyle.html: generate() 얼굴 자동 로드
  // - closet.html: generateStyling() 얼굴 자동 로드
  // ==============================
  async function getUserFaceImageSrc(user) {
    try {
      const u = user || getCurrentUser() || {};
      // 1순위: avatarFace (IDB 원본 해상도)
      const faceRef = String(u.avatarFace || '').trim();
      if (faceRef) {
        const src = await getImageSrc(faceRef);
        if (src) return src;
      }
      // 2순위: photo (300px 썸네일, mypage용이지만 fallback)
      const photoRef = String(u.photo || '').trim();
      if (photoRef) {
        const src = await getImageSrc(photoRef);
        if (src) return src;
      }
      return '';
    } catch (e) {
      console.warn('getUserFaceImageSrc failed', e);
      return '';
    }
  }

  // ==============================
  // 서버 파일로 이미지 영구 저장(코디앨범 안정성)
  // - 모바일 브라우저(특히 Android)에서 IndexedDB/Blob URL 이미지가
  //   간헐적으로 사라지거나(짧게 보였다가 삭제) 깨지는 사례가 있어,
  //   데모 안정성을 위해 서버의 /uploads 경로에 저장할 수 있게 합니다.
  //
  // 사용처:
  // - AI 추천 코디 이미지(코디앨범)
  // - 오프라인 옷 등록 이미지(전면/후면/기타)
  // ==============================

  function blobToDataUrl(blob) {
    return new Promise((resolve, reject) => {
      try {
        const fr = new FileReader();
        fr.onload = () => resolve(fr.result);
        fr.onerror = () => reject(fr.error || new Error('FileReader failed'));
        fr.readAsDataURL(blob);
      } catch (e) {
        reject(e);
      }
    });
  }

  async function uploadDataUrlToServer(dataUrl, slot) {
    const str = String(dataUrl || '');
    if (!str.startsWith('data:')) return '';

    const base = getBackendBaseResolved();
    if (!base) return '';

    const url = resolveBaseUrl(base, '/api/storage/upload');
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataUrl: str, slot: String(slot || 'img') }),
    });
    const j = await r.json().catch(() => null);
    if (!r.ok || !j || j.ok !== true) {
      throw new Error((j && j.error) ? String(j.error) : `upload failed: HTTP ${r.status}`);
    }
    // path(/uploads/.. )를 우선 반환(프론트에서 host:8787로 해석)
    return String(j.path || j.url || '');
  }

  async function persistImageRefToServer(imageRef, slot) {
    const ref = String(imageRef || '');
    if (!ref) return '';

    // 이미 서버 파일이면 그대로
    if (ref.startsWith('/uploads/')) return ref;

    // 절대 URL(예: http://192.168.0.x:8787/uploads/.. )인 경우
    // - 예전 데이터가 host를 포함하면, 다른 네트워크/기기에서 깨질 수 있어
    //   가능하면 현재 서버(/uploads)로 재업로드해 "상대경로"로 바꿉니다.
    if (ref.startsWith('http://') || ref.startsWith('https://')) {
      try {
        // (안정화) 예전 데이터가 'http://.../uploads/..' 형태로 저장되면
        // 모바일/외부 네트워크에서 host가 바뀌는 순간 이미지가 깨질 수 있습니다.
        // 같은 서버의 파일이라면 host는 버리고 '/uploads/..' 상대경로로만 유지하는 것이 가장 안전합니다.
        try {
          const u = new URL(ref);
          if (u && u.pathname && String(u.pathname).startsWith('/uploads/')) {
            return String(u.pathname);
          }
        } catch (_) {}
        const blob = await fetch(ref, { mode: 'cors' }).then((res) => {
          if (!res.ok) throw new Error('fetch failed');
          return res.blob();
        });
        const dataUrl = await blobToDataUrl(blob);
        const uploaded = await uploadDataUrlToServer(dataUrl, slot);
        return uploaded || ref;
      } catch (e) {
        console.warn('persistImageRefToServer(url) failed', e);
        return ref;
      }
    }

    // dataURL이면 바로 업로드
    if (ref.startsWith('data:')) {
      try {
        return await uploadDataUrlToServer(ref, slot);
      } catch (e) {
        console.warn('persistImageRefToServer(data) failed', e);
        return ref;
      }
    }

    // blob URL 또는 IndexedDB id
    try {
      const src = ref.startsWith('blob:') ? ref : await getImageSrc(ref);
      if (!src) return '';
      const blob = await fetch(src).then((res) => res.blob());
      const dataUrl = await blobToDataUrl(blob);
      return await uploadDataUrlToServer(dataUrl, slot);
    } catch (e) {
      console.warn('persistImageRefToServer(idb/blob) failed', e);
      return '';
    }
  }

  function clearImageSrcCache() {
    try {
      _imageUrlCache.forEach((url) => {
        try {
          if (typeof URL !== 'undefined' && URL.revokeObjectURL) URL.revokeObjectURL(url);
        } catch (_) {}
      });
    } catch (_) {}
    _imageUrlCache.clear();
  }

// ==============================
// Server storage (prototype)
// - Some mobile browsers may evict large local images quickly.
// - For investor demo, we support uploading images to the local proxy server.
// - Saved ref is a RELATIVE path like "/uploads/xxx.jpg" so that it works on
//   both desktop(localhost) and mobile(Wi‑Fi IP).
// ==============================
async function uploadImageToServer(dataUrl, opts) {
  const str = String(dataUrl || '');
  if (!str) return { ok: false, error: '이미지가 없습니다.' };

  // 0) 이미 서버 경로면 그대로 사용
  if (str.startsWith('/uploads/')) {
    return { ok: true, path: str, url: '' };
  }

  // 0-b) 절대 URL이면 /uploads 경로를 추출(크로스 디바이스 호환)
  if (str.startsWith('http://') || str.startsWith('https://')) {
    try {
      const u = new URL(str);
      const p = String(u.pathname || '');
      if (p.startsWith('/uploads/')) return { ok: true, path: p, url: str };
    } catch (_) {}
    return { ok: true, path: '', url: str };
  }

  const base = getBackendBaseResolved();
  if (!base) return { ok: false, error: '백엔드 서버 주소를 찾을 수 없습니다.' };

  const url = resolveBaseUrl(base, '/api/storage/upload');
  const meta = (opts && typeof opts === 'object') ? opts : {};

  function extFromMime(mime) {
    const m = String(mime || '').toLowerCase();
    if (m.includes('png')) return 'png';
    if (m.includes('webp')) return 'webp';
    if (m.includes('jpeg') || m.includes('jpg')) return 'jpg';
    // heic/heif는 브라우저/서버에서 디코딩 호환이 떨어질 수 있어 jpg로 저장 시도
    if (m.includes('heic') || m.includes('heif')) return 'jpg';
    return 'jpg';
  }

  // 1) multipart/form-data 우선 업로드(용량/속도/안정성 ↑)
  // - DataURL(JSON) 방식은 base64 오버헤드 때문에 커질 수 있습니다.
  if (str.startsWith('data:') && typeof FormData !== 'undefined') {
    try {
      const blob = dataUrlToBlob(str);
      const form = new FormData();
      const slot = String(meta.slot || 'img');
      const ext = extFromMime(blob && blob.type ? blob.type : 'image/jpeg');
      form.append('file', blob, `${slot}.${ext}`);
      if (meta.slot) form.append('slot', String(meta.slot));
      if (meta.email) form.append('email', String(meta.email));

      const ctrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
      const t = ctrl ? setTimeout(() => ctrl.abort(), 45000) : null;

      try {
        const res = await fetch(url, {
          method: 'POST',
          body: form,
          signal: ctrl ? ctrl.signal : undefined,
        });

        const j = await res.json().catch(() => ({}));
        if (res.ok && j && j.ok === true) {
          return { ok: true, path: String(j.path || ''), url: String(j.url || '') };
        }
        // multipart를 서버가 처리 못하는 경우(JSON fallback)
      } finally {
        if (t) clearTimeout(t);
      }
    } catch (_) {
      // multipart 실패 시 JSON fallback
    }
  }

  // 2) JSON(dataUrl) fallback
  const payload = Object.assign({ dataUrl: str }, meta);

  const ctrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const t = ctrl ? setTimeout(() => ctrl.abort(), 45000) : null;

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: ctrl ? ctrl.signal : undefined,
    });
    const j = await res.json().catch(() => ({}));
    if (!res.ok || !j || j.ok !== true) {
      return { ok: false, error: (j && j.error) ? j.error : `업로드 실패(HTTP ${res.status})` };
    }
    // Prefer relative path for cross-device compatibility
    return { ok: true, path: String(j.path || ''), url: String(j.url || '') };
  } catch (e) {
    return { ok: false, error: '서버 업로드 중 오류가 발생했습니다.' };
  } finally {
    if (t) clearTimeout(t);
  }
}



  // =============================
  // Location & Weather
  // =============================
  async function fetchJsonWithTimeout(url, timeoutMs) {
    const ms = Number(timeoutMs || 9000);
    const ctrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
    const t = ctrl ? setTimeout(() => ctrl.abort(), ms) : null;

    try {
      const res = await fetch(url, ctrl ? { signal: ctrl.signal } : undefined);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } finally {
      if (t) clearTimeout(t);
    }
  }

  function getGpsPosition(opts) {
    const timeoutMs = Number((opts && opts.timeoutMs) || 8000);
    const maximumAge = Number((opts && opts.maximumAge) || 300000);
    const enableHighAccuracy = (opts && typeof opts.enableHighAccuracy === 'boolean') ? opts.enableHighAccuracy : true;

    return new Promise((resolve, reject) => {
      if (!navigator.geolocation || !navigator.geolocation.getCurrentPosition) {
        reject(new Error('Geolocation not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          resolve({
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            accuracy: pos.coords.accuracy,
            source: 'gps',
          });
        },
        (err) => reject(err),
        { enableHighAccuracy, timeout: timeoutMs, maximumAge }
      );
    });
  }

  function buildLocationLabel(geo) {
    if (!geo) return '현재 위치';
    const city = String(geo.city || '').trim();
    const locality = String(geo.locality || '').trim();
    const region = String(geo.principalSubdivision || '').trim();

    const main = city || locality || region || String(geo.countryName || '').trim() || '현재 위치';

    if (region && main && region !== main && !main.includes(region)) {
      const combo = `${region} ${main}`.trim();
      return combo.length > 18 ? main : combo;
    }
    return main;
  }

  async function getSmartLocation(opts) {
    const language = (opts && opts.language) ? String(opts.language) : 'ko';
    const timeoutMs = Number((opts && opts.timeoutMs) || 9000);

    // 1) GPS 시도
    let gps = null;
    try {
      gps = await getGpsPosition({ timeoutMs: 8000, maximumAge: 120000, enableHighAccuracy: true });
    } catch (_) {
      gps = null;
    }

    // 2) BigDataCloud reverse-geocode-client
    const url = gps
      ? `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${encodeURIComponent(gps.lat)}&longitude=${encodeURIComponent(gps.lon)}&localityLanguage=${encodeURIComponent(language)}`
      : `https://api.bigdatacloud.net/data/reverse-geocode-client?localityLanguage=${encodeURIComponent(language)}`;

    try {
      const geo = await fetchJsonWithTimeout(url, timeoutMs);
      const lat = gps ? gps.lat : (geo && typeof geo.latitude === 'number' ? geo.latitude : null);
      const lon = gps ? gps.lon : (geo && typeof geo.longitude === 'number' ? geo.longitude : null);
      const label = buildLocationLabel(geo);
      const source = gps ? 'gps' : (geo && geo.lookupSource ? String(geo.lookupSource) : 'ip');

      return {
        ok: true,
        lat,
        lon,
        label,
        source,
        accuracy: gps ? gps.accuracy : null,
        raw: geo,
      };
    } catch (e) {
      // BigDataCloud 실패 시에도 GPS가 있으면 좌표 기반으로 반환
      if (gps) {
        return { ok: true, lat: gps.lat, lon: gps.lon, label: '현재 위치', source: 'gps', accuracy: gps.accuracy, raw: null };
      }
      return { ok: false, error: '위치 정보를 가져올 수 없습니다.' };
    }
  }

  function weatherCodeToKorean(code) {
    const c = Number(code);
    if (c === 0) return { text: '맑음', icon: 'wb_sunny' };
    if ([1, 2].includes(c)) return { text: '대체로 맑음', icon: 'partly_cloudy_day' };
    if (c === 3) return { text: '흐림', icon: 'cloud' };
    if ([45, 48].includes(c)) return { text: '안개', icon: 'foggy' };
    if ([51, 53, 55].includes(c)) return { text: '이슬비', icon: 'rainy' };
    if ([56, 57].includes(c)) return { text: '어는 이슬비', icon: 'rainy' };
    if ([61, 63, 65].includes(c)) return { text: '비', icon: 'rainy' };
    if ([66, 67].includes(c)) return { text: '어는 비', icon: 'rainy' };
    if ([71, 73, 75].includes(c)) return { text: '눈', icon: 'ac_unit' };
    if (c === 77) return { text: '싸락눈', icon: 'ac_unit' };
    if ([80, 81, 82].includes(c)) return { text: '소나기', icon: 'rainy' };
    if (c === 95) return { text: '뇌우', icon: 'thunderstorm' };
    if ([96, 99].includes(c)) return { text: '뇌우(우박)', icon: 'thunderstorm' };
    return { text: '날씨', icon: 'cloud' };
  }

  // ==============================
  // Weather provider
  // - OPEN_METEO_DEV: prototype-friendly (but NOT recommended for commercial prod)
  // - KMA: data.go.kr / KMA (recommended for commercial, requires key/proxy)
  // ==============================
  async function getWeatherByCoordsOpenMeteo(lat, lon, opts) {
    const timeoutMs = Number((opts && opts.timeoutMs) || 9000);
    const tz = (opts && opts.timezone) ? String(opts.timezone) : 'auto';
    // ─── 2026-04-26 KST v11 TJ 지시 ──────────────────────────────────────
    // 1) 일별 최고/최저 온도뿐 아니라 강수확률·풍속·UV 지수 추가
    // 2) 시간별로도 강수확률·풍속을 받아 정확한 시간대 분석 가능
    // 3) 별도로 Open-Meteo air-quality API에서 PM2.5 가져와 병합
    // 추가 파라미터:
    //   - daily: precipitation_probability_max, wind_speed_10m_max, uv_index_max
    //   - hourly: precipitation_probability, wind_speed_10m
    // ─────────────────────────────────────────────────────────────────────
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${encodeURIComponent(lat)}&longitude=${encodeURIComponent(lon)}&current=temperature_2m,weather_code,is_day,precipitation,wind_speed_10m&hourly=temperature_2m,weather_code,precipitation_probability,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max,wind_speed_10m_max,uv_index_max&forecast_days=14&timezone=${encodeURIComponent(tz)}`;
    
    const w = await fetchJsonWithTimeout(url, timeoutMs);
    
    // [v11] 미세먼지(PM2.5) 별도 호출 — air-quality API
    // 실패해도 기본 날씨는 정상 반환되도록 안전 처리
    try {
      const aqUrl = `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${encodeURIComponent(lat)}&longitude=${encodeURIComponent(lon)}&current=pm2_5,pm10&hourly=pm2_5&forecast_days=7&timezone=${encodeURIComponent(tz)}`;
      const aq = await fetchJsonWithTimeout(aqUrl, Math.min(timeoutMs, 6000));
      if (aq) {
        w.airQuality = {
          current: aq.current || null,
          hourly: aq.hourly || null,
        };
      }
    } catch (_) {
      // PM2.5 가져오기 실패 시 무시 (기본 날씨는 사용 가능)
      w.airQuality = null;
    }
    
    return w;
  }

  async function getWeatherByCoordsKmaViaBackend(lat, lon, opts) {
    const cfg = getConfig();
    const timeoutMs = Number((opts && opts.timeoutMs) || 9000);
    const tz = (opts && opts.timezone) ? String(opts.timezone) : 'Asia/Seoul';
    const base = cfg.backendBase;
    const url = resolveBaseUrl(base, `/api/weather?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&tz=${encodeURIComponent(tz)}`);
    return fetchJsonWithTimeout(url, timeoutMs);
  }

  async function getWeatherByCoords(lat, lon, opts) {
    const cfg = getConfig();
    const provider = String(cfg.weatherProvider || 'OPEN_METEO_DEV').toUpperCase();

    // 1) Prefer KMA if configured
    if (provider === 'KMA') {
      try {
        // Recommended: backend proxy (hides key + avoids CORS)
        if (cfg.backendBase) {
          return await getWeatherByCoordsKmaViaBackend(lat, lon, opts);
        }
      } catch (_) {
        // fallthrough
      }

      // If KMA is selected but proxy not available, fallback only if explicitly allowed
      if (cfg.allowOpenMeteoDev) {
        return getWeatherByCoordsOpenMeteo(lat, lon, opts);
      }

      throw new Error('KMA 날씨 설정이 필요합니다. (backend proxy 또는 서비스키)');
    }

    // 2) Default: OPEN_METEO_DEV
    return getWeatherByCoordsOpenMeteo(lat, lon, opts);
  }



  /* ============================================================
     지역 판별 & main/sub 스타일리스트 도시 매핑
     - 사용자 위치 → 지역(아시아/유럽/중동 등) → main/sub 패션 도시
     ============================================================ */
  const _REGION_KEYWORDS = {
    '아시아': ['korea','seoul','busan','incheon','daegu','daejeon','gwangju','ulsan','jeju','japan','tokyo','osaka','china','beijing','shanghai','hong kong','singapore','bangkok','thailand','vietnam','hanoi','ho chi minh','indonesia','jakarta','philippines','manila','malaysia','kuala lumpur','taiwan','taipei','india','mumbai','new delhi','한국','서울','부산','인천','대구','대전','광주','울산','제주','일본','도쿄','중국','베이징','상하이','홍콩','싱가포르','방콕','하노이','호치민','자카르타','마닐라','대만','타이베이','뭄바이','뉴델리'],
    '유럽': ['paris','france','london','uk','england','berlin','germany','rome','italy','milan','madrid','spain','amsterdam','netherlands','barcelona','vienna','austria','prague','zurich','switzerland','moscow','russia','stockholm','sweden','copenhagen','denmark','lisbon','portugal','athens','greece','warsaw','poland','budapest','hungary','dublin','ireland','brussels','belgium','helsinki','finland','oslo','norway','파리','런던','베를린','로마','밀라노','마드리드','암스테르담','바르셀로나','비엔나','프라하','취리히','모스크바','스톡홀름','코펜하겐','리스본','아테네','바르샤바','부다페스트','더블린','브뤼셀','헬싱키','오슬로'],
    '중동': ['dubai','abu dhabi','uae','riyadh','saudi','doha','qatar','bahrain','kuwait','oman','istanbul','turkey','cairo','egypt','iran','tehran','israel','tel aviv','jordan','lebanon','두바이','아부다비','리야드','도하','카이로','이스탄불','테헤란'],
    '아프리카': ['cape town','south africa','johannesburg','nairobi','kenya','lagos','nigeria','casablanca','morocco','케이프타운','요하네스버그','나이로비','라고스','카사블랑카'],
    '북미': ['new york','los angeles','chicago','usa','san francisco','miami','seattle','boston','washington','houston','toronto','canada','vancouver','las vegas','뉴욕','로스앤젤레스','시카고','샌프란시스코','마이애미','시애틀','보스턴','워싱턴','토론토','밴쿠버'],
    '남미': ['são paulo','sao paulo','rio','brazil','buenos aires','argentina','lima','peru','bogota','colombia','santiago','chile','mexico city','mexico','상파울루','리우','부에노스아이레스','리마','보고타','산티아고','멕시코시티'],
    '오세아니아': ['sydney','melbourne','australia','auckland','new zealand','시드니','멜버른','오클랜드'],
  };
  const _CITY_MAP = {
    '아시아':    { main: '서울',     sub: '뉴욕' },
    '유럽':      { main: '파리',     sub: '밀라노' },
    '중동':      { main: '두바이',   sub: '뉴욕' },
    '아프리카':  { main: '파리',     sub: '밀라노' },
    '북미':      { main: '뉴욕',     sub: '밀라노' },
    '남미':      { main: '상파울루', sub: '뉴욕' },
    '오세아니아':{ main: '뉴욕',     sub: '런던' },
  };

  function detectRegion(locationStr) {
    if (!locationStr) return '아시아';
    const loc = String(locationStr).toLowerCase().trim();
    for (const [region, keywords] of Object.entries(_REGION_KEYWORDS)) {
      for (const kw of keywords) {
        if (loc.includes(kw)) return region;
      }
    }
    return '아시아';
  }

  function getMainSubCities(locationStr) {
    const region = detectRegion(locationStr);
    const mapping = _CITY_MAP[region] || _CITY_MAP['아시아'];
    return { region, main: mapping.main, sub: mapping.sub };
  }


  /* ============================================================
     AI 코디앨범 (로컬 저장)
     - 생성된 AI 추천 코디 이미지를 날짜/날씨/목적과 함께 저장
     - 저장소: localStorage(메타데이터) + IndexedDB(images) 참조
     ============================================================ */
  const AI_ALBUM_KEY = 'codibank_ai_album_v1';

  function getAiAlbumAll() {
    const raw = loadJson(AI_ALBUM_KEY, []);
    return Array.isArray(raw) ? raw : [];
  }

  function setAiAlbumAll(arr) {
    return saveJson(AI_ALBUM_KEY, Array.isArray(arr) ? arr : []);
  }

  function getAiAlbumEntries(email) {
    const e = normalizeEmail(email);
    return getAiAlbumAll().filter(x => normalizeEmail(x && x.email) === e);
  }

  function addAiAlbumEntry(email, entry) {
    const e = normalizeEmail(email);
    const all = getAiAlbumAll();
    const id = (entry && entry.id) ? String(entry.id) : uid();
    const next = Object.assign(
      {
        id,
        email: e,
        createdAt: nowIso(),
      },
      entry || {}
    );
    // 최신이 위로
    all.unshift(next);
    // 너무 커지지 않게 상한(데모 기준)
    const capped = all.slice(0, 500);
    setAiAlbumAll(capped);
    return { ok: true, entry: next };
  }

  function updateAiAlbumEntry(email, id, patch) {
    const e = normalizeEmail(email);
    const sid = String(id || '');
    if (!e || !sid) return { ok: false };
    const all = getAiAlbumAll();
    let changed = false;
    const next = all.map((x) => {
      if (normalizeEmail(x && x.email) === e && String(x && x.id) === sid) {
        changed = true;
        return Object.assign({}, x, patch || {});
      }
      return x;
    });
    if (changed) setAiAlbumAll(next);
    return { ok: changed };
  }

  function deleteAiAlbumEntry(email, id) {
    const e = normalizeEmail(email);
    const sid = String(id || '');
    const all = getAiAlbumAll().filter(x => !(normalizeEmail(x && x.email) === e && String(x && x.id) === sid));
    setAiAlbumAll(all);
    return { ok: true };
  }

  /* ============================================================
     회원 탈퇴(계정 삭제)
     - Prototype: 로컬 저장소(users/items/ai-album)에서 데이터 제거
     - 서버 업로드 파일(/uploads/..)은 데모 서버의 파일이므로 즉시 삭제하지 않습니다.
       (필요하면 추후 서버에 삭제 API를 추가)
     ============================================================ */
  async function deleteUserAccount(email) {
    const e = normalizeEmail(email);
    if (!e) return { ok: false, error: '이메일이 없습니다.' };
    try {
      // ─── 2026-09-24 KST · TJ 지시 ─── 서버 탈퇴(본인 토큰 검증) 먼저 → 성공해야 로컬 정리
      //   이전: 존재하지 않는 /api/user/delete 를 로그아웃 뒤에 호출(토큰 없음) → 서버 계정이 남았음
      const sb = (window.CodiBankConsent && window.CodiBankConsent.client) ? await window.CodiBankConsent.client() : _getSupabase();
      let _tok = '';
      try { const _s = sb ? await sb.auth.getSession() : null; _tok = (_s && _s.data && _s.data.session && _s.data.session.access_token) || ''; } catch (_) {}
      const _base = (window.CODIBANK_CONFIG && window.CODIBANK_CONFIG.backendBase) || 'https://codibank-api.onrender.com';
      const _r = await fetch(_base + '/api/user/withdraw', { method: 'POST',
        headers: Object.assign({ 'Content-Type': 'application/json' }, _tok ? { Authorization: 'Bearer ' + _tok } : {}),
        body: JSON.stringify({ email: e }) });
      const _d = await _r.json().catch(() => ({}));
      if (!_r.ok || !_d.ok) return { ok: false, error: _d.error || '회원탈퇴 처리 중 오류가 발생했습니다.' };

      // 1) Supabase 로그아웃 (세션 제거)
      if (sb) { try { await sb.auth.signOut({ scope: 'local' }); } catch (_) {} }
      clearSession();

      // 2) 로컬 데이터 정리
      const users = getUsers();
      delete users[e];
      setUsers(users);
      try {
        const items = getAllItems();
        setAllItems((Array.isArray(items)?items:[]).filter(it=>normalizeEmail(it&&it.userEmail)!==e));
      } catch (_) {}
      try {
        const all = getAiAlbumAll();
        setAiAlbumAll((Array.isArray(all)?all:[]).filter(x=>normalizeEmail(x&&x.email)!==e));
      } catch (_) {}
      try { localStorage.removeItem(`codibank_weather_cache_v1_${e}`); } catch (_) {}

      return { ok: true };
    } catch (err) {
      return { ok: false, error: '회원탈퇴 처리 중 오류가 발생했습니다.' };
    }
  }

  /* ============================================================
     관리자 계정 (버전이 바뀌어도 유지)
     ============================================================ */
  // ensureAdminAccount: Supabase 기반으로 전환 후 로컬 demo 계정 불필요
  function ensureAdminAccount() { return { ok: true }; }

  /* ============================================================
     간편로그인(데모)
     - 실제 OAuth 연동 전, "버튼이 작동"하도록 로컬 계정으로 로그인 처리
     ============================================================ */
  function socialLogin(provider) {
    const p = String(provider || '').trim().toLowerCase();
    const supported = ['naver', 'kakao'];
    if (!supported.includes(p)) return { ok: false, error: '지원하지 않는 간편로그인입니다.' };

    const email = normalizeEmail(`${p}@social`);
    let u = getUser(email);
    if (!u) {
      u = {
        email,
        password: `${p}1234`, // 규칙 충족(영문+숫자)
        createdAt: nowIso(),
        updatedAt: nowIso(),
        plan: 'FREE',
        nickname: p === 'naver' ? '네이버 유저' : '카카오 유저',
        socialProvider: p,
      };
      upsertUser(u);
    }

    setSession({ email: u.email, loggedInAt: nowIso(), provider: p });
    return { ok: true, user: u };
  }

  

  // ==============================
  // Bottom Navigation Active Fix
  // - 여러 페이지에서 복사/붙여넣기 하다 보면 '활성화 컬러'가 잘못 지정되는 경우가 생깁니다.
  // - 현재 URL(페이지)에 따라 하단 탭을 자동으로 활성화하여 UI 에러를 방지합니다.
  // ==============================
  function _cbNormalizeFileName(hrefOrPath) {
    try {
      const u = new URL(String(hrefOrPath || ''), (typeof window !== 'undefined' && window.location) ? window.location.href : 'http://localhost/');
      const p = u.pathname || '';
      const file = p.split('/').filter(Boolean).pop() || '';
      return file || '';
    } catch (_) {
      const s = String(hrefOrPath || '');
      const parts = s.split('/').filter(Boolean);
      return parts.length ? parts[parts.length - 1] : s;
    }
  }

  function _cbResolveActiveNavFile() {
    const cur = _cbNormalizeFileName((typeof window !== 'undefined' && window.location) ? window.location.pathname : '');
    // 서브 페이지들은 가장 가까운 탭으로 묶어줍니다.
    const map = {
      'index.html': 'closet.html',
      'item.html': 'camera.html',  // [2026-04-07] 아이템은 Ai 옷장 소속
      'camera.html': 'camera.html',
      'closet.html': 'closet.html',
      'album.html': 'album.html',
      'share-sale.html': 'share-sale.html',
      'share.html': 'share-sale.html',    // 레거시 페이지도 공유판매 탭으로
      'sale.html': 'share-sale.html',     // 레거시 페이지도 공유판매 탭으로
      'share-item.html': 'share-sale.html',
      'sale-item.html': 'share-sale.html',
      'codistyle.html': 'codistyle.html',
      'mypage.html': 'mypage.html',
      'pricing.html': 'mypage.html',
      'login.html': 'mypage.html',
      'signup.html': 'mypage.html',
    };
    return map[cur] || cur || 'closet.html';
  }

  function initBottomNavActive() {
    try {
      const activeFile = _cbResolveActiveNavFile();

      // 하단 네비게이션은 보통 fixed bottom-0 클래스(또는 유사)로 구성됩니다.
      const nav = document.querySelector('nav.fixed.bottom-0, nav[data-cb-bottom-nav]');
      if (!nav) return;

      const links = Array.from(nav.querySelectorAll('a[href]'));
      if (!links.length) return;

      links.forEach((a) => {
        const hrefFile = _cbNormalizeFileName(a.getAttribute('href') || '');
        const isActive = (hrefFile === activeFile);

        // 텍스트 컬러
        a.classList.remove('text-accent', 'text-slate-500');
        a.classList.add(isActive ? 'text-accent' : 'text-slate-500');

        // 아이콘 filled 처리
        const icon = a.querySelector('.material-symbols-outlined');
        if (icon) {
          if (isActive) icon.classList.add('filled');
          else icon.classList.remove('filled');
        }
      });
    } catch (e) {
      // UI 보조 기능이므로 실패해도 서비스는 동작해야 합니다.
      console.warn('[codibank] initBottomNavActive failed', e);
    }
  }

  try {
    if (typeof document !== 'undefined') {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBottomNavActive);
      } else {
        initBottomNavActive();
      }
      window.addEventListener('popstate', initBottomNavActive);
      window.addEventListener('hashchange', initBottomNavActive);
    }
  } catch (_) {}

  // ─── 2026-09-22 KST · TJ 지시 ─── 카테고리 schema v2 자동 변환 (페이지 로드마다, 변경 시에만 저장)
  //   coat/jacket → outer(가디건·니트베스트는 top), 넥타이 → etc, 점프수트·오버올 → onepiece,
  //   치마바지 → skirt. 아이템당 1회만 내용 기반 재분류(meta.catSchema=2), 원래 키는 meta.legacyCategoryKey.
  try {
    const _mv2 = migrateAllItemsCategoryV2();
    if (_mv2) console.log('[category v2] 아이템', _mv2, '개 변환 완료');
  } catch (_) {}

window.CodiBank = {
    // config
    getConfig,
    getBackendBaseResolved,

    DEFAULT_CATEGORIES,
    OPTIONAL_CATEGORIES,
    LEGACY_CATEGORY_ALIAS,          // [2026-09-22] 카테고리 v2
    normalizeGender,
    getCategoryKeysForGender,
    legacyCategoryToV2,
    migrateAllItemsCategoryV2,
    resolveAnalyzedCategory,
    passwordMeetsRule,
    uid,
    nowIso,

    // auth
    ensureAdminAccount,
    socialLogin,
    getSupabaseClient: _getSupabase,   // signup.html 등 외부에서 단일 클라이언트 사용
    onSessionReady,

    hasAnyUser,
    getCurrentUser,
    requireAuth,
    showAuthRequiredModal,    // (v39) 비로그인 안내 모달 — 호출처에서 force 옵션으로 강제 표시 가능
    validateSession,          // (v48) 서버 측 세션 유효성 검증 — 삭제된 계정 자동 정리
    login,
    signup,
    logout,

    // profile
    updateUserProfile,
    deleteUserAccount,

    // plan
    getUserPlan,
    setUserPlan,
    getPlanLimit,
    getPlanPriceKrw,
    getAiStylingLimit,
    getAiStylingUsage,
    getAiStylingRemaining,
    consumeAiStyling,

    // categories
    getCategoryMetaByKey,
    getCategoriesForUser,
    addCategoriesToUser,
    addCustomCategoryToUser,

    // items
    getAllItems,
    getItemsByUser,
    getItemsByUserAndCategory,
    getItemById,
    addItem,
    updateItem,
    deleteItem,

    // images
    addAiAlbumEntry,
    getAiAlbumEntries,
    deleteAiAlbumEntry,
    updateAiAlbumEntry,

    // 이미지 서버 저장
    uploadDataUrlToServer,
    persistImageRefToServer,

    saveImage,
    uploadImageToServer,
    getImageSrc,
    getUserFaceImageSrc,
    clearImageSrcCache,

    // location & weather
    getSmartLocation,
    getWeatherByCoords,
    weatherCodeToKorean,

    // region & city mapping
    detectRegion,
    getMainSubCities,
  };
})();

// ─── 2026-05-09 KST · TJ 지시 (v42) ─── 비로그인 click 가드 ───
//   동작: HTML에 [data-requires-auth] 속성 가진 요소 클릭 시
//          비로그인 → preventDefault + stopPropagation + 팝업 강제 표시
//          로그인됨 → 정상 동작
//   범위: 모든 페이지 자동 적용 (codibank.js 로드 시점에 등록)
(function _cbAuthClickGuard(){
  function _isAuthed(){
    try{ return !!(window.CodiBank && CodiBank.getCurrentUser && CodiBank.getCurrentUser()); }
    catch(_){ return false; }
  }
  document.addEventListener('click', function(e){
    try{
      // 가드 대상 요소 탐색 (자기 자신 또는 가장 가까운 부모)
      var t = e.target.closest && e.target.closest('[data-requires-auth]');
      if(!t) return;
      if(_isAuthed()) return;          // 로그인 상태면 통과
      // 비로그인 → 차단 + 팝업
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation && e.stopImmediatePropagation();
      try{
        if(window.CodiBank && CodiBank.showAuthRequiredModal){
          CodiBank.showAuthRequiredModal({force:true});
        }
      }catch(_){}
    }catch(_){}
  }, true);  // capture 단계 — 다른 핸들러보다 먼저 실행
})();


// ─── 2026-05-09 KST · TJ 지시 (v45) ─── 자동 표시 비활성 ───
//   v39: 페이지 진입 시 비로그인이면 자동 모달 표시 (세션당 1회).
//   v45: TJ는 사용자가 액션 버튼을 클릭한 시점에만 토스트가 뜨길 원함.
//        → 자동 표시 IIFE 제거. 페이지 진입은 깨끗하게.
//        → [data-requires-auth] 가드(_cbAuthClickGuard)가 클릭 시 토스트 호출.
//   (이전 _cbAutoAuthModal IIFE는 의도적으로 삭제됨)


// ─── 2026-05-09 KST · TJ 지시 (v48) ─── 페이지 진입 시 자동 세션 검증 ───
//   배경: Supabase 대시보드에서 사용자를 삭제해도 클라이언트 access_token은
//          만료 전까지 유효 → 자동 로그인 상태로 보이는 버그.
//   처리: 페이지 로드 후 sb.auth.getUser() 호출 (서버 검증).
//          - 사용자 삭제됨 / 토큰 무효 → clearSession + reload (로그아웃 상태로)
//          - 정상 → 캐시 동기화
//   범위: 모든 codibank 페이지 자동 적용. login.html / signup.html은 제외
//          (그 페이지 자체가 인증 진행 중).
(function _cbAutoValidateSession(){
  function _shouldSkip(){
    var p = (window.location.pathname || '').toLowerCase();
    if(p.indexOf('login.html')   !== -1) return true;
    if(p.indexOf('signup.html')  !== -1) return true;
    if(p.indexOf('terms.html')   !== -1) return true;
    if(p.indexOf('privacy.html') !== -1) return true;
    if(p.indexOf('refund.html')  !== -1) return true;
    if(p.indexOf('withdraw.html')!== -1) return true;
    return false;
  }
  async function _check(){
    try{
      if(_shouldSkip()) return;
      if(!window.CodiBank || !window.CodiBank.validateSession) return;
      var result = await window.CodiBank.validateSession();
      if(result && !result.ok && result.cleared){
        try{ window.location.reload(); }catch(_){}
        return;
      }
      // ─── 2026-09-24 KST · TJ 지시 ─── 로그인 사용자 → 현재 버전 동의 확인 (없으면 동의 시트)
      //   대부분 페이지는 SDK 없이 로컬 캐시로 동작(reason='no_supabase') → 캐시 사용자 기준으로 확인,
      //   부족하면 ensure() 가 SDK 를 지연 로드해 서버 기록을 재확인한 뒤에만 시트를 띄움
      var _cu = (result && result.user) || (window.CodiBank.getCurrentUser && window.CodiBank.getCurrentUser());
      if(result && result.ok && _cu && window.CodiBankConsent){
        try{ await window.CodiBankConsent.ensure(); }catch(_){}
      }
    }catch(_){}
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ setTimeout(_check, 200); });
  } else {
    setTimeout(_check, 200);
  }
})();

// ─── 2026-05-09 KST · TJ 지시 (v49) ─── 영어 모드 풋바/공통 라벨 정규화 ───
//   배경: 영어 모드에서 풋바 일부 라벨이 한글 그대로 노출 (트라이온, Ai 옷장, 코디앨범 등).
//          페이지별 i18n 사전 매핑 누락/혼선이 원인.
//   처리: 영어 모드일 때 codibank.js에서 글로벌 후처리로 일괄 정규화.
//          ① 풋바(.cb-nav-tab .nl) 라벨
//          ② 공통 한글 라벨이 그대로 남은 경우 매핑 (예: 'UV 높음' → 'UV High')
//   주의: 한국어 모드에선 동작 안 함. 페이지가 자체적으로 i18n.t() 처리한 부분은 건드리지 않음.
function _cbApplyGlobalEnLabels(){
  try{
    var en = window.CodiBankI18n && window.CodiBankI18n.isEn && window.CodiBankI18n.isEn();
    if(!en) return;
    
    var FOOTER_MAP = {
      '코디핏':'Codi Fit','코디 핏':'Codi Fit','Outfit핏':'Codi Fit','Outfit 핏':'Codi Fit','Codi 핏':'Codi Fit','Codissam':'Codi Fit',
      '트라이온':'Try-On','트라이 온':'Try-On','Try On':'Try-On',
      'Ai 옷장':'AI Closet','AI 옷장':'AI Closet','내옷장':'My Closet','내 옷장':'My Closet',
      '코디앨범':'Codi Album','코디 앨범':'Codi Album','Album':'Codi Album',
      'MY':'MY','마이':'MY','My':'MY',
    };
    document.querySelectorAll('.cb-nav-tab .nl').forEach(function(el){
      var cur = (el.textContent || '').trim();
      if(FOOTER_MAP[cur]) el.textContent = FOOTER_MAP[cur];
    });
    
    // ─── (v49) 광범위 한글 라벨 정규화 ───
    //   영어 모드에서 페이지가 자체 i18n으로 처리 못한 한글 잔존을 일괄 변환.
    //   정확 일치 + 자식 없는 텍스트 노드만 — 의도치 않은 변환 방지.
    var COMMON_MAP = {
      // ─── (v51) 코디핏 짬뽕 잔존 (한/영 혼용) — 어디서든 정확 일치 시 통일 ───
      '코디핏':'Codi Fit','코디 핏':'Codi Fit',
      'Outfit 핏':'Codi Fit','Outfit핏':'Codi Fit','Codi 핏':'Codi Fit',
      'Codissam':'Codi Fit',
      
      // 날씨/위치/UV
      'UV 높음':'UV High','UV 보통':'UV Mid','UV 낮음':'UV Low',
      '오늘':'Today','내일':'Tomorrow',
      '맑음':'Clear','구름많음':'Cloudy','흐림':'Overcast','비':'Rain','눈':'Snow','소나기':'Showers',
      '서울특별시':'Seoul','부산광역시':'Busan','대구광역시':'Daegu',
      '인천광역시':'Incheon','광주광역시':'Gwangju','대전광역시':'Daejeon',
      '울산광역시':'Ulsan','세종특별자치시':'Sejong',
      '경기도':'Gyeonggi','강원도':'Gangwon','충청북도':'Chungbuk','충청남도':'Chungnam',
      '전라북도':'Jeonbuk','전라남도':'Jeonnam','경상북도':'Gyeongbuk','경상남도':'Gyeongnam',
      '제주특별자치도':'Jeju',
      
      // 트라이온 페이지
      '트라이 온':'Try-On','트라이온':'Try-On',
      '이 옷이 어울릴까 고민하지 마세요. 3단계로 착장을 완성해요':'Wonder if it suits you? Complete your outfit in 3 steps.',
      'Step 1. 무엇을 입어볼까요?':'Step 1. What will you wear?',
      '상의 · 하의 · 아우터 · 신발을 선택하세요':'Choose top, bottom, outer, shoes',
      '상의 · 하의 · 신발':'Top · Bottom · Shoes',
      '상의 · 하의':'Top · Bottom',
      'Step 2. 누구의 핏을 보고 싶어요?':'Step 2. Whose fit?',
      'Step 3. 지금 입어볼까요?':'Step 3. Try it now?',
      '선택한 데이터를 종합해서 착장이미지를 만들어드립니다!':'AI combines your data to generate a styled image!',
      '이미지를 생성할 준비가 되었어요':'Ready to generate the image',
      '투피스':'Two-piece','원피스':'One-piece','아우터':'Outer',
      '상의':'Top','하의':'Bottom','신발':'Shoes',
      '옷장에서 선택':'Choose from closet',
      '내옷장':'My Closet','내 옷장':'My Closet',
      '필수':'Required','옵션':'Optional','선택':'Select',
      '마이 핏':'My Fit','썸바디':'Somebody','모델 핏':'Model Fit',
      '코디 프로필':'Codi Profile','코디 프로필이 비어있어요':'Codi Profile is empty',
      'AI가 개인화된 착장을 만드는 데 쓰여요':'Used by AI to personalize your styling',
      '촬영':'Camera',
      '성별':'Gender','나이대':'Age','키':'Height','몸무게':'Weight','수정':'Edit',
      '남성':'Male','여성':'Female',
      '트라이온 피팅':'Try-On Fit',
      '스니커즈 · 로퍼':'Sneakers · Loafers',
      '+ 신발':'+ Shoes','+ 아우터':'+ Outer','+ 상의':'+ Top','+ 하의':'+ Bottom',
      '트라이 온 1회 가능':'1 Try-On available',
      
      // 퍼스널 컬러 시즌 + 톤
      '가을 딥 웜톤':'Autumn Deep · Warm',
      '봄 라이트 웜톤':'Spring Light · Warm',
      '여름 라이트 쿨톤':'Summer Light · Cool',
      '겨울 딥 쿨톤':'Winter Deep · Cool',
      '봄':'Spring','여름':'Summer','가을':'Autumn','겨울':'Winter',
      '웜톤':'Warm','쿨톤':'Cool','뉴트럴':'Neutral',
      '따뜻한 브라운 · 머스타드 · 올리브 계열이 잘 어울려요':'Warm browns, mustards & olives suit you well',
      
      // 연령
      '20대':'20s','30대':'30s','40대':'40s','50대':'50s','60대':'60s','10대':'Teens',
      
      // mypage
      '구독 Plan':'Subscription Plan','사용량 OK · Plan 변경':'Usage · Change Plan',
      '사진 · 신체정보 · 퍼스널컬러':'Photo · Body Info · Personal Color',
      '사용량 확인 · 플랜 변경':'Check Usage · Change Plan',
      '사용자':'User','게스트':'Guest','없음':'None',
      '회원가입':'Sign Up','로그인':'Log In','로그아웃':'Log Out',
      
      // closet 위치/날짜
      'Choose outfit goal':'Choose outfit goal',  // 이미 영어
    };
    
    // 정확 일치 + 자식 없는 텍스트 노드만 (안전)
    var sels = ['div','span','p','h1','h2','h3','h4','button','label','a','b','strong','em','small'];
    document.querySelectorAll(sels.join(',')).forEach(function(el){
      if(el.children.length > 0) return;
      var cur = (el.textContent || '').trim();
      if(COMMON_MAP[cur]) el.textContent = COMMON_MAP[cur];
    });
    
    // 날짜 형식: "2026년 5Mon" → "May 2026" (혼용 패턴)
    var monMap = {'1Mon':'January','2Mon':'February','3Mon':'March','4Mon':'April',
                  '5Mon':'May','6Mon':'June','7Mon':'July','8Mon':'August',
                  '9Mon':'September','10Mon':'October','11Mon':'November','12Mon':'December'};
    document.querySelectorAll(sels.join(',')).forEach(function(el){
      if(el.children.length > 0) return;
      var cur = (el.textContent || '').trim();
      // "2026년 5Mon" 또는 "년 5Mon" 패턴
      var m = cur.match(/^(\d{4})년\s+(\d{1,2}Mon)$/);
      if(m && monMap[m[2]]){ el.textContent = monMap[m[2]] + ' ' + m[1]; return; }
      // "2026.05.10 (Sun)"은 그대로 유지 (이미 영어 친화)
    });
    
    // title 변환
    var titleMap = {'트라이 온 — CodiBank':'Try-On — CodiBank','트라이온 — CodiBank':'Try-On — CodiBank'};
    if(titleMap[document.title]) document.title = titleMap[document.title];
  }catch(_){}
}
(function _cbAutoApplyEnLabels(){
  function _run(){
    try{ _cbApplyGlobalEnLabels(); }catch(_){}
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){
      setTimeout(_run, 50);  // 페이지 자체 i18n 적용 직후
      setTimeout(_run, 500); // 동적 렌더링(예: 위치/날씨) 이후 한 번 더
      setTimeout(_run, 1500); // ─── (v50) 추가: 더 늦은 동적 렌더링용
      setTimeout(_run, 3000); // ─── (v50) 추가: 가장 늦은 콘텐츠
    });
  } else {
    setTimeout(_run, 50);
    setTimeout(_run, 500);
    setTimeout(_run, 1500);
    setTimeout(_run, 3000);
  }
  
  // ─── 2026-05-09 KST · TJ 지시 (v50) ─── MutationObserver로 동적 DOM 정규화 ───
  //   배경: tryon.html / closet.html 등의 동적 렌더링은 setTimeout보다 늦게 실행될 수 있음.
  //          DOM에 새 노드 추가될 때마다 자동 정규화 실행.
  //   안전: throttle로 과도 호출 방지 (200ms 디바운스).
  function _initObserver(){
    try{
      var en = window.CodiBankI18n && window.CodiBankI18n.isEn && window.CodiBankI18n.isEn();
      if(!en) return; // 한국어 모드는 observer 불필요
      var _throttleTimer = null;
      var observer = new MutationObserver(function(mutations){
        // 새 노드 추가 또는 텍스트 변경 감지
        var hasChange = false;
        for(var i = 0; i < mutations.length; i++){
          var m = mutations[i];
          if(m.type === 'childList' && m.addedNodes.length > 0){ hasChange = true; break; }
          if(m.type === 'characterData'){ hasChange = true; break; }
        }
        if(!hasChange) return;
        if(_throttleTimer) return; // 이미 처리 예약됨
        _throttleTimer = setTimeout(function(){
          _throttleTimer = null;
          try{ _cbApplyGlobalEnLabels(); }catch(_){}
        }, 200);
      });
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true,
      });
    }catch(_){}
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', _initObserver);
  } else {
    _initObserver();
  }
})();


// ═══════════════════════════════════════════════════════════════════════
// ─── 2026-09-24 KST · TJ 지시 ─── 서비스 이용 동의 (가입 · 기존회원 재동의) ───
//   · 필수: 만 14세 이상 / 이용약관 / 개인정보 수집·이용 / 신체데이터(사진·신체사이즈) 이용 / 국외 이전
//   · 선택: 서비스 개선 활용
//   · 신체데이터 동의는 전문을 체크박스 바로 아래에 펼쳐서 표시 (나중에 "못 봤다" 는 다툼 방지)
//   · 기록: Supabase user_metadata.consent {v, at, items} + 서버 /api/consent/log (시각·UA·IP)
//   · 기존 회원: 로그인 페이지 진입 시 consent.v 가 현재 버전보다 낮으면 동의 시트 표시 (필수 미동의 시 이용 불가)
//   · 사용처: signup.html STEP1 (CodiBankConsent.build), 전 페이지 자동(ensure), mypage 동의관리(openManage)
// ═══════════════════════════════════════════════════════════════════════
(function _cbConsentModule(){
  var VERSION = '2026-09-24';
  function _en(){ try{ return !!(window.CodiBankI18n && (CodiBankI18n.isForeign ? CodiBankI18n.isForeign() : CodiBankI18n.isEn())); }catch(_){ return false; } }
  function T(ko, en){ return _en() ? en : ko; }
  var BODY_KO = '스타일몬스터의 착장 서비스(코디핏·트라이온·AI옷장)를 이용하기 위해 본인이 제공하는 신체데이터(얼굴·전신 사진, 키·몸무게·체형·신체 사이즈, 퍼스널컬러 등)를 스타일몬스터가 수집하여 착장 이미지 생성, 체형 분석, 맞춤 코디 추천에 사용·응용·분석하는 것에 동의합니다. 신체데이터는 위 목적 외에는 사용하지 않으며, 마이페이지에서 언제든 삭제할 수 있고 회원 탈퇴 시 지체 없이 파기합니다. 동의하지 않으면 착장 이미지 생성 등 핵심 기능을 이용할 수 없습니다.';
  var BODY_EN = 'To use Stylemonster\'s outfit services (Codi Fit, Try-On, AI Closet), I agree that Stylemonster collects the body data I provide (face and full-body photos, height, weight, body type and measurements, personal color, etc.) and uses, applies and analyzes it to generate outfit images, analyze body type and recommend outfits. Body data is not used for any other purpose, can be deleted at any time in My Page, and is destroyed without delay when I delete my account. Without this consent, core features such as outfit image generation are unavailable.';
  var OVERSEAS_KO = '사진·신체데이터·생성 이미지는 AI 이미지 생성과 저장을 위해 Google LLC(미국), OpenAI(미국), BytePlus(싱가포르), Cloudflare(미국), Supabase(미국), Render(싱가포르)로 서비스 이용 시점에 암호화 전송되어 처리·보관됩니다. 자세한 내용은 개인정보처리방침 제5조를 확인하세요.';
  var OVERSEAS_EN = 'Photos, body data and generated images are transferred (encrypted) at the time of use to Google LLC (USA), OpenAI (USA), BytePlus (Singapore), Cloudflare (USA), Supabase (USA) and Render (Singapore) for AI image generation and storage. See Article 5 of the Privacy Policy.';
  var IMPROVE_KO = '생성된 착장 이미지와 신체데이터를 개인을 알아볼 수 없도록 처리한 뒤 추천 품질 개선·통계 분석에 활용하는 데 동의합니다. 동의하지 않아도 서비스 이용에는 제한이 없습니다.';
  var IMPROVE_EN = 'I agree that generated outfit images and body data may be de-identified and used to improve recommendations and for statistics. Declining does not limit the service.';
  var ITEMS = [
    { key:'age14',    req:true,  ko:'만 14세 이상입니다',                      en:'I am 14 years of age or older' },
    { key:'terms',    req:true,  ko:'이용약관 동의',                            en:'Terms of Service',                         link:'terms.html' },
    { key:'privacy',  req:true,  ko:'개인정보 수집·이용 동의',                   en:'Collection & use of personal information',  link:'privacy.html' },
    { key:'body',     req:true,  ko:'신체데이터(사진·신체사이즈) 이용 동의',      en:'Use of body data (photos & measurements)', detailKo:BODY_KO, detailEn:BODY_EN, open:true },
    { key:'overseas', req:true,  ko:'개인정보 국외 이전 동의',                   en:'Overseas transfer of personal information', detailKo:OVERSEAS_KO, detailEn:OVERSEAS_EN },
    { key:'improve',  req:false, ko:'서비스 개선 활용 동의',                     en:'Use for service improvement',              detailKo:IMPROVE_KO, detailEn:IMPROVE_EN },
  ];
  function _css(){
    if(document.getElementById('cbcStyle')) return;
    var st = document.createElement('style'); st.id = 'cbcStyle';
    st.textContent = ''
      + '.cbc{display:flex;flex-direction:column;gap:2px;text-align:left;font-family:inherit;}'
      + '.cbc-all{display:flex;align-items:center;gap:10px;padding:13px 14px;border-radius:14px;background:rgba(151,254,237,.08);border:1.5px solid rgba(151,254,237,.28);cursor:pointer;margin-bottom:6px;}'
      + '.cbc-all b{font-size:15px;font-weight:800;color:#fff;}'
      + '.cbc-row{display:flex;align-items:flex-start;gap:10px;padding:9px 4px;}'
      + '.cbc-row label{flex:1;font-size:13px;color:rgba(255,255,255,.82);line-height:1.5;cursor:pointer;}'
      + '.cbc-tag{font-weight:800;margin-right:4px;}.cbc-req{color:#97FEED;}.cbc-opt{color:rgba(255,255,255,.45);}'
      + '.cbc-link{flex-shrink:0;font-size:12px;color:rgba(151,254,237,.8);text-decoration:underline;background:none;border:none;cursor:pointer;padding:2px 0;font-family:inherit;}'
      + '.cbc-box{appearance:none;-webkit-appearance:none;flex-shrink:0;width:20px;height:20px;border-radius:6px;border:1.5px solid rgba(255,255,255,.35);background:rgba(255,255,255,.04);cursor:pointer;margin-top:1px;position:relative;}'
      + '.cbc-box:checked{background:#35A29F;border-color:#97FEED;}'
      + '.cbc-box:checked::after{content:"";position:absolute;left:6px;top:2px;width:5px;height:10px;border:solid #fff;border-width:0 2px 2px 0;transform:rotate(45deg);}'
      + '.cbc-detail{margin:0 4px 6px 34px;padding:10px 12px;border-radius:10px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);font-size:12px;line-height:1.65;color:rgba(255,255,255,.66);}'
      + '.cbc-detail.hide{display:none;}'
      + '.cbc-sheet-bg{position:fixed;inset:0;z-index:2147483000;background:rgba(0,2,46,.72);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);display:flex;align-items:flex-end;justify-content:center;}'
      + '.cbc-sheet{width:100%;max-width:480px;max-height:92dvh;overflow:auto;background:#00022E;border:1px solid rgba(151,254,237,.22);border-bottom:none;border-radius:24px 24px 0 0;padding:22px 18px calc(18px + env(safe-area-inset-bottom));color:#fff;font-family:"Pretendard","Noto Sans KR",sans-serif;}'
      + '.cbc-sheet h3{font-size:18px;font-weight:800;margin-bottom:6px;}'
      + '.cbc-sheet .cbc-sub{font-size:12.5px;color:rgba(255,255,255,.55);line-height:1.6;margin-bottom:14px;}'
      + '.cbc-btn{width:100%;padding:15px;border:none;border-radius:14px;background:linear-gradient(135deg,#0B666A,#35A29F);color:#fff;font-size:16px;font-weight:800;cursor:pointer;font-family:inherit;margin-top:12px;}'
      + '.cbc-btn:disabled{opacity:.4;cursor:not-allowed;}'
      + '.cbc-foot{display:flex;justify-content:center;gap:18px;margin-top:12px;}'
      + '.cbc-foot button{background:none;border:none;color:rgba(255,255,255,.45);font-size:12px;text-decoration:underline;cursor:pointer;font-family:inherit;}'
      + '.cbc-err{color:#ff8a8a;font-size:12px;margin-top:8px;min-height:1em;}';
    (document.head || document.documentElement).appendChild(st);
  }
  function _esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(m){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]; }); }
  // 대부분의 페이지는 Supabase SDK 를 싣지 않음(로컬 캐시 기반) → 동의 저장·탈퇴에 필요할 때만 지연 로드
  var SDK_URL = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js';
  var _sdkP = null;
  function _loadSdk(){
    if(window.supabase && window.supabase.createClient) return Promise.resolve(true);
    if(_sdkP) return _sdkP;
    _sdkP = new Promise(function(res){
      var done = false; function fin(v){ if(done) return; done = true; if(!v) _sdkP = null; res(v); }
      var sc = document.createElement('script'); sc.src = SDK_URL; sc.async = true;
      sc.onload = function(){ fin(!!(window.supabase && window.supabase.createClient)); };
      sc.onerror = function(){ fin(false); };
      (document.head || document.documentElement).appendChild(sc);
      setTimeout(function(){ fin(!!(window.supabase && window.supabase.createClient)); }, 12000);
    });
    return _sdkP;
  }
  async function client(){
    var c = window.CodiBank && CodiBank.getSupabaseClient && CodiBank.getSupabaseClient();
    if(c) return c;
    await _loadSdk();
    return (window.CodiBank && CodiBank.getSupabaseClient && CodiBank.getSupabaseClient()) || null;
  }
  function _remember(u, snap){
    try{
      if(!u || !snap) return;
      u.consent = snap;
      try{ localStorage.setItem('cb_consent_' + String(u.email||'').toLowerCase(), JSON.stringify(snap)); }catch(_){}
      try{ var all = JSON.parse(localStorage.getItem('codibank_users') || '{}'); var k = String(u.email||'').toLowerCase(); if(all[k]){ all[k].consent = snap; localStorage.setItem('codibank_users', JSON.stringify(all)); } }catch(_){}
    }catch(_){}
  }
  // container 에 동의 UI 를 그림 → { isValid, values, setAll, onChange }
  function build(container, opts){
    opts = opts || {};
    _css();
    var init = opts.values || {};
    var uid = 'cbc' + Math.random().toString(36).slice(2, 8);
    var html = '<div class="cbc">'
      + '<label class="cbc-all" for="' + uid + '_all"><input type="checkbox" class="cbc-box" id="' + uid + '_all"><b>' + _esc(T('전체 동의','Agree to all')) + '</b></label>';
    ITEMS.forEach(function(it){
      var id = uid + '_' + it.key;
      var detail = _en() ? it.detailEn : it.detailKo;
      html += '<div class="cbc-row">'
        + '<input type="checkbox" class="cbc-box" id="' + id + '" data-key="' + it.key + '"' + (init[it.key] ? ' checked' : '') + '>'
        + '<label for="' + id + '"><span class="cbc-tag ' + (it.req ? 'cbc-req' : 'cbc-opt') + '">[' + _esc(it.req ? T('필수','Required') : T('선택','Optional')) + ']</span>' + _esc(_en() ? it.en : it.ko) + '</label>'
        + (it.link ? '<a class="cbc-link" href="' + it.link + '" target="_blank" rel="noopener">' + _esc(T('보기','View')) + '</a>'
           : (detail && !it.open ? '<button type="button" class="cbc-link" data-toggle="' + id + '_d">' + _esc(T('보기','View')) + '</button>' : ''))
        + '</div>'
        + (detail ? '<div class="cbc-detail' + (it.open ? '' : ' hide') + '" id="' + id + '_d">' + _esc(detail) + '</div>' : '');
    });
    html += '</div>';
    container.innerHTML = html;
    var all = container.querySelector('#' + uid + '_all');
    var boxes = Array.prototype.slice.call(container.querySelectorAll('input[data-key]'));
    var listeners = [];
    function values(){ var v = {}; boxes.forEach(function(b){ v[b.getAttribute('data-key')] = !!b.checked; }); return v; }
    function isValid(){ var v = values(); return ITEMS.every(function(it){ return !it.req || v[it.key]; }); }
    function sync(){ all.checked = boxes.every(function(b){ return b.checked; }); listeners.forEach(function(fn){ try{ fn(isValid(), values()); }catch(_){} }); }
    all.addEventListener('change', function(){ boxes.forEach(function(b){ b.checked = all.checked; }); sync(); });
    boxes.forEach(function(b){ b.addEventListener('change', sync); });
    Array.prototype.forEach.call(container.querySelectorAll('[data-toggle]'), function(btn){
      btn.addEventListener('click', function(){ var d = document.getElementById(btn.getAttribute('data-toggle')); if(d) d.classList.toggle('hide'); });
    });
    all.checked = boxes.every(function(b){ return b.checked; });
    return {
      isValid: isValid, values: values,
      onChange: function(fn){ listeners.push(fn); try{ fn(isValid(), values()); }catch(_){} },
      setAll: function(on){ all.checked = !!on; boxes.forEach(function(b){ b.checked = !!on; }); sync(); },
    };
  }
  function snapshot(vals){
    var items = {}; ITEMS.forEach(function(it){ items[it.key] = !!(vals && vals[it.key]); });
    return { v: VERSION, at: new Date().toISOString(), items: items };
  }
  function hasValid(user){
    try{
      var c = user && user.consent;
      if(!c || String(c.v || '') < VERSION) return false;
      return ITEMS.every(function(it){ return !it.req || (c.items && c.items[it.key]); });
    }catch(_){ return false; }
  }
  async function _token(){
    try{
      var sb = await client();
      if(!sb) return '';
      var r = await sb.auth.getSession();
      return (r && r.data && r.data.session && r.data.session.access_token) || '';
    }catch(_){ return ''; }
  }
  // 서버 동의 기록 (실패해도 가입·이용은 막지 않음)
  async function log(vals, source, email){
    try{
      var base = (window.CODIBANK_CONFIG && window.CODIBANK_CONFIG.backendBase) || 'https://codibank-api.onrender.com';
      var tok = await _token();
      var h = { 'Content-Type':'application/json' }; if(tok) h['Authorization'] = 'Bearer ' + tok;
      await fetch(base + '/api/consent/log', { method:'POST', headers:h, keepalive:true,
        body: JSON.stringify({ email: String(email || '').trim().toLowerCase(), version: VERSION, items: snapshot(vals).items, source: source || '' }) });
    }catch(_){}
  }
  // 로그인 사용자의 동의를 Supabase user_metadata 에 저장
  async function save(vals, source){
    var snap = snapshot(vals);
    var sb = await client();
    if(!sb) throw new Error('supabase_unavailable');
    var r = await sb.auth.updateUser({ data: { consent: snap } });
    if(r && r.error) throw r.error;
    try{
      var u = CodiBank.getCurrentUser && CodiBank.getCurrentUser();
      _remember(u, snap);
      log(vals, source || 'reconsent', u && u.email);
    }catch(_){}
    return snap;
  }
  function _sheet(opts){
    _css();
    var old = document.getElementById('cbcSheet'); if(old) old.remove();
    var bg = document.createElement('div'); bg.className = 'cbc-sheet-bg'; bg.id = 'cbcSheet';
    bg.innerHTML = '<div class="cbc-sheet" role="dialog" aria-modal="true">'
      + '<h3>' + _esc(opts.title) + '</h3><p class="cbc-sub">' + _esc(opts.sub) + '</p>'
      + '<div id="cbcSheetBox"></div><p class="cbc-err" id="cbcSheetErr"></p>'
      + '<button type="button" class="cbc-btn" id="cbcSheetOk">' + _esc(opts.okLabel) + '</button>'
      + (opts.foot ? '<div class="cbc-foot">' + opts.foot + '</div>' : '')
      + '</div>';
    document.body.appendChild(bg);
    var ui = build(document.getElementById('cbcSheetBox'), { values: opts.values || {} });
    var ok = document.getElementById('cbcSheetOk');
    ui.onChange(function(valid){ ok.disabled = !valid; });
    return { bg: bg, ui: ui, ok: ok, err: document.getElementById('cbcSheetErr') };
  }
  // 기존 회원 재동의 — 필수 항목 미동의면 서비스 이용 불가 (로그아웃·탈퇴 경로 제공)
  var _ensuring = false;
  async function ensure(){
    if(_ensuring) return true;
    try{
      var p = (location.pathname || '').toLowerCase();
      if(/(login|signup|terms|privacy|refund|withdraw|admin)\.html/.test(p)) return true;
      var u = window.CodiBank && CodiBank.getCurrentUser && CodiBank.getCurrentUser();
      if(!u || !u.email) return true;
      if(hasValid(u)) return true;
      try{ var loc = JSON.parse(localStorage.getItem('cb_consent_' + String(u.email).toLowerCase()) || 'null'); if(hasValid({ consent: loc })) return true; }catch(_){}
      _ensuring = true;
      // 다른 기기에서 이미 동의했을 수 있으므로 서버(Supabase)의 최신 동의 기록을 먼저 확인
      var sb = await client();
      if(!sb){ _ensuring = false; return true; }            // SDK 로드 실패 → 이번엔 건너뜀(다음 진입 때 재시도)
      try{
        var gu = await sb.auth.getUser();
        var fu = gu && gu.data && gu.data.user;
        if(!fu){ _ensuring = false; return true; }          // 세션 없음 → 저장 불가, 로그인 후 재시도
        var fc = (fu.user_metadata || {}).consent;
        if(hasValid({ consent: fc })){ _remember(u, fc); _ensuring = false; return true; }
      }catch(_){ _ensuring = false; return true; }
      var s = _sheet({
        title: T('서비스 이용 동의 안내', 'Please review our updated terms'),
        sub: T('개인정보 보호를 강화하기 위해 이용약관과 개인정보처리방침이 개정되었어요 (시행 2026.10.01). 계속 이용하시려면 아래 항목에 동의해 주세요.',
               'We updated our Terms and Privacy Policy to better protect your data (effective Oct 1, 2026). Please agree to continue.'),
        okLabel: T('동의하고 계속하기', 'Agree and continue'),
        values: (u.consent && u.consent.items) || {},
        foot: '<button type="button" id="cbcLogout">' + _esc(T('로그아웃','Log out')) + '</button><button type="button" id="cbcWithdraw">' + _esc(T('회원탈퇴','Delete account')) + '</button>',
      });
      document.getElementById('cbcLogout').onclick = async function(){ try{ if(CodiBank.logout) await CodiBank.logout(); }catch(_){} location.replace('login.html'); };
      document.getElementById('cbcWithdraw').onclick = function(){ location.href = 'withdraw.html'; };
      return await new Promise(function(resolve){
        s.ok.onclick = async function(){
          s.ok.disabled = true; s.err.textContent = '';
          try{ await save(s.ui.values(), 'reconsent'); s.bg.remove(); _ensuring = false; resolve(true); }
          catch(e){ s.ok.disabled = false; s.err.textContent = T('저장하지 못했어요. 네트워크를 확인한 뒤 다시 눌러주세요.', 'Could not save. Check your connection and try again.'); }
        };
      });
    }catch(e){ _ensuring = false; return true; }
  }
  // 마이페이지 동의 관리 — 선택 동의 변경 · 필수 동의 확인
  function openManage(){
    var u = window.CodiBank && CodiBank.getCurrentUser && CodiBank.getCurrentUser();
    if(!u){ location.href = 'login.html'; return; }
    var s = _sheet({
      title: T('동의 관리', 'Manage consent'),
      sub: T('필수 항목 동의를 철회하시려면 회원탈퇴를 이용해 주세요. 얼굴 사진·신체정보는 프로필에서 언제든 삭제할 수 있어요.',
             'To withdraw required consent, please delete your account. You can delete your face photo and body info anytime in Profile.'),
      okLabel: T('저장', 'Save'),
      values: (u.consent && u.consent.items) || {},
      foot: '<button type="button" id="cbcClose">' + _esc(T('닫기','Close')) + '</button><button type="button" id="cbcProfile">' + _esc(T('사진·신체정보 삭제','Delete photo & body info')) + '</button><button type="button" id="cbcWithdraw2">' + _esc(T('회원탈퇴','Delete account')) + '</button>',
    });
    document.getElementById('cbcClose').onclick = function(){ s.bg.remove(); };
    document.getElementById('cbcProfile').onclick = function(){ location.href = 'profile.html'; };
    document.getElementById('cbcWithdraw2').onclick = function(){ location.href = 'withdraw.html'; };
    s.ok.onclick = async function(){
      s.ok.disabled = true; s.err.textContent = '';
      try{ await save(s.ui.values(), 'mypage'); s.bg.remove(); try{ alert(T('저장했어요.', 'Saved.')); }catch(_){} }
      catch(e){ s.ok.disabled = false; s.err.textContent = T('저장하지 못했어요. 다시 시도해주세요.', 'Could not save. Please try again.'); }
    };
  }
  window.CodiBankConsent = { VERSION: VERSION, ITEMS: ITEMS, build: build, snapshot: snapshot, hasValid: hasValid, log: log, save: save, ensure: ensure, openManage: openManage, client: client, token: _token };
})();
