// 코디뱅크 런타임 설정 (프로토타입 기본값)
// - 필요 시 app/config.example.js 를 참고해 값만 수정하세요.

window.CODIBANK_CONFIG = {
  backendBase: "",
  weatherProvider: "OPEN_METEO_DEV", // 프로토타입 기본(상업 운영 시 KMA 전환 권장)
  kmaServiceKey: "",
  allowOpenMeteoDev: true,
  aiProvider: "REMOTE", // OpenAI 이미지 생성 사용(서버 실행 필요). 서버 미실행 시 로컬 데모로 자동 폴백
  aiBase: "",
};
