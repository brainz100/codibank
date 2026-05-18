/* ══════════════════════════════════════════
   CodiBank Service Worker
   ─── 2026-05-18 KST · TJ 지시 (구버전 캐시 서빙 버그 수정) ───
   변경:
     1) CACHE_NAME 버전 bump (codibank-v1 → 날짜 기반)
        → SW 파일 내용이 바뀌어야 브라우저가 새 SW 로 교체.
          activate 시 옛 캐시(codibank-v1 등) 전부 자동 삭제.
     2) APP_SHELL 에서 HTML 전부 제거
        → closet.html 등 자주 바뀌는 HTML 을 프리캐시하면,
          network-first 라도 네트워크 지연/실패 시 박제된 구버전이 폴백됨.
          HTML 은 프리캐시하지 않고 런타임 network-first 로만 처리.
     3) HTML 요청은 항상 network-first — 성공 시 캐시 갱신,
        실패(오프라인) 시에만 캐시 → offline.html.
   ※ SW 를 갱신할 때는 반드시 아래 CACHE_NAME 의 날짜/접미문자를 변경할 것.
══════════════════════════════════════════ */
const CACHE_NAME = 'codibank-2026-05-18a';

// HTML 은 제외 — JS / 오프라인 페이지만 프리캐시 (자주 바뀌지 않는 자원)
const APP_SHELL = [
  '/app/codibank.js',
  '/app/i18n.js',
  '/app/config.js',
  '/app/offline.html',
];

// Install: 앱 셸 프리캐시 (HTML 제외)
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching app shell:', CACHE_NAME);
      return cache.addAll(APP_SHELL).catch((err) => {
        console.warn('[SW] Some resources failed to cache:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activate: 오래된 캐시 정리 (codibank-v1 등 이전 버전 전부 삭제)
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) => {
      return Promise.all(
        names
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

// HTML 요청 판별 (네비게이션 또는 Accept: text/html)
function _isHtmlRequest(request) {
  if (request.mode === 'navigate') return true;
  const accept = request.headers.get('accept') || '';
  return accept.includes('text/html');
}

// Fetch: HTML = 항상 network-first / 그 외 = 기존 전략
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API 요청은 캐시하지 않음
  if (url.pathname.startsWith('/api/') || url.hostname.includes('onrender.com')) {
    return;
  }

  // ─── HTML: 항상 네트워크 우선 (캐시에 박제 금지) ───
  //   배포 즉시 최신 closet.html 등이 반영되도록.
  //   네트워크 실패(오프라인) 시에만 캐시 → 없으면 offline.html.
  if (url.origin === location.origin && _isHtmlRequest(event.request)) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          return caches.match(event.request).then((cached) => {
            return cached || caches.match('/app/offline.html');
          });
        })
    );
    return;
  }

  // 외부 리소스(폰트, CDN)는 캐시 우선
  if (url.origin !== location.origin) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        return cached || fetch(event.request).then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        }).catch(() => cached);
      })
    );
    return;
  }

  // 그 외 동일 출처 자원(JS 등): 네트워크 우선 → 캐시 폴백
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cached) => {
          if (cached) return cached;
          return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
        });
      })
  );
});
