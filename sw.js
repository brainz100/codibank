/* ══════════════════════════════════════════
   CodiBank Service Worker v1.0
   - 앱 셸 캐싱 (HTML, CSS, JS, 폰트)
   - 네트워크 우선 + 캐시 폴백 전략
   - 오프라인 기본 페이지 제공
══════════════════════════════════════════ */

const CACHE_NAME = 'codibank-v1';
const APP_SHELL = [
  '/app/closet.html',
  '/app/album.html',
  '/app/camera.html',
  '/app/codistyle.html',
  '/app/mypage.html',
  '/app/profile.html',
  '/app/login.html',
  '/app/signup.html',
  '/app/codibank.js',
  '/app/i18n.js',
  '/app/config.js',
  '/app/offline.html',
];

// Install: 앱 셸 프리캐시
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching app shell');
      return cache.addAll(APP_SHELL).catch((err) => {
        console.warn('[SW] Some resources failed to cache:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activate: 오래된 캐시 정리
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) => {
      return Promise.all(
        names
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch: 네트워크 우선, 캐시 폴백
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API 요청은 캐시하지 않음
  if (url.pathname.startsWith('/api/') || url.hostname.includes('onrender.com')) {
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

  // 앱 리소스: 네트워크 우선 → 캐시 폴백 → 오프라인 페이지
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
          // HTML 요청인 경우 오프라인 페이지 표시
          if (event.request.headers.get('accept')?.includes('text/html')) {
            return caches.match('/app/offline.html');
          }
          return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
        });
      })
  );
});
