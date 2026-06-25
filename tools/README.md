# 색인(인덱싱) 도구

가장 빠른 색인 통보 흐름입니다.

## 자동 생성물 (build.py 실행 시)

| 파일 | 용도 |
|---|---|
| `sitemap.xml` | 구글·네이버·빙 공통. `lastmod`·`changefreq`·`priority` 포함 |
| `rss.xml` | 네이버·빙 피드 발견 (head에 `rel="alternate"` 연결) |
| `robots.txt` | 전 검색엔진 허용 + sitemap 위치 명시 (Googlebot·Yeti·bingbot) |
| `<INDEXNOW_KEY>.txt` | IndexNow 키 검증 파일 (사이트 루트) |

## 1. 빙·네이버 즉시 통보 — IndexNow

IndexNow 한 번 제출 → Bing·Naver·Yandex·Seznam 전파. (구글 미참여)

```bash
python build.py                 # 키 파일·sitemap 생성
# 배포 후(키 파일이 라이브여야 함):
python tools/indexnow.py        # sitemap 전체 일괄 통보
python tools/indexnow.py <url>  # 글 올릴 때마다 해당 URL만 통보
```

> 키 파일 `https://hanam-home-massage.pages.dev/<KEY>.txt` 가 **배포되어 접근 가능**해야
> 통보가 수락됩니다(403이면 키 파일 미배포). 키는 `content/site.py`의 `INDEXNOW_KEY`.

## 2. 구글 — Search Console + (선택) Indexing API

- **권장**: Search Console에 사이트 등록 → `sitemap.xml` 제출 → URL 검사로 색인 요청
- 구글 sitemap **ping 엔드포인트는 2023년 폐지**되어 자동 ping은 동작하지 않습니다.
- (선택) `tools/google_index.py` — 서비스 계정으로 Indexing API 통보. 공식 지원은
  JobPosting/BroadcastEvent용이므로 일반 페이지는 Search Console 사용을 권장.

## 글 올릴 때마다 (운영 루틴)

```bash
python build.py
git add -A && git commit -m "..." && git push      # 배포
python tools/indexnow.py https://hanam-home-massage.pages.dev/<새글경로>/
```
