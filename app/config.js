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

  // ── Supabase 인증 설정 (필수) ────────────────────────────────
  supabaseUrl:     "https://drgsayvlpzcacurcczjq.supabase.co",
  supabaseAnonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRyZ3NheXZscHpjYWN1cmNjempxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4MjU4MTMsImV4cCI6MjA4OTQwMTgxM30.4_M245-q2LeFKRf6go587R0U2ocPNa9iSv3qHCQMOPA",  // ← Supabase 대시보드 anon public 키 (eyJhbGci...)
  // ─────────────────────────────────────────────────────────────
};
