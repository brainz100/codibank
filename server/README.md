# CodiBank OpenAI 스타일링 프록시 (필수: AI 추천 스타일링 데모)

`app/`은 **정적(Static) 프론트**라서, OpenAI API Key를 안전하게 보관할 수 없습니다.
따라서 **PC에서 로컬 프록시 서버**를 띄우고(같은 Wi‑Fi), 모바일은 그 서버를 호출하는 구조로 데모를 만듭니다.

- 프론트(갤럭시 크롬): `http://내PC_IP:5500/app/closet.html`
- 프록시(PC): `http://내PC_IP:8787/api/ai/styling`

> 프론트는 기본적으로 `aiProvider: "REMOTE"`이며, 서버가 꺼져 있으면 **로컬 데모 이미지로 자동 폴백**합니다.

---

## 1) 준비물

- Python 3.10+ 권장
- OpenAI API Key (환경변수로 설정)

---

## 2) 설치

```bash
cd server
python3 -m pip install -r requirements.txt
```

---

## 3) OpenAI API Key 설정

### macOS / Linux

```bash
export OPENAI_API_KEY="YOUR_KEY"
```

### Windows (PowerShell)

```powershell
setx OPENAI_API_KEY "YOUR_KEY"
```

> `setx`는 **새 터미널**에서 적용됩니다. 설정 후 PowerShell을 새로 열어주세요.

---

## 4) 서버 실행

```bash
python3 mock_backend.py
```

기본 포트: **8787**

정상 동작 확인:
- `http://localhost:8787/health`

추가 진단(권장):
- `http://localhost:8787/api/ai/diagnose`
  - ok=true면 "키 인증"까지는 정상입니다.
  - 여기서 에러가 나면 키/조직/권한/요금(빌링) 문제일 가능성이 높습니다.

---

## 5) 갤럭시폰에서 접속이 안될 때(중요)

1) 휴대폰/PC가 **같은 Wi‑Fi**인지 확인
2) PC 방화벽에서 **8787 포트 허용**
3) 프록시 주소는 `127.0.0.1`이 아니라 **내 PC의 Wi‑Fi IP**

---

## 6) 옵션(모델/품질)

환경변수로 바꿀 수 있습니다.

- 얼굴 없는 생성 모델(기본: `gpt-image-1.5`)
  - `CODIBANK_OPENAI_IMAGE_MODEL`
- 얼굴 포함(참조 이미지) 모델(기본: `gpt-image-1.5`)
  - `CODIBANK_OPENAI_IMAGE_MODEL_FACE`

> 비용/속도/품질 트레이드오프가 있습니다.

---

## 7) 디버그(프롬프트 확인)

```bash
export CODIBANK_DEBUG_PROMPT=1
```

서버 응답에 `prompt`가 포함됩니다.
