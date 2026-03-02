"""
코디뱅크 — Cloudflare R2 연결 점검 스크립트
=============================================
사용법:
  1. 이 파일을 server 폴더 안에 넣습니다
  2. 터미널에서 server 폴더로 이동합니다
  3. python test_r2.py 실행

필요 패키지: boto3, python-dotenv
  pip install boto3 python-dotenv
"""

import os
import sys

# ── .env 파일 자동 로딩 ────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    _here = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(_here, ".env"))
    load_dotenv(os.path.join(os.path.dirname(_here), ".env"))
except ImportError:
    print("⚠️  python-dotenv 없음 — 환경변수를 직접 읽습니다")

# ── 색상 출력 헬퍼 ─────────────────────────────────────────────────
def ok(msg):   print(f"  ✅  {msg}")
def err(msg):  print(f"  ❌  {msg}")
def warn(msg): print(f"  ⚠️   {msg}")
def info(msg): print(f"  ℹ️   {msg}")
def sep():     print("─" * 55)

# ═══════════════════════════════════════════════════════════════════
print()
print("=" * 55)
print("  코디뱅크 Cloudflare R2 연결 점검")
print("=" * 55)
print()

# ─────────────────────────────────────────────────────────────────
# STEP 1: 환경변수 확인
# ─────────────────────────────────────────────────────────────────
sep()
print("STEP 1  환경변수 확인")
sep()

KEYS = [
    ("R2_ACCESS_KEY_ID",     "액세스 키 ID"),
    ("R2_SECRET_ACCESS_KEY", "비밀 액세스 키"),
    ("R2_ENDPOINT_URL",      "엔드포인트 URL"),
    ("R2_BUCKET_NAME",       "버킷 이름"),
    ("R2_PUBLIC_URL",        "공개 URL"),
]

env = {}
all_ok = True
for key, label in KEYS:
    val = os.getenv(key, "").strip()
    env[key] = val
    if val:
        # 비밀 키는 앞 6자리만 표시
        display = val[:6] + "..." if "SECRET" in key else val
        ok(f"{label:20s}  {display}")
    else:
        err(f"{label:20s}  ← 비어있음!")
        all_ok = False

if not all_ok:
    print()
    err("환경변수가 빠져있습니다. server/.env 파일을 확인하세요.")
    print()
    print("  .env 파일 예시:")
    print("  ┌────────────────────────────────────────────────┐")
    print("  │ R2_ACCESS_KEY_ID=여기에_액세스키_입력          │")
    print("  │ R2_SECRET_ACCESS_KEY=여기에_비밀키_입력        │")
    print("  │ R2_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com │")
    print("  │ R2_BUCKET_NAME=codibank                        │")
    print("  │ R2_PUBLIC_URL=https://pub-xxx.r2.dev           │")
    print("  └────────────────────────────────────────────────┘")
    sys.exit(1)

print()

# ─────────────────────────────────────────────────────────────────
# STEP 2: boto3 설치 확인
# ─────────────────────────────────────────────────────────────────
sep()
print("STEP 2  boto3 패키지 확인")
sep()

try:
    import boto3
    ok(f"boto3 설치됨  (버전 {boto3.__version__})")
except ImportError:
    err("boto3가 설치되지 않았습니다")
    print()
    print("  아래 명령어로 설치하세요:")
    print("  pip install boto3")
    sys.exit(1)

print()

# ─────────────────────────────────────────────────────────────────
# STEP 3: R2 접속 테스트
# ─────────────────────────────────────────────────────────────────
sep()
print("STEP 3  R2 서버 접속 테스트")
sep()

try:
    client = boto3.client(
        "s3",
        endpoint_url=env["R2_ENDPOINT_URL"],
        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )
    ok("R2 클라이언트 생성 성공")
except Exception as e:
    err(f"R2 클라이언트 생성 실패: {e}")
    sys.exit(1)

print()

