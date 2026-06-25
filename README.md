# 하남 출장마사지 사이트

경기도 하남시 전지역 방문 관리 서비스(출장마사지·홈타이) 안내 정적 사이트입니다.
하남은 행정구가 없는 도시이므로 **하남 메인 → 대표 지역 → 역세권 → 생활권 → 예약 안내** 구조로 구성합니다.

**상호**: 바로 GO
**예약전화**: 0508-202-4719
**메인 URL**: `/gyeonggi/hanam/`

## 구조

- **정적 HTML 사이트** — GitHub Pages / Cloudflare Pages / 일반 웹서버 어디서든 그대로 서빙
- **build.py** + **content/** — 페이지를 Python으로 정의하고 정적 HTML 생성
- **생성물** — 각 디렉터리의 `index.html`, `sitemap.xml`, `robots.txt`

```
build.py                    # 빌드 스크립트 (헤더·푸터·스키마 자동 주입)
content/
  site.py                  # 상호·전화·도메인·상단 메뉴(NAV)
  root.py                  # 루트(/) → /gyeonggi/hanam/ 리다이렉트
  main.py                  # 하남 메인 페이지 (히어로·FAQ)
  areas.py                 # 지역 페이지 16개
  stations.py              # 역세권 페이지 8개
  areas_and_stations.py    # 생활권 페이지 13개
  info.py                  # 정보 페이지 5개 (예약·확인사항·가이드·고객센터·약관)
assets/
  style.css                # 프리미엄 다크 + 오렌지 + Pretendard, 글래스 오버레이
  nav.js                   # 모바일 네비게이션
gyeonggi/hanam/...          # 생성된 페이지
```

## 빌드

```bash
python3 build.py
```

빌드 시 페이지별 본문 글자수 리포트가 출력됩니다.

## 페이지 구성 (총 43개 + 루트 리다이렉트)

- 메인 1 / 지역 16 / 역세권 8 / 생활권 13 / 정보 5
- 핵심 역세권: 미사역, 하남풍산역, 하남시청역, 하남검단산역
- 강일역·상일동역·마천역·둔촌오륜역은 서울 강동·송파 성격이 강해 **인접 생활권 이동 기준**으로만 안내
- 위례동·감일동은 송파·강동이 아닌 **하남 기준**으로 작성

## SEO 운영 원칙

- 본문 **2,000자 미만 페이지는 자동 `noindex`** 처리 (build.py)
- 메뉴명·URL에 "출장마사지" 반복 없음 — Title·H1·첫 문단·메타 설명에서만 자연스럽게 사용
- 메타 설명 80자 이내
- 모든 페이지 본문 고유 작성 (지역명만 바꾼 복제 없음)
- 내부 링크 롱테일 강화 + 권위 외부 링크(E-E-A-T)
- JSON-LD 스키마: Organization / WebPage / BreadcrumbList (전 페이지 자동), 메인은 HealthAndBeautyBusiness · FAQPage 추가
- 방문형(오프라인 사업장 주소 없음)이므로 LocalBusiness 스키마 미사용

## 롱테일 내부링크 & 후기·평점

- 메인·지역·역세권·생활권·정보 전 페이지에 **롱테일 관련 안내 카드 블록**(`render_related`) 자동 삽입 — 주제별(방문 가능 지역·예약 전 확인·생활권 안내) 앵커로 내부링크 강화
- 전 서비스 페이지(개인정보처리방침·루트 제외)에 **이용 후기 섹션 + Service·AggregateRating·Review 스키마** 자동 삽입(`render_reviews`/`make_service_schema`)
- ⚠️ **표시 후기·별점은 예시입니다.** 구글 정책상 가짜 평점은 페널티 위험이 있으므로, 운영 시 `build.py`의 `_REVIEW_POOL`을 **실제 고객 후기로 교체**하세요. 후기가 없다면 `_reviews_eligible()`을 `return False`로 두면 마크업이 비활성화됩니다.

## 푸터

- 오렌지 컬러 버튼 **웹사이트 제작문의 · 제휴문의** → 텔레그램(`https://t.me/googleseolab`) 연결

## 배포 전 할 일

1. `content/site.py`의 `BASE_URL`을 실제 도메인으로 변경
2. `python3 build.py` 재실행
3. `assets/og-image.png` (1200×630) 추가 — 선호 썸네일 지정용
4. Google Search Console에 `sitemap.xml` 제출
