#!/usr/bin/env python3
"""IndexNow 일괄 색인 통보 — 빙·네이버·얀덱스 등 즉시 통보.

IndexNow는 한 번의 제출로 참여 검색엔진(Bing, Naver, Yandex, Seznam)에
모두 전파됩니다. ※ 구글은 IndexNow에 참여하지 않습니다(구글은 Search Console /
Indexing API 사용 — tools/google_index.py 참고).

사용법:
  # 1) 전체 URL 일괄 통보 (sitemap.xml 기반)
  python tools/indexnow.py

  # 2) 특정 URL만 통보 (글 올릴 때마다)
  python tools/indexnow.py https://hanam-home-massage.pages.dev/misa-area/ \
                           https://hanam-home-massage.pages.dev/reservation/

키 파일은 빌드 시 사이트 루트에 자동 생성됩니다:
  https://hanam-home-massage.pages.dev/<INDEXNOW_KEY>.txt
"""
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from content.site import BASE_URL, INDEXNOW_KEY  # noqa: E402

BASE = BASE_URL.rstrip("/")
HOST = re.sub(r"^https?://", "", BASE).split("/")[0]
KEY_LOCATION = f"{BASE}/{INDEXNOW_KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"  # 단일 제출 → 전 참여 엔진 전파


def sitemap_urls():
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        sys.exit("sitemap.xml 없음 — 먼저 `python build.py` 를 실행하세요.")
    with open(path, encoding="utf-8") as f:
        return re.findall(r"<loc>(.*?)</loc>", f.read())


def submit(urls):
    urls = [u for u in urls if u.startswith(BASE)]
    if not urls:
        sys.exit("통보할 URL이 없습니다.")
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    print(f"→ {len(urls)}개 URL을 IndexNow로 통보 ({HOST})")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
    # 200=수신, 202=수락(검증 대기). 그 외는 키 파일/호스트 확인.
    print(f"  응답 코드: {code}", {
        200: "OK (수신 완료)",
        202: "Accepted (키 검증 후 처리)",
        400: "잘못된 요청",
        403: "키 불일치 — 키 파일 배포 확인",
        422: "URL/호스트 불일치",
        429: "요청 과다 — 잠시 후 재시도",
    }.get(code, ""))
    return code


if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else sitemap_urls()
    submit(targets)