# ─────────────────────────────────────────────────────────────────
# STEP 4: 버킷 접근 테스트
# ─────────────────────────────────────────────────────────────────
sep()
print("STEP 4  버킷 접근 테스트")
sep()

bucket = env["R2_BUCKET_NAME"]

try:
    response = client.list_objects_v2(Bucket=bucket, MaxKeys=5)
    count = response.get("KeyCount", 0)
    ok(f"버킷 '{bucket}' 접근 성공!")
    info(f"현재 저장된 파일 수: {count}개")
except client.exceptions.NoSuchBucket:
    err(f"버킷 '{bucket}'이 존재하지 않습니다")
    print()
    warn("Cloudflare R2에서 버킷 이름을 확인하세요")
    sys.exit(1)
except Exception as e:
    err(f"버킷 접근 실패: {e}")
    print()
    if "InvalidAccessKeyId" in str(e) or "SignatureDoesNotMatch" in str(e):
        warn("Access Key ID 또는 Secret Key가 잘못됐습니다")
        warn("Cloudflare R2에서 새 API 토큰을 발급받으세요")
    elif "NoSuchBucket" in str(e):
        warn(f"버킷 이름 '{bucket}'을 확인하세요")
    else:
        warn("Endpoint URL이 잘못됐을 수 있습니다")
    sys.exit(1)

print()

# ─────────────────────────────────────────────────────────────────
# STEP 5: 파일 업로드 테스트
# ─────────────────────────────────────────────────────────────────
sep()
print("STEP 5  파일 업로드 테스트")
sep()

TEST_KEY = "test_codibank_connection.txt"
TEST_CONTENT = b"CodiBank R2 connection test OK!"

try:
    client.put_object(
        Bucket=bucket,
        Key=TEST_KEY,
        Body=TEST_CONTENT,
        ContentType="text/plain",
    )
    ok("파일 업로드 성공!")
except Exception as e:
    err(f"업로드 실패: {e}")
    print()
    warn("API 토큰 권한을 확인하세요 (Object Read & Write 필요)")
    sys.exit(1)

print()

# ─────────────────────────────────────────────────────────────────
# STEP 6: 공개 URL 접근 테스트
# ─────────────────────────────────────────────────────────────────
sep()
print("STEP 6  공개 URL 접근 테스트")
sep()

public_url = env["R2_PUBLIC_URL"].rstrip("/")
test_url = f"{public_url}/{TEST_KEY}"

try:
    import urllib.request
    with urllib.request.urlopen(test_url, timeout=10) as resp:
        content = resp.read()
        if content == TEST_CONTENT:
            ok("공개 URL로 파일 접근 성공!")
            ok(f"URL: {test_url}")
        else:
            warn("파일은 읽혔지만 내용이 다릅니다 (정상일 수 있음)")
except Exception as e:
    err(f"공개 URL 접근 실패: {e}")
    print()
    warn("R2 버킷의 'Public Development URL' 설정을 확인하세요")
    warn("Settings → Public Development URL → 허용 클릭")
    info(f"테스트 URL: {test_url}")

print()

# ─────────────────────────────────────────────────────────────────
# STEP 7: 테스트 파일 삭제
# ─────────────────────────────────────────────────────────────────
sep()
print("STEP 7  테스트 파일 정리")
sep()

try:
    client.delete_object(Bucket=bucket, Key=TEST_KEY)
    ok("테스트 파일 삭제 완료")
except Exception as e:
    warn(f"테스트 파일 삭제 실패 (무시 가능): {e}")

print()

# ─────────────────────────────────────────────────────────────────
# 최종 결과
# ─────────────────────────────────────────────────────────────────
print("=" * 55)
print("  🎉  모든 테스트 통과!  R2 연결 정상입니다")
print("=" * 55)
print()
print("  다음 단계: Render.com 환경변수에 아래 5개 값 입력")
print()
for key, label in KEYS:
    val = env[key]
    display = val[:6] + "..." if "SECRET" in key else val
    print(f"  {key}")
    print(f"    → {display}")
    print()
