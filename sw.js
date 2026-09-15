/* ─── 2026-09-09 KST · TJ 지시 ─── Stylemonster Service Worker (Web Push 전용)
   배포 위치: 사이트 루트 /sw.js  (scope '/' 필요 — /app/ 하위에 두면 scope 제한으로 등록 실패)
   역할: ① 푸시 수신 → 알림 표시  ② 알림 클릭 → aicloset.html?alarm=<id> 열기 (열려있으면 포커스+메시지)
   주의: 캐싱/오프라인 기능은 넣지 않았습니다 (PWA 캐시 정책은 별도 결정 사항). */
self.addEventListener('install', function(){ self.skipWaiting(); });
/* ─── 2026-09-10 KST · TJ 지시 ─── 활성화 시 이전 서비스워커가 남긴 캐시 전부 삭제
   (구 pwa-register.js 가 index.html/manifest.json/아이콘을 캐시해 두면 리브랜딩 후에도
    'CodiBank' 아이콘·텍스트 스플래시가 계속 보이는 원인이 됨) */
self.addEventListener('activate', function(e){
  e.waitUntil((async function(){
    try { var keys = await caches.keys(); await Promise.all(keys.map(function(k){ return caches.delete(k); })); } catch(_) {}
    await self.clients.claim();
  })());
});

/* ─── 2026-09-15 KST · TJ 지시 ─── 앱 아이콘 배지 = 알림창에 남아 있는 스타일몬스터 알림 수
   알림 표시·클릭·닫기 때마다 다시 계산 → 사용자가 결과를 확인(알림 닫힘)하면 숫자가 줄어듦 */
function _syncBadge(){
  return self.registration.getNotifications().then(function(list){
    var n = (list || []).filter(function(x){ return String(x.tag || '').indexOf('sm-alarm-') === 0; }).length;
    if (!('setAppBadge' in self.navigator)) return;
    return (n > 0 ? self.navigator.setAppBadge(n) : self.navigator.clearAppBadge()).catch(function(){});
  }).catch(function(){});
}

self.addEventListener('push', function(event){
  var data = {};
  try { data = event.data ? event.data.json() : {}; } catch(_) { data = { body: event.data ? event.data.text() : '' }; }
  var title = data.title || 'Stylemonster';
  var opts = {
    body: data.body || '',
    icon: '/app/icons/icon-192.png',
    badge: '/app/icons/favicon-32.png',
    image: data.image || undefined,
    tag: 'sm-alarm-' + (data.alarmId || 'x'),
    renotify: true,
    data: { url: data.url || '/app/aicloset.html', alarmId: data.alarmId || '' }
  };
  event.waitUntil(self.registration.showNotification(title, opts).then(_syncBadge));
});

self.addEventListener('notificationclose', function(event){ event.waitUntil(_syncBadge()); });

self.addEventListener('notificationclick', function(event){
  event.notification.close();
  var d = (event.notification && event.notification.data) || {};
  var target = new URL(d.url || '/app/aicloset.html', self.location.origin).href;
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(list){
      for (var i = 0; i < list.length; i++) {
        var c = list[i];
        if (c.url && c.url.indexOf('/aicloset.html') >= 0 && 'focus' in c) {
          try { c.postMessage({ type: 'sm_open_alarm', id: d.alarmId || '' }); } catch(_) {}
          return c.focus();
        }
      }
      return self.clients.openWindow(target);
    }).then(_syncBadge)
  );
});
