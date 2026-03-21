/* ══════════════════════════════════════════
   CodiBank PWA Registration
   - Service Worker 등록
   - 홈화면 추가(A2HS) 배너 표시
══════════════════════════════════════════ */
(function(){
'use strict';

// Service Worker 등록
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then(function(reg) {
        console.log('[PWA] SW registered, scope:', reg.scope);
        // 자동 업데이트 체크 (1시간마다)
        setInterval(function() { reg.update(); }, 3600000);
      })
      .catch(function(err) {
        console.warn('[PWA] SW registration failed:', err);
      });
  });
}

// "홈화면에 추가" 프롬프트 캡처
var _deferredPrompt = null;

window.addEventListener('beforeinstallprompt', function(e) {
  e.preventDefault();
  _deferredPrompt = e;
  showInstallBanner();
});

// 이미 설치된 경우 감지
window.addEventListener('appinstalled', function() {
  _deferredPrompt = null;
  hideInstallBanner();
  console.log('[PWA] App installed');
});

// 설치 배너 표시
function showInstallBanner() {
  // 이미 닫은 적 있으면 24시간 동안 안 보여줌
  var dismissed = localStorage.getItem('cb_pwa_dismissed');
  if (dismissed && (Date.now() - Number(dismissed)) < 86400000) return;

  // 이미 standalone 모드면 안 보여줌
  if (window.matchMedia('(display-mode: standalone)').matches) return;
  if (window.navigator.standalone === true) return;

  // 배너가 이미 있으면 스킵
  if (document.getElementById('cb-install-banner')) return;

  var isEn = window.CodiBankI18n && CodiBankI18n.isEn();

  var banner = document.createElement('div');
  banner.id = 'cb-install-banner';
  banner.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);z-index:99998;width:calc(100% - 32px);max-width:400px;background:rgba(7,19,42,.92);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid rgba(76,219,206,.25);border-radius:20px;padding:16px 20px;display:flex;align-items:center;gap:14px;box-shadow:0 16px 48px rgba(2,13,36,.6);animation:slideUpBanner .4s ease-out;';

  banner.innerHTML = [
    '<div style="width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#4cdbce,#13bbaf);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:20px;font-weight:900;color:#003733;font-family:Arial,sans-serif;">CB</div>',
    '<div style="flex:1;min-width:0;">',
    '  <div style="font-size:13px;font-weight:700;color:#d8e2ff;margin-bottom:2px;">' + (isEn ? 'Add CodiBank to Home Screen' : '코디뱅크를 홈화면에 추가') + '</div>',
    '  <div style="font-size:11px;color:rgba(216,226,255,.45);">' + (isEn ? 'Use like a native app — fast & convenient' : '앱처럼 빠르고 편리하게 사용하세요') + '</div>',
    '</div>',
    '<button id="cb-install-btn" style="padding:8px 16px;border-radius:9999px;background:linear-gradient(135deg,#4cdbce,#13bbaf);color:#003733;font-size:12px;font-weight:700;border:none;cursor:pointer;flex-shrink:0;font-family:Inter,sans-serif;">' + (isEn ? 'Install' : '설치') + '</button>',
    '<button id="cb-install-close" style="width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,.08);border:none;cursor:pointer;color:rgba(216,226,255,.4);font-size:16px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">✕</button>',
  ].join('');

  // 스타일 애니메이션
  if (!document.getElementById('cb-pwa-style')) {
    var style = document.createElement('style');
    style.id = 'cb-pwa-style';
    style.textContent = '@keyframes slideUpBanner{from{transform:translateX(-50%) translateY(20px);opacity:0}to{transform:translateX(-50%) translateY(0);opacity:1}}';
    document.head.appendChild(style);
  }

  document.body.appendChild(banner);

  // 설치 버튼
  document.getElementById('cb-install-btn').addEventListener('click', function() {
    if (_deferredPrompt) {
      _deferredPrompt.prompt();
      _deferredPrompt.userChoice.then(function(result) {
        if (result.outcome === 'accepted') {
          console.log('[PWA] User accepted install');
        }
        _deferredPrompt = null;
        hideInstallBanner();
      });
    }
  });

  // 닫기 버튼
  document.getElementById('cb-install-close').addEventListener('click', function() {
    localStorage.setItem('cb_pwa_dismissed', String(Date.now()));
    hideInstallBanner();
  });
}

function hideInstallBanner() {
  var el = document.getElementById('cb-install-banner');
  if (el) el.remove();
}

// iOS Safari 대응: "홈 화면에 추가" 안내
if (/iPad|iPhone|iPod/.test(navigator.userAgent) && !window.navigator.standalone) {
  // iOS는 beforeinstallprompt 미지원 → 3초 후 안내 배너 표시
  setTimeout(function() {
    if (window.matchMedia('(display-mode: standalone)').matches) return;
    var dismissed = localStorage.getItem('cb_pwa_dismissed');
    if (dismissed && (Date.now() - Number(dismissed)) < 86400000) return;
    if (document.getElementById('cb-install-banner')) return;

    var isEn = window.CodiBankI18n && CodiBankI18n.isEn();

    var banner = document.createElement('div');
    banner.id = 'cb-install-banner';
    banner.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);z-index:99998;width:calc(100% - 32px);max-width:400px;background:rgba(7,19,42,.92);backdrop-filter:blur(24px);border:1px solid rgba(76,219,206,.25);border-radius:20px;padding:16px 20px;box-shadow:0 16px 48px rgba(2,13,36,.6);animation:slideUpBanner .4s ease-out;text-align:center;';
    banner.innerHTML = [
      '<div style="font-size:13px;font-weight:700;color:#d8e2ff;margin-bottom:6px;">' + (isEn ? 'Add CodiBank to Home Screen' : '코디뱅크를 홈화면에 추가하세요') + '</div>',
      '<div style="font-size:11px;color:rgba(216,226,255,.45);line-height:1.6;">' + (isEn ? 'Tap <b>Share</b> ↗ then <b>"Add to Home Screen"</b>' : '<b>공유</b> ↗ 버튼 → <b>"홈 화면에 추가"</b>를 눌러주세요') + '</div>',
      '<button id="cb-install-close" style="margin-top:10px;padding:6px 20px;border-radius:9999px;background:rgba(255,255,255,.08);border:none;cursor:pointer;color:rgba(216,226,255,.5);font-size:11px;font-weight:600;">' + (isEn ? 'Got it' : '알겠어요') + '</button>',
    ].join('');

    if (!document.getElementById('cb-pwa-style')) {
      var style = document.createElement('style');
      style.id = 'cb-pwa-style';
      style.textContent = '@keyframes slideUpBanner{from{transform:translateX(-50%) translateY(20px);opacity:0}to{transform:translateX(-50%) translateY(0);opacity:1}}';
      document.head.appendChild(style);
    }

    document.body.appendChild(banner);
    document.getElementById('cb-install-close').addEventListener('click', function() {
      localStorage.setItem('cb_pwa_dismissed', String(Date.now()));
      banner.remove();
    });
  }, 3000);
}

})();
