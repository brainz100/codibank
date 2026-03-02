# CodiBank Prototype (Static HTML)

이 폴더는 첨부해주신 UI 시안(랜딩/클로젯/공유/판매)을 **로컬에서 바로 열어볼 수 있게** 정리한 정적(Static) 프로토타입입니다.

## 실행 방법

가장 간단한 방법:

- `index.html`을 더블클릭해서 브라우저로 열기

권장(라우팅/리소스 오류 방지): 로컬 서버로 실행

```bash
# Node.js가 있다면
npx serve .
# 또는
python -m http.server 8080
```

브라우저에서 `http://localhost:3000` 또는 `http://localhost:8080` 으로 접속합니다.

### 카메라(촬영) 테스트

`app/camera.html`은 브라우저 보안 정책 때문에 **HTTPS 또는 localhost**에서만 카메라 접근(`getUserMedia`)이 정상 동작합니다.

- 권장: 위의 로컬 서버 방식으로 실행
- 카메라가 막히는 환경에서도 테스트 가능: 전면/후면/브랜드 이미지를 **업로드**로도 등록할 수 있게 구성해두었습니다.

## 런타임 설정(config.js)

`app/config.js`에서 아래를 설정할 수 있습니다.

- `weatherProvider`: `"OPEN_METEO_DEV"`(프로토타입) / `"KMA"`(상업 운영 권장)
- `backendBase`: `http://내PC_IP:8787` 처럼 **백엔드/프록시** 주소
- `aiProvider`: `"LOCAL"`(프로토타입 합성) / `"REMOTE"`(백엔드 AI)

예시는 `app/config.example.js`를 참고하세요.

> ⚠️ 주의: 상업 운영에서는 브라우저 코드에 서비스키(공공 API 키 포함)를 직접 넣지 마세요.

## (선택) 백엔드/프록시 서버

이 프로토타입은 정적 파일이지만,
상업 운영/정확도 개선을 위해 아래 2가지는 **백엔드**가 있는 구조가 현실적입니다.

1) 날씨(KMA/data.go.kr) 호출 프록시(키 보관 + CORS 회피)
2) 추천 코디/가상 스타일링 이미지 생성(오픈소스 LLM + SDXL/IP-Adapter 등)

`server/` 폴더에 **엔드포인트 스펙/더미 서버 예시**를 같이 넣어두었습니다.

## 구성

- `index.html` : 랜딩페이지
- `app/closet.html` : 디지털 옷장 메인
- `app/item.html` : 옷 아이템 상세(공유/판매 버튼 포함)
- `app/share.html` : 공유 피드
- `app/share-item.html` : 공유 상세/요청
- `app/sale.html` : 판매 피드
- `app/sale-item.html` : 판매 상세/오퍼 관리
- `app/login.html` : 로그인(네이버/카카오 버튼 포함, Prototype)
- `app/signup.html` : 회원가입(키/몸무게/성별)
- `app/pricing.html` : 구독 플랜
- `app/camera.html` : 아이템 촬영/등록(AI: 카테고리·컬러·브랜드 자동 인식)

## AI 추천/가상 스타일링(프로토타입 → 백엔드 연동)

- 기본값은 `LOCAL` 모드로, 브라우저에서 **룩북 느낌의 이미지**를 합성합니다.
- `aiProvider = "REMOTE"`로 바꾸면, `POST /api/ai/styling` 호출을 시도합니다.
  - 백엔드가 응답하면 그 이미지를 사용하고,
  - 실패하면 자동으로 LOCAL 합성으로 fallback 됩니다.

## 참고

- 이 프로토타입은 **UI/UX 검증용**입니다.
- 실제 서비스 개발 시에는 API/DB/권한/결제/정산/운영툴/보안이 추가로 필요합니다.
