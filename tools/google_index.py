#!/usr/bin/env python3
"""구글 Indexing API 통보 (선택) — 구글은 IndexNow 미참여.

⚠️ 사전 준비
  1) Google Cloud 콘솔에서 프로젝트 생성 → "Indexing API" 사용 설정
  2) 서비스 계정 생성 → JSON 키 다운로드
  3) Search Console에서 해당 사이트 속성에 서비스 계정 이메일을
     '소유자'로 추가
  4) pip install google-auth requests

⚠️ 정책 주의
  구글 Indexing API는 공식적으로 JobPosting / BroadcastEvent 페이지용입니다.
  일반 페이지에도 동작은 하지만 공식 지원 대상이 아니므로, 일반 색인은
  sitemap.xml + Search Console URL 검사 도구 사용을 권장합니다.

사용법:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/service-account.json
  python tools/google_index.py                # sitemap 전체
  python tools/google_index.py <url> [<url>]  # 특정 URL
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from content.site import BASE_URL  # noqa: E402

BASE = BASE_URL.rstrip("/")
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def sitemap_urls():
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        sys.exit("sitemap.xml 없음 — 먼저 `python build.py` 실행.")
    with open(path, encoding="utf-8") as f:
        return re.findall(r"<loc>(.*?)</loc>", f.read())


def main(urls):
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("pip install google-auth requests 필요")

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS 환경변수에 서비스 계정 JSON 경로 지정 필요")

    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    session = AuthorizedSession(creds)

    urls = [u for u in urls if u.startswith(BASE)]
    ok = 0
    for u in urls:
        r = session.post(ENDPOINT, json={"url": u, "type": "URL_UPDATED"})
        status = "OK" if r.status_code == 200 else f"FAIL {r.status_code}"
        if r.status_code == 200:
            ok += 1
        print(f"  [{status}] {u}")
    print(f"\n{ok}/{len(urls)} 통보 완료")


if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else sitemap_urls()
    main(targets)
