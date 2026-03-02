// 코디뱅크 런타임 설정 예시
// 1) 이 파일을 복사해서 app/config.js 로 저장하세요.
// 2) 필요에 따라 값만 수정하면 됩니다.
//
// ⚠️ 주의(중요)
// - 브라우저(프론트) 코드에 "실제 서비스키"를 직접 넣는 것은 보안상 위험합니다.
// - 상업 서비스에서는 backend proxy(서버)에서 키를 보관하고 프론트는 proxy만 호출하세요.

window.CODIBANK_CONFIG = {
  // (권장) 백엔드/프록시 서버 주소
  // - 예: "http://192.168.0.12:8787" (같은 와이파이에서 갤럭시폰으로 접속 가능)
  // - 비워두면 현재 origin 기준으로 호출합니다.
  backendBase: "",

  // 날씨 제공자
  // - "KMA": data.go.kr(기상청) 기반 (상업용 권장)
  // - "OPEN_METEO_DEV": 프로토타입 개발용(상업 운영 전환 필수)
  weatherProvider: "OPEN_METEO_DEV",

  // KMA 서비스키 (개발용 직접 호출 시 사용)
  // - 상업 운영은 서버에서 키를 보관하세요.
  kmaServiceKey: "",

  // open-meteo 개발용 fallback 허용
  // - 상업 운영에서는 false 권장
  allowOpenMeteoDev: true,

  // AI 가상스타일링
  // - "LOCAL": 현재처럼 브라우저에서 프로토타입 이미지 합성
  // - "REMOTE": 백엔드 AI(오픈소스 LLM + SDXL/IP-Adapter 등)로 이미지 생성
  aiProvider: "LOCAL",

  // AI Base (옵션)
  // - 비워두면 backendBase를 사용합니다.
  aiBase: "",
};
