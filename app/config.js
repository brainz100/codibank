// CodiBank 설정 파일
// Supabase 대시보드 → Settings → API 에서 "anon public" 키 확인
// URL: https://supabase.com/dashboard/project/drgsayvlpzcacurcczjq/settings/api

window.CODIBANK_CONFIG = {
  backendBase: "https://codibank-api.onrender.com",
  weatherProvider: "OPEN_METEO_DEV",
  kmaServiceKey: "",
  allowOpenMeteoDev: true,
  aiProvider: "REMOTE",
  aiBase: "",

  // ─── 2026-09-08 KST · TJ 지시 ─── 기능 플래그 (테스트 간소화) ────────────
  //  featureRunway : 풋바 '런웨이' 탭 노출 + runway.html 직접 접근 허용 여부
  //    false → 풋바 5탭 (코디핏·트라이온·Ai옷장·코디앨범·MY)
  //             runway.html 직접 URL 접근 시 closet.html 로 리다이렉트
  //    true  → 6탭 원복. runway.html · /api/runway/* · Seedance v21 프롬프트는
  //             삭제하지 않고 그대로 살려두었으므로 즉시 정상 동작합니다.
  //  ※ 이 한 줄만 바꾸면 전 페이지가 동시에 원복됩니다 (HTML 재수정 불필요).
  featureRunway: false,
  // ─────────────────────────────────────────────────────────────────────────

  // ── Supabase 인증 설정 (필수) ────────────────────────────────
  supabaseUrl:     "https://drgsayvlpzcacurcczjq.supabase.co",
  supabaseAnonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRyZ3NheXZscHpjYWN1cmNjempxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4MjU4MTMsImV4cCI6MjA4OTQwMTgxM30.4_M245-q2LeFKRf6go587R0U2ocPNa9iSv3qHCQMOPA",  // ← Supabase 대시보드 anon public 키 (eyJhbGci...)
  // ─────────────────────────────────────────────────────────────
};
