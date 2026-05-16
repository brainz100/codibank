# -*- coding: utf-8 -*-
"""
CodiBank — 패션 트렌드 캐시 배치
======================================================================
3일마다 GitHub Actions로 자동 실행:
  1) Brave Search API로 7도시 × 15목적 패션 트렌드 검색
  2) gpt-4.1-mini로 검색 결과 → 구체적 의상 키워드로 정제
  3) trend_cache.json 조립 → Cloudflare R2 업로드

Flask(mock_backend.py)는 요청 시점에 R2의 trend_cache.json을 우선 조회,
없거나 오래되면(6일 초과) fashion_keywords_db.json으로 자동 폴백.

필요 환경변수 (GitHub Actions Secrets):
  BRAVE_API_KEY, OPENAI_API_KEY,
  R2_BUCKET_NAME, R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
  (선택) R2_ENDPOINT — 없으면 R2_ACCOUNT_ID로 자동 구성
======================================================================
"""
import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse

# ── 7개 패션 도시 (한글 → 영문) ──
CITIES = {
    '서울': 'Seoul',
    '뉴욕': 'New York',
    '파리': 'Paris',
    '런던': 'London',
    '상파울루': 'Sao Paulo',
    '두바이': 'Dubai',
    '밀라노': 'Milan',
}

# ── 15개 코디 목적 (한글 → 영문) ──
PURPOSES = {
    '비즈니스 포멀': 'Business Formal',
    '데일리 오피스룩': 'Daily Office Look',
    '면접룩': 'Job Interview Look',
    '결혼식 하객룩': 'Wedding Guest Look',
    '소개팅룩': 'Blind Date Look',
    '로맨틱 데이트룩': 'Romantic Date Look',
    '상견례/가족모임': 'Formal Family Gathering',
    '사교 모임/파티': 'Social Party',
    '주말 나들이': 'Weekend Outing',
    '여행지 인생샷': 'Travel Photo Look',
    '꾸안꾸 데일리': 'Effortless Chic Daily',
    '스포티/애슬레저': 'Sporty Athleisure',
    '공항 패션': 'Airport Fashion',
    '미니멀/심플': 'Minimal Simple',
    '트렌디/스트릿': 'Trendy Street',
}

BRAVE_KEY = os.environ.get('BRAVE_API_KEY', '').strip()
OPENAI_KEY = os.environ.get('OPENAI_API_KEY', '').strip()


# ══════════════════════════════════════════════════════════════
# 1) Brave Search — (도시, 목적) 패션 트렌드 검색
# ══════════════════════════════════════════════════════════════
def brave_search(query, count=8):
    """Brave Search API 호출 → 검색 결과 제목+설명 텍스트 반환"""
    url = 'https://api.search.brave.com/res/v1/web/search?' + urllib.parse.urlencode({
        'q': query,
        'count': count,
        'text_decorations': 'false',
        'safesearch': 'moderate',
    })
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': BRAVE_KEY,
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            import gzip
            raw = gzip.decompress(raw)
        data = json.loads(raw.decode('utf-8'))

    items = (data.get('web') or {}).get('results') or []
    snippets = []
    for it in items:
        title = (it.get('title') or '').strip()
        desc = (it.get('description') or '').strip()
        if title or desc:
            snippets.append(f'{title} - {desc}')
    return '\n'.join(snippets[:count])


# ══════════════════════════════════════════════════════════════
# 2) LLM 정제 — 검색 결과 → 구체적 의상 키워드 15개 (men/women)
# ══════════════════════════════════════════════════════════════
def refine_keywords(city_en, purpose_ko, purpose_en, search_text):
    """gpt-4.1-mini로 검색 스니펫 → 구체적 패션 키워드 JSON"""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)

    system = (
        "You are a senior fashion editor. From real web search snippets about "
        "current fashion trends, extract CONCRETE clothing/styling keywords usable "
        "for AI image generation. STRICT RULES:\n"
        "- Only garment, fabric, silhouette, footwear, and accessory words.\n"
        "- NO mood adjectives (chic, sexy, elegant), NO makeup, NO hair, NO background.\n"
        "- Reflect the SPECIFIC city's fashion identity, not generic terms.\n"
        "- Output strict JSON only, no markdown."
    )
    user = (
        f"City: {city_en}\n"
        f"Occasion: {purpose_en}\n\n"
        f"Web search snippets (current trends):\n{search_text[:2800]}\n\n"
        f"Extract 15 men's and 15 women's concrete fashion keywords for this "
        f"city + occasion. Each keyword MUST be formatted as 'Korean(English)'.\n"
        f'Return strict JSON: {{"men": ["...x15"], "women": ["...x15"]}}'
    )
    resp = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ],
        temperature=0.8,
        response_format={'type': 'json_object'},
    )
    obj = json.loads(resp.choices[0].message.content)
    men = [str(k).strip() for k in (obj.get('men') or []) if str(k).strip()]
    women = [str(k).strip() for k in (obj.get('women') or []) if str(k).strip()]
    if len(men) < 8 or len(women) < 8:
        raise ValueError(f'키워드 부족 (men={len(men)}, women={len(women)})')
    return {'men': men[:15], 'women': women[:15]}


