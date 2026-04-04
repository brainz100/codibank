/**
 * 착착 코디뱅크 — Global Weather Utility v2.1
 * 
 * 목적: 사용자의 실제 위치를 기반으로 날씨 예보를 제공
 * (6대 도시 AI 스타일리스트 매칭과는 별개 — 패션 추천은 코디뱅크 DB에서 처리)
 * 
 * 사용법:
 *   <script src="global_weather_utility.js"></script>
 *   const weather = await CodiBankWeather.init();
 */

const CodiBankWeather = (() => {

  // ═══════════════════════════════════════════════
  // 도시명 한글 변환 DB (날씨 표시용 — 패션 추천과 무관)
  // IP 위치 감지 시 영어 도시명 → 한글 표기 변환에만 사용
  // ═══════════════════════════════════════════════
  const CITY_NAME_KO = {
    // 한국
    "Seoul": "서울", "Busan": "부산", "Incheon": "인천", "Daegu": "대구",
    "Daejeon": "대전", "Gwangju": "광주", "Suwon": "수원", "Ulsan": "울산",
    "Seongnam": "성남", "Goyang": "고양", "Yongin": "용인", "Jeju": "제주",
    "Changwon": "창원", "Cheongju": "청주", "Jeonju": "전주", "Pohang": "포항",
    // 일본
    "Tokyo": "도쿄", "Osaka": "오사카", "Kyoto": "교토", "Yokohama": "요코하마",
    // 중국
    "Beijing": "베이징", "Shanghai": "상하이", "Hong Kong": "홍콩", "Guangzhou": "광저우",
    // 동남아
    "Singapore": "싱가포르", "Bangkok": "방콕", "Hanoi": "하노이",
    "Ho Chi Minh City": "호치민", "Jakarta": "자카르타", "Manila": "마닐라",
    // 남아시아
    "Mumbai": "뭄바이", "New Delhi": "뉴델리",
    // 중동
    "Dubai": "두바이", "Abu Dhabi": "아부다비", "Riyadh": "리야드",
    "Doha": "도하", "Cairo": "카이로", "Istanbul": "이스탄불",
    // 유럽
    "Paris": "파리", "London": "런던", "Berlin": "베를린", "Rome": "로마",
    "Madrid": "마드리드", "Amsterdam": "암스테르담", "Barcelona": "바르셀로나",
    "Milan": "밀라노", "Vienna": "비엔나", "Prague": "프라하",
    "Zurich": "취리히", "Moscow": "모스크바", "Stockholm": "스톡홀름",
    "Copenhagen": "코펜하겐", "Helsinki": "헬싱키", "Oslo": "오슬로",
    "Lisbon": "리스본", "Athens": "아테네", "Warsaw": "바르샤바",
    "Budapest": "부다페스트", "Dublin": "더블린", "Brussels": "브뤼셀",
    // 북미
    "New York": "뉴욕", "Los Angeles": "로스앤젤레스", "Chicago": "시카고",
    "San Francisco": "샌프란시스코", "Toronto": "토론토", "Vancouver": "밴쿠버",
    "Miami": "마이애미", "Seattle": "시애틀", "Boston": "보스턴",
    "Washington": "워싱턴", "Houston": "휴스턴", "Las Vegas": "라스베이거스",
    // 남미
    "São Paulo": "상파울루", "Rio de Janeiro": "리우데자네이루",
    "Buenos Aires": "부에노스아이레스", "Mexico City": "멕시코시티",
    "Lima": "리마", "Bogota": "보고타", "Santiago": "산티아고",
    // 오세아니아
    "Sydney": "시드니", "Melbourne": "멜버른", "Auckland": "오클랜드",
    // 아프리카
    "Cape Town": "케이프타운", "Johannesburg": "요하네스버그",
    "Nairobi": "나이로비", "Lagos": "라고스", "Casablanca": "카사블랑카",
  };

  // ═══════════════════════════════════════════════
  // WMO 날씨 코드 → 한/영 이중 매핑
  // ═══════════════════════════════════════════════
  const WMO = {
    0:  { icon: "☀️",  ko: "맑음",           en: "Clear sky" },
    1:  { icon: "🌤️", ko: "대체로 맑음",     en: "Mainly clear" },
    2:  { icon: "⛅",  ko: "구름 조금",       en: "Partly cloudy" },
    3:  { icon: "☁️",  ko: "흐림",           en: "Overcast" },
    45: { icon: "🌫️", ko: "안개",           en: "Fog" },
    48: { icon: "🌫️", ko: "짙은 안개",       en: "Rime fog" },
    51: { icon: "🌦️", ko: "가벼운 이슬비",   en: "Light drizzle" },
    53: { icon: "🌦️", ko: "이슬비",         en: "Drizzle" },
    55: { icon: "🌧️", ko: "강한 이슬비",     en: "Heavy drizzle" },
    56: { icon: "🧊",  ko: "결빙 이슬비",     en: "Freezing drizzle" },
    57: { icon: "🧊",  ko: "강한 결빙 이슬비", en: "Heavy freezing drizzle" },
    61: { icon: "🌧️", ko: "약한 비",         en: "Light rain" },
    63: { icon: "🌧️", ko: "비",             en: "Rain" },
    65: { icon: "🌧️", ko: "강한 비",         en: "Heavy rain" },
    66: { icon: "🧊",  ko: "결빙 비",         en: "Freezing rain" },
    67: { icon: "🧊",  ko: "강한 결빙 비",     en: "Heavy freezing rain" },
    71: { icon: "🌨️", ko: "약한 눈",         en: "Light snow" },
    73: { icon: "❄️",  ko: "눈",             en: "Snow" },
    75: { icon: "❄️",  ko: "강한 눈",         en: "Heavy snow" },
    77: { icon: "🌨️", ko: "싸락눈",         en: "Snow grains" },
    80: { icon: "🌦️", ko: "약한 소나기",     en: "Light showers" },
    81: { icon: "🌧️", ko: "소나기",         en: "Showers" },
    82: { icon: "⛈️",  ko: "강한 소나기",     en: "Heavy showers" },
    85: { icon: "🌨️", ko: "약한 눈소나기",   en: "Light snow showers" },
    86: { icon: "❄️",  ko: "강한 눈소나기",   en: "Heavy snow showers" },
    95: { icon: "⛈️",  ko: "뇌우",           en: "Thunderstorm" },
    96: { icon: "⛈️",  ko: "우박 뇌우",       en: "Thunderstorm with hail" },
    99: { icon: "⛈️",  ko: "강한 우박 뇌우",   en: "Severe thunderstorm with hail" },
  };

  function getWMO(code, lang) {
    const e = WMO[code] || WMO[0];
    return { icon: e.icon, desc: (lang === "ko") ? e.ko : e.en, descKo: e.ko, descEn: e.en };
  }

  // ═══════════════════════════════════════════════
  // 도시명 한글 변환 (표시용)
  // ═══════════════════════════════════════════════
  function toKoreanCityName(englishName) {
    if (!englishName) return null;
    const name = englishName.trim();
    // 정확 매칭
    if (CITY_NAME_KO[name]) return CITY_NAME_KO[name];
    // 부분 매칭
    const lower = name.toLowerCase();
    for (const [key, ko] of Object.entries(CITY_NAME_KO)) {
      if (key.toLowerCase() === lower) return ko;
    }
    // 매칭 안 되면 원래 이름 반환 (세계 어디든 가능)
    return name;
  }

  // ═══════════════════════════════════════════════
  // 사용자 언어 감지
  // ═══════════════════════════════════════════════
  function detectLang() {
    try {
      const u = JSON.parse(localStorage.getItem('codibank_user') || '{}');
      if (u.language) return u.language;
    } catch(e) {}
    const nav = (navigator.language || 'ko').toLowerCase();
    if (nav.startsWith('ko')) return 'ko';
    return 'en';
  }

  // ═══════════════════════════════════════════════
  // 사용자 위치 감지 — 전 세계 어디든 작동
  // 순서: 프로필 도시 → IP 감지 → GPS → 서울 fallback
  // ═══════════════════════════════════════════════
  async function detectLocation() {
    // 0) 프로필에 도시가 있으면 우선 (사용자가 직접 설정한 위치)
    try {
      const u = JSON.parse(localStorage.getItem('codibank_user') || '{}');
      if (u.lat && u.lon) {
        return { lat: u.lat, lon: u.lon, city: u.city || null, source: 'profile-coords' };
      }
    } catch(e) {}

    // 1) IP 기반 — 전 세계 어디서든 작동
    const ipApis = [
      { url: "https://ipapi.co/json/",
        parse: d => ({ lat: d.latitude, lon: d.longitude, city: d.city || d.region || '' }) },
      { url: "https://ipwho.is/",
        parse: d => ({ lat: d.latitude, lon: d.longitude, city: d.city || d.region || '' }) },
      { url: "https://get.geojs.io/v1/ip/geo.json",
        parse: d => ({ lat: parseFloat(d.latitude), lon: parseFloat(d.longitude), city: d.city || d.region || '' }) },
    ];
    for (const api of ipApis) {
      try {
        const ctrl = new AbortController();
        const tid = setTimeout(() => ctrl.abort(), 4000);
        const res = await fetch(api.url, { signal: ctrl.signal });
        clearTimeout(tid);
        if (!res.ok) continue;
        const data = await res.json();
        const loc = api.parse(data);
        if (loc.lat && loc.lon && !isNaN(loc.lat) && !isNaN(loc.lon)) {
          return { lat: loc.lat, lon: loc.lon, city: loc.city, source: 'ip' };
        }
      } catch(e) { continue; }
    }

    // 2) 브라우저 GPS
    if (navigator.geolocation) {
      try {
        const pos = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
        });
        return { lat: pos.coords.latitude, lon: pos.coords.longitude, city: null, source: 'gps' };
      } catch(e) {}
    }

    // 3) 최종 fallback — 서울
    return { lat: 37.5665, lon: 126.978, city: "Seoul", source: 'fallback' };
  }

  // ═══════════════════════════════════════════════
  // Open-Meteo 호출 — 위도/경도 기반 (전 세계 커버)
  // ═══════════════════════════════════════════════
  async function fetchWeather(lat, lon) {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}`
      + `&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation`
      + `&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code`
      + `&timezone=auto&forecast_days=7`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Weather API ${res.status}`);
    return await res.json();
  }

  // ═══════════════════════════════════════════════
  // 기온 → 옷차림 버킷 (순수 온도 기반, 위치 무관)
  // ═══════════════════════════════════════════════
  function getTempBucket(temp) {
    if (temp <= -10) return { ko: "한파",     en: "extreme cold",  layer: "heavy padded coat, thermal layers, insulated boots" };
    if (temp <= 0)   return { ko: "매우 추움", en: "very cold",     layer: "winter coat with layers, warm knitwear, boots" };
    if (temp <= 5)   return { ko: "추움",     en: "cold",          layer: "thick coat, sweater or fleece, closed shoes" };
    if (temp <= 10)  return { ko: "쌀쌀",     en: "chilly",        layer: "jacket with long-sleeve shirt, light layers" };
    if (temp <= 15)  return { ko: "선선",     en: "cool",          layer: "light jacket or cardigan, comfortable layers" };
    if (temp <= 20)  return { ko: "적당",     en: "mild",          layer: "single outer layer optional, versatile clothing" };
    if (temp <= 25)  return { ko: "따뜻",     en: "warm",          layer: "light single layer, breathable fabrics" };
    if (temp <= 30)  return { ko: "더움",     en: "hot",           layer: "light clothing, breathable, sun protection" };
    if (temp <= 35)  return { ko: "매우 더움", en: "very hot",      layer: "minimal layers, UV protection, light colors" };
    return            { ko: "폭염",     en: "extreme heat",  layer: "lightest breathable fabrics, sun shielding essential" };
  }

  // ═══════════════════════════════════════════════
  // 메인 초기화
  // ═══════════════════════════════════════════════
  async function init() {
    const lang = detectLang();
    const DAY_KO = ["일","월","화","수","목","금","토"];
    const DAY_EN = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
    const now = new Date();
    const dateStr = `${now.getFullYear()}.${now.getMonth()+1}.${now.getDate()} (${DAY_KO[now.getDay()]})`;

    let result = {
      city: "...", cityEn: "...",
      temp: "--°C", tempNum: null, feelTemp: "--°C",
      icon: "⏳", desc: lang === "ko" ? "날씨 확인 중..." : "Loading weather...",
      descKo: "", descEn: "",
      humidity: null, windSpeed: null, precipitation: null,
      weatherCode: 0, date: dateStr,
      tempBucket: null,
      forecast: [],       // 7일 예보
      loading: true, error: null, lang, source: null,
    };

    try {
      const loc = await detectLocation();
      result.source = loc.source;

      // 도시명
      const cityKo = loc.city ? toKoreanCityName(loc.city) : null;
      result.cityEn = loc.city || "";

      // 날씨 데이터
      const data = await fetchWeather(loc.lat, loc.lon);
      const cur = data.current;
      const tempNum = Math.round(cur.temperature_2m);
      const feelNum = Math.round(cur.apparent_temperature);
      const wmo = getWMO(cur.weather_code, lang);
      const bucket = getTempBucket(tempNum);

      // 도시명 최종 결정
      if (cityKo) {
        result.city = cityKo;
      } else {
        const tz = data.timezone || "";
        const tzCity = tz.split("/").pop().replace(/_/g, " ");
        result.city = toKoreanCityName(tzCity);
        result.cityEn = tzCity;
      }

      // 7일 예보
      const forecast = [];
      if (data.daily) {
        for (let i = 0; i < (data.daily.time || []).length; i++) {
          const d = new Date(data.daily.time[i] + "T00:00:00");
          const fWmo = getWMO(data.daily.weather_code[i], lang);
          const fBucket = getTempBucket(Math.round((data.daily.temperature_2m_max[i] + data.daily.temperature_2m_min[i]) / 2));
          forecast.push({
            date: data.daily.time[i],
            dayKo: DAY_KO[d.getDay()],
            dayEn: DAY_EN[d.getDay()],
            maxTemp: Math.round(data.daily.temperature_2m_max[i]),
            minTemp: Math.round(data.daily.temperature_2m_min[i]),
            precipProb: data.daily.precipitation_probability_max[i],
            icon: fWmo.icon,
            desc: fWmo.desc,
            descKo: fWmo.descKo,
            descEn: fWmo.descEn,
            bucket: fBucket,
          });
        }
      }

      Object.assign(result, {
        temp: `${tempNum}°C`, tempNum,
        feelTemp: `${feelNum}°C`,
        icon: wmo.icon, desc: wmo.desc, descKo: wmo.descKo, descEn: wmo.descEn,
        humidity: cur.relative_humidity_2m,
        windSpeed: Math.round(cur.wind_speed_10m),
        precipitation: cur.precipitation,
        weatherCode: cur.weather_code,
        tempBucket: bucket,
        forecast,
        loading: false,

        // 백엔드 전송용 (mock_backend.py → 프롬프트에 삽입)
        forBackend: {
          temp: tempNum,
          feels_like: feelNum,
          humidity: cur.relative_humidity_2m,
          wind_speed: Math.round(cur.wind_speed_10m),
          condition: wmo.descEn,       // 영어 (프롬프트용)
          code: cur.weather_code,
          location: result.cityEn || result.city,  // 사용자 실제 위치
          bucket: bucket.en,
          layer_hint: bucket.layer,
        }
      });

    } catch(err) {
      result.loading = false;
      result.error = err.message;
      result.icon = "⚠️";
      result.desc = lang === "ko" ? "날씨 정보 불러오기 실패" : "Weather unavailable";
    }

    return result;
  }

  return { init, detectLocation, toKoreanCityName, getTempBucket, getWMO, CITY_NAME_KO, WMO };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = CodiBankWeather;
