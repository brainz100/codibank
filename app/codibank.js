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
    return {
      email:            sbUser.email || '',
      gender:           m.gender     || '',
      ageGroup:         m.ageGroup   || '',
      height:           m.height     || '',
      weight:           m.weight     || '',
      location:         m.location   || '',
      nickname:         m.nickname   || m.name || '',
      avatarFace:       m.avatarFace || '',
      plan:             m.plan       || 'FREE',
      categories:       m.categories || DEFAULT_CATEGORIES.map((c) => c.key),
      customCategories: m.customCategories || [],
      createdAt:        sbUser.created_at  || nowIso(),
      updatedAt:        m.updatedAt  || nowIso(),
      sbId:             sbUser.id,
    };
  }

  // ✅ 기본 카테고리(옷장 페이지 기준 고정 순서)
  // 코트, 자켓, 탑, 바지, 양말, 구두, 시계, 스카프, 기타
  const DEFAULT_CATEGORIES = [
    { key: 'coat', label: '코트' },
    { key: 'jacket', label: '자켓' },
    { key: 'top', label: '탑/셔츠/블라우스' },
    { key: 'pants', label: '바지/스커트' },
    { key: 'socks', label: '양말' },
    { key: 'shoes', label: '구두/운동화' },
    { key: 'watch', label: '시계' },
    { key: 'scarf', label: '스카프/목도리' },
    { key: 'etc', label: '기타' },
  ];

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
    localStorage.removeItem(KEYS.SESSION);
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
  function requireAuth(redirectTo) {
    const to = redirectTo || 'login.html';
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
          window.location.replace(to);
        }
      }).catch(() => window.location.replace(to));
    } else {
      window.location.replace(to);
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
      const key = String(it.categoryKey || '');
      if (!allowedSet.has(key)) {
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
    const k = String(key || '');
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
    return u.categories.map((k) => getCategoryMetaByKey(k, email));
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
    return getItemsByUser(email).filter((it) => it.categoryKey === categoryKey);
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

    const categoryKey = item.categoryKey;

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
      meta: item.meta || {},
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
    const nextCategory = (patch && patch.categoryKey !== undefined) ? String(patch.categoryKey || '') : String(before.categoryKey || '');
    if (nextCategory && nextCategory !== String(before.categoryKey || '')) {
      next.categoryKey = nextCategory;
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
      const { data, error } = await sb.auth.signUp({
        email,
        password: String(payload.password),   // Supabase Auth 파라미터 (meta에는 저장 안 함)
        options: { data: meta },
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
    // v17
    // - "오늘/내일" 코디 추천을 위해 2일 예보까지 가져옵니다.
    // - daily(최고/최저/날씨코드)는 내일의 대표값(평균 온도+요약 코드) 계산에 사용합니다.
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${encodeURIComponent(lat)}&longitude=${encodeURIComponent(lon)}&current=temperature_2m,weather_code,is_day&hourly=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,weather_code&forecast_days=14&timezone=${encodeURIComponent(tz)}`;
    return fetchJsonWithTimeout(url, timeoutMs);
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
      // 1) Supabase 로그아웃 (세션 제거)
      const sb = _getSupabase();
      if (sb) await sb.auth.signOut();
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

      // 3) 서버 경유 Supabase 계정 삭제 (service_role 필요 → 백엔드 API)
      try {
        const base = (window.CODIBANK_CONFIG && window.CODIBANK_CONFIG.backendBase) || '';
        if (base) await fetch(base + '/api/user/delete', { method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: e }) });
      } catch (_) {}

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
      'item.html': 'closet.html',
      'camera.html': 'camera.html',
      'closet.html': 'closet.html',
      'album.html': 'album.html',
      'share-sale.html': 'share-sale.html',
      'share.html': 'share-sale.html',    // 레거시 페이지도 공유판매 탭으로
      'sale.html': 'share-sale.html',     // 레거시 페이지도 공유판매 탭으로
      'share-item.html': 'share-sale.html',
      'sale-item.html': 'share-sale.html',
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

window.CodiBank = {
    // config
    getConfig,
    getBackendBaseResolved,

    DEFAULT_CATEGORIES,
    OPTIONAL_CATEGORIES,
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
    clearImageSrcCache,

    // location & weather
    getSmartLocation,
    getWeatherByCoords,
    weatherCodeToKorean,
  };
})();