# ══════════════════════════════════════════════════════════════
# 3) R2 업로드
# ══════════════════════════════════════════════════════════════
def upload_to_r2(data_bytes):
    """trend_cache.json을 R2 버킷 루트에 업로드"""
    import boto3
    bucket = os.environ['R2_BUCKET_NAME']
    endpoint = os.environ.get('R2_ENDPOINT', '').strip()
    if not endpoint:
        acct = os.environ['R2_ACCOUNT_ID']
        endpoint = f'https://{acct}.r2.cloudflarestorage.com'
    client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
        region_name='auto',
    )
    client.put_object(
        Bucket=bucket,
        Key='trend_cache.json',
        Body=data_bytes,
        ContentType='application/json',
        CacheControl='no-cache',
    )


# ══════════════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════════════
def main():
    if not BRAVE_KEY:
        print('ERROR: BRAVE_API_KEY 환경변수 누락', flush=True)
        sys.exit(1)
    if not OPENAI_KEY:
        print('ERROR: OPENAI_API_KEY 환경변수 누락', flush=True)
        sys.exit(1)

    print('=' * 60, flush=True)
    print('CodiBank 트렌드 캐시 배치 시작', flush=True)
    print(f'  대상: {len(CITIES)}도시 × {len(PURPOSES)}목적 = '
          f'{len(CITIES) * len(PURPOSES)}건', flush=True)
    print('=' * 60, flush=True)

    city_keywords = {}
    ok, fail = 0, 0

    for city_ko, city_en in CITIES.items():
        city_keywords[city_ko] = {}
        for purpose_ko, purpose_en in PURPOSES.items():
            query = f'{city_en} {purpose_en} fashion outfit trend 2026'
            try:
                search_text = brave_search(query)
                if not search_text:
                    raise ValueError('빈 검색 결과')
                kw = refine_keywords(city_en, purpose_ko, purpose_en, search_text)
                city_keywords[city_ko][purpose_ko] = kw
                ok += 1
                print(f'  OK  {city_ko}/{purpose_ko}: '
                      f'men {len(kw["men"])} / women {len(kw["women"])}', flush=True)
            except Exception as e:
                fail += 1
                # 실패한 셀은 키를 넣지 않음 → Flask가 정적 DB로 자동 폴백
                print(f'  !!  {city_ko}/{purpose_ko} 실패: {e}', flush=True)
            time.sleep(1.2)  # Brave/OpenAI rate limit 여유

    cache = {
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'source': 'brave_search + gpt-4.1-mini',
        'cities': list(CITIES.keys()),
        'purposes': list(PURPOSES.keys()),
        'stats': {'ok': ok, 'fail': fail},
        'city_keywords': city_keywords,
    }
    body = json.dumps(cache, ensure_ascii=False, indent=2).encode('utf-8')

    try:
        upload_to_r2(body)
        print('=' * 60, flush=True)
        print(f'완료: 성공 {ok} / 실패 {fail}', flush=True)
        print(f'R2 업로드: trend_cache.json ({len(body):,} bytes)', flush=True)
        print('=' * 60, flush=True)
    except Exception as e:
        print(f'ERROR: R2 업로드 실패: {e}', flush=True)
        sys.exit(1)

    # 전부 실패면 워크플로 실패 처리 (캐시 갱신 안 함)
    if ok == 0:
        print('ERROR: 모든 셀 실패 — 캐시 신뢰 불가', flush=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
