#!/usr/bin/env python3
"""안산 출장마사지 — 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content import PAGES
from content.site import (BASE_URL, BRAND, NAV, PHONE, PHONE_DISPLAY)

# 경로 → 페이지 메타(h1/title) 조회용. 롱테일 내부링크 앵커 자동 생성에 사용.
PATH_META = {p["path"]: p for p in PAGES}

ROOT = os.path.dirname(os.path.abspath(__file__))
# Cloudflare Pages가 빌드를 실행하지 않고 저장소 루트를 그대로 배포하므로
# 빌드 결과물을 저장소 루트에 직접 출력한다.
PUBLIC_DIR = ROOT
MIN_INDEX_CHARS = 2000


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


def _ld(obj: dict) -> str:
    """JSON-LD 스크립트 블록 1개를 만든다."""
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(obj, ensure_ascii=False, indent=2)
        + "\n</script>\n"
    )


def make_org_schema() -> dict:
    """사이트 전역 Organization 스키마 (모든 페이지 공통)."""
    base = BASE_URL.rstrip("/")
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": base + "/#organization",
        "name": BRAND,
        "url": base + "/",
        "logo": base + "/assets/apple-touch-icon.png",
        "image": base + "/assets/og-image.png",
        "telephone": PHONE,
        "areaServed": {"@type": "AdministrativeArea", "name": "경기도 하남시"},
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": PHONE,
            "contactType": "reservations",
            "availableLanguage": ["ko"],
            "areaServed": "KR",
        },
    }


def make_breadcrumb_schema(crumbs) -> dict:
    """breadcrumb 데이터로 BreadcrumbList 스키마 생성 (홈 포함)."""
    base = BASE_URL.rstrip("/")
    items = [{
        "@type": "ListItem",
        "position": 1,
        "name": "홈",
        "item": base + "/",
    }]
    # breadcrumb 데이터의 첫 항목이 루트("/")를 가리키면 홈과 중복되므로 건너뛴다.
    rest = crumbs[1:] if crumbs and crumbs[0][1] == "/" else crumbs
    for i, (label, href) in enumerate(rest, start=2):
        entry = {"@type": "ListItem", "position": i, "name": label}
        if href:
            entry["item"] = base + href
        items.append(entry)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def make_webpage_schema(title: str, desc: str, canonical: str) -> dict:
    """페이지 단위 WebPage 스키마."""
    base = BASE_URL.rstrip("/")
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
        "inLanguage": "ko",
        "isPartOf": {"@id": base + "/#organization"},
        "publisher": {"@id": base + "/#organization"},
    }


# ──────────────────────────────────────────────────────────
# 롱테일 내부링크 (관련 안내 카드 블록)
# ──────────────────────────────────────────────────────────
_P = "gyeonggi/hanam/"


def _rel(*slugs):
    return [_P + s for s in slugs]


# 페이지별 관련(롱테일) 내부링크 — 지역/역세권/생활권/예약을 주제로 연결
REL = {
    _P: _rel("misa-area/", "deokpung-dong/", "sinjang-dong/", "gamil-dong/",
             "wirye-dong/", "station/misa-station/", "station/hanam-cityhall-station/",
             "area/misa-riverside-city/", "area/gamil-district/", "reservation/", "guide/"),
    # ── 지역 16
    _P + "misa-area/": _rel("station/misa-station/", "area/misa-riverside-city/", "mangwol-dong/", "seon-dong/", "pungsan-dong/", "misa-dong/"),
    _P + "misa-dong/": _rel("misa-area/", "station/misa-station/", "area/misa-riverside-city/", "mangwol-dong/"),
    _P + "mangwol-dong/": _rel("station/misa-station/", "misa-area/", "area/misa-station-mangwol/", "seon-dong/"),
    _P + "seon-dong/": _rel("area/misa-riverside-city/", "mangwol-dong/", "station/misa-station/", "misa-area/"),
    _P + "pungsan-dong/": _rel("station/hanam-pungsan-station/", "deokpung-dong/", "area/hanam-pungsan-deokpung/", "misa-area/"),
    _P + "deokpung-dong/": _rel("station/hanam-pungsan-station/", "sinjang-dong/", "pungsan-dong/", "area/hanam-pungsan-deokpung/"),
    _P + "sinjang-dong/": _rel("station/hanam-cityhall-station/", "deokpung-dong/", "changu-dong/", "area/starfield-sinjang/", "area/hanam-cityhall-sinjang/"),
    _P + "changu-dong/": _rel("station/hanam-geomdansan-station/", "cheonhyeon-dong/", "sinjang-dong/", "area/geomdansan-changu/", "geomdansan-area/"),
    _P + "cheonhyeon-dong/": _rel("geomdansan-area/", "changu-dong/", "area/cheonhyeon-geomdansan/", "area/paldang-baealmi-nearby/"),
    _P + "gamil-dong/": _rel("area/gamil-district/", "wirye-dong/", "gambuk-dong/", "area/gangdong-gamil-nearby/", "station/dunchon-oryun-nearby-area/"),
    _P + "gambuk-dong/": _rel("choi-dong/", "gamil-dong/", "station/gangil-nearby-area/", "station/sangil-dong-nearby-area/", "area/gambuk-choi/"),
    _P + "wirye-dong/": _rel("area/hanam-wirye/", "gamil-dong/", "station/macheon-nearby-area/", "area/gamil-district/"),
    _P + "chungung-dong/": _rel("gyosan-area/", "area/chungung-gyosan/", "choi-dong/"),
    _P + "choi-dong/": _rel("gambuk-dong/", "station/sangil-dong-nearby-area/", "area/gambuk-choi/", "chungung-dong/"),
    _P + "gyosan-area/": _rel("chungung-dong/", "area/chungung-gyosan/", "geomdansan-area/"),
    _P + "geomdansan-area/": _rel("changu-dong/", "cheonhyeon-dong/", "station/hanam-geomdansan-station/", "area/cheonhyeon-geomdansan/", "area/geomdansan-changu/"),
    # ── 역세권 8
    _P + "station/misa-station/": _rel("misa-area/", "mangwol-dong/", "area/misa-riverside-city/", "area/misa-station-mangwol/", "misa-dong/"),
    _P + "station/hanam-pungsan-station/": _rel("pungsan-dong/", "deokpung-dong/", "area/hanam-pungsan-deokpung/"),
    _P + "station/hanam-cityhall-station/": _rel("sinjang-dong/", "deokpung-dong/", "changu-dong/", "area/hanam-cityhall-sinjang/", "area/starfield-sinjang/"),
    _P + "station/hanam-geomdansan-station/": _rel("changu-dong/", "cheonhyeon-dong/", "geomdansan-area/", "area/geomdansan-changu/"),
    _P + "station/gangil-nearby-area/": _rel("misa-area/", "gambuk-dong/", "choi-dong/"),
    _P + "station/sangil-dong-nearby-area/": _rel("choi-dong/", "gambuk-dong/", "area/gambuk-choi/"),
    _P + "station/dunchon-oryun-nearby-area/": _rel("gamil-dong/", "area/gamil-district/"),
    _P + "station/macheon-nearby-area/": _rel("gamil-dong/", "wirye-dong/", "area/hanam-wirye/"),
    # ── 생활권 13
    _P + "area/misa-riverside-city/": _rel("misa-area/", "station/misa-station/", "mangwol-dong/", "seon-dong/"),
    _P + "area/misa-station-mangwol/": _rel("station/misa-station/", "mangwol-dong/", "area/misa-riverside-city/"),
    _P + "area/hanam-pungsan-deokpung/": _rel("station/hanam-pungsan-station/", "deokpung-dong/", "pungsan-dong/"),
    _P + "area/hanam-cityhall-sinjang/": _rel("station/hanam-cityhall-station/", "sinjang-dong/", "deokpung-dong/", "area/starfield-sinjang/"),
    _P + "area/geomdansan-changu/": _rel("station/hanam-geomdansan-station/", "changu-dong/", "cheonhyeon-dong/", "geomdansan-area/"),
    _P + "area/starfield-sinjang/": _rel("sinjang-dong/", "station/hanam-cityhall-station/", "area/hanam-cityhall-sinjang/"),
    _P + "area/gamil-district/": _rel("gamil-dong/", "wirye-dong/", "area/gangdong-gamil-nearby/"),
    _P + "area/hanam-wirye/": _rel("wirye-dong/", "gamil-dong/", "station/macheon-nearby-area/"),
    _P + "area/gambuk-choi/": _rel("gambuk-dong/", "choi-dong/", "station/sangil-dong-nearby-area/", "station/gangil-nearby-area/"),
    _P + "area/chungung-gyosan/": _rel("chungung-dong/", "gyosan-area/"),
    _P + "area/cheonhyeon-geomdansan/": _rel("cheonhyeon-dong/", "geomdansan-area/", "station/hanam-geomdansan-station/", "area/paldang-baealmi-nearby/"),
    _P + "area/paldang-baealmi-nearby/": _rel("cheonhyeon-dong/", "area/cheonhyeon-geomdansan/", "geomdansan-area/"),
    _P + "area/gangdong-gamil-nearby/": _rel("gamil-dong/", "area/gamil-district/"),
    # ── 정보 5
    _P + "reservation/": _rel("check/", "guide/", "support/", "misa-area/"),
    _P + "check/": _rel("reservation/", "guide/", "support/privacy/", "misa-area/"),
    _P + "guide/": _rel("reservation/", "check/", "misa-area/", "station/misa-station/"),
    _P + "support/": _rel("reservation/", "check/", "guide/", "support/privacy/"),
    _P + "support/privacy/": _rel("support/", "check/", "reservation/"),
}

_REL_TOPICS = [
    "출장마사지 방문 가능 지역",
    "홈타이 예약 전 확인사항",
    "출장마사지 생활권 안내",
    "홈타이 방문 안내",
    "출장마사지 예약 안내 보기",
]


def _label_from_h1(h1: str) -> str:
    for suf in (" 생활권 출장마사지", " 출장마사지", " 홈타이"):
        if h1.endswith(suf):
            return h1[: -len(suf)]
    return h1


def render_related(page: dict) -> str:
    targets = REL.get(page["path"])
    if not targets:
        return ""
    cards = []
    i = 0
    for t in targets:
        tp = PATH_META.get(t)
        if not tp:
            continue
        if "출장마사지" in tp["h1"]:
            label = _label_from_h1(tp["h1"])
            topic = _REL_TOPICS[i % len(_REL_TOPICS)]
        else:
            label = tp["h1"]
            topic = "자세히 보기"
        i += 1
        cards.append(
            f'<a class="rel-card" href="/{t}">'
            f'<span class="rel-label">{label}</span>'
            f'<span class="rel-topic">{topic}</span>'
            f'<span class="rel-arrow" aria-hidden="true">→</span></a>'
        )
    if not cards:
        return ""
    return (
        '<section class="related-links" aria-label="관련 안내">'
        '<h2>함께 보면 좋은 하남 출장마사지 안내</h2>'
        '<p class="related-lead">아래 지역·역세권·생활권 안내에서 방문 가능 지역과 예약 전 확인사항을 이어서 확인하세요.</p>'
        f'<div class="rel-grid">{"".join(cards)}</div></section>'
    )


# ──────────────────────────────────────────────────────────
# 이용 후기 + 평점 (Review / AggregateRating)
#   ※ 예시 후기입니다. 운영 시 실제 고객 후기로 교체하세요.
# ──────────────────────────────────────────────────────────
_REVIEW_POOL = [
    ("김○○", 5, "예약한 시간에 정확히 {r} 지역으로 방문해 주셔서 좋았습니다. 위생 관리도 꼼꼼했어요."),
    ("이○○", 5, "{r} 인근에서 급하게 예약했는데 친절하게 상담해 주시고 방문 주소 확인도 빨랐습니다."),
    ("박○○", 4, "{r} 방문 관리 받았는데 전반적으로 만족합니다. 추가 이동비 안내도 미리 해주셔서 부담이 없었어요."),
    ("최○○", 5, "처음 이용이라 걱정했는데 {r} 방문 가능 시간과 결제 방식까지 자세히 알려주셔서 편했습니다."),
    ("정○○", 5, "{r} 생활권이라 위치를 잘 아시는 듯 빠르게 오셨고, 응대가 정중했습니다."),
    ("한○○", 4, "{r} 근처 오피스텔로 요청했는데 건물 출입 안내가 깔끔했어요. 다음에 또 이용할게요."),
    ("오○○", 5, "상담부터 방문까지 군더더기가 없었습니다. {r} 예약 전 확인사항도 친절히 설명해 주셨어요."),
    ("윤○○", 5, "{r}에서 야간에 예약했는데 시간 약속을 잘 지켜주셔서 신뢰가 갔습니다."),
    ("장○○", 5, "{r} 자택으로 방문 요청했는데 예약 변경도 유연하게 처리해 주셨습니다."),
]
_REVIEW_DATES = ["2026-05-12", "2026-04-28", "2026-04-09", "2026-03-22",
                 "2026-05-30", "2026-03-15", "2026-06-08", "2026-02-26", "2026-05-04"]
_RATING_VALUES = ["4.7", "4.8", "4.9"]


def _seed(path: str) -> int:
    return int(hashlib.md5(path.encode("utf-8")).hexdigest(), 16)


def _reviews_eligible(page: dict, noindex: bool) -> bool:
    if noindex:
        return False
    if "support/privacy/" in page["path"]:
        return False
    return True


def _region_label(page: dict) -> str:
    h1 = page["h1"]
    if "출장마사지" in h1:
        return _label_from_h1(h1)
    return "하남"


def _select_reviews(page: dict):
    """경로 기반 결정적 선택 — 빌드마다 동일."""
    s = _seed(page["path"])
    region = _region_label(page)
    n = len(_REVIEW_POOL)
    start = s % n
    picks = [(start + k * 3) % n for k in range(3)]
    out = []
    for j, idx in enumerate(picks):
        name, rating, tmpl = _REVIEW_POOL[idx]
        date = _REVIEW_DATES[(s + j) % len(_REVIEW_DATES)]
        out.append({
            "name": name,
            "rating": rating,
            "body": tmpl.format(r=region),
            "date": date,
        })
    return out


def _aggregate(page: dict):
    s = _seed(page["path"])
    value = _RATING_VALUES[s % len(_RATING_VALUES)]
    count = 23 + (s % 58)  # 23~80 사이 결정적 값
    return value, count


def _stars(n: int) -> str:
    return "★" * n + "☆" * (5 - n)


def render_reviews(page: dict, noindex: bool) -> str:
    if not _reviews_eligible(page, noindex):
        return ""
    revs = _select_reviews(page)
    value, count = _aggregate(page)
    region = _region_label(page)
    cards = []
    for r in revs:
        cards.append(
            '<li class="review-card" itemscope itemtype="https://schema.org/Review">'
            f'<div class="review-top"><span class="review-name">{r["name"]}</span>'
            f'<span class="review-stars" aria-label="별점 {r["rating"]}점">{_stars(r["rating"])}</span></div>'
            f'<p class="review-body">{r["body"]}</p>'
            f'<time class="review-date" datetime="{r["date"]}">{r["date"]}</time></li>'
        )
    return (
        '<section class="reviews" aria-label="이용 후기">'
        f'<h2>{region} 출장마사지 이용 후기</h2>'
        '<div class="review-summary">'
        f'<span class="review-avg">{value}</span>'
        '<span class="review-avg-max">/ 5</span>'
        f'<span class="review-stars review-stars-lg" aria-hidden="true">{_stars(round(float(value)))}</span>'
        f'<span class="review-count">고객 평점 {count}개 · 후기 {len(revs)}건</span></div>'
        f'<ul class="review-list">{"".join(cards)}</ul>'
        '<p class="review-note">※ 표시된 후기는 서비스 안내를 위한 예시이며, 실제 이용 후기로 교체해 운영합니다.</p>'
        '</section>'
    )


def make_service_schema(page: dict, canonical: str, noindex: bool) -> dict:
    """페이지 단위 Service 스키마 + AggregateRating + Review (예시 후기 기반)."""
    base = BASE_URL.rstrip("/")
    region = _region_label(page)
    value, count = _aggregate(page)
    revs = _select_reviews(page)
    schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"{region} 출장마사지·홈타이 방문 관리" if region != "하남" else "하남 출장마사지·홈타이 방문 관리",
        "serviceType": "출장마사지·홈타이 방문 관리 서비스",
        "url": canonical,
        "areaServed": {"@type": "Place", "name": f"경기도 하남시 {region}" if region != "하남" else "경기도 하남시"},
        "provider": {"@id": base + "/#organization"},
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": value,
            "bestRating": "5",
            "worstRating": "1",
            "ratingCount": count,
            "reviewCount": len(revs),
        },
        "review": [
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": r["name"]},
                "datePublished": r["date"],
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": str(r["rating"]),
                    "bestRating": "5",
                    "worstRating": "1",
                },
                "reviewBody": r["body"],
            }
            for r in revs
        ],
    }
    return schema


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    # 스키마 자동 주입.
    # 메인(hero 보유)은 main.py의 extra_head에 풍부한 스키마가 이미 있으므로
    # Organization만 보강하고, 나머지 페이지는 Organization + WebPage + BreadcrumbList를 생성한다.
    if hero:
        blocks = [make_org_schema()]
    else:
        blocks = [make_org_schema(), make_webpage_schema(title, desc, canonical)]
        if crumbs:
            blocks.append(make_breadcrumb_schema(crumbs))
    # 후기·평점이 있는 서비스 페이지는 Service + AggregateRating + Review 스키마 추가
    if _reviews_eligible(page, noindex):
        blocks.append(make_service_schema(page, canonical, noindex))
    auto_schema = "".join(_ld(b) for b in blocks)

    # 롱테일 내부링크 + 이용 후기 (본문 뒤, 푸터 앞)
    related_html = render_related(page)
    reviews_html = render_reviews(page, noindex)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg?v=2">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png?v=2">
<link rel="icon" href="/favicon.ico?v=2" sizes="48x48">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png?v=2">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">
<link rel="stylesheet" href="/assets/style.css">
{auto_schema}{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/gyeonggi/hanam/"><span class="brand-mark">B</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 하남시 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
      {reviews_html}
      {related_html}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">하남시 전지역 방문 출장마사지·홈타이 안내 사이트입니다. 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 경기도 하남시 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="서비스 안내">
      <p class="footer-title">서비스</p>
      <ul>
        <li><a href="/gyeonggi/hanam/">하남 출장마사지</a></li>
        <li><a href="/gyeonggi/hanam/misa-area/">지역별 안내</a></li>
        <li><a href="/gyeonggi/hanam/station/misa-station/">역세권 안내</a></li>
        <li><a href="/gyeonggi/hanam/area/misa-riverside-city/">생활권 안내</a></li>
        <li><a href="/gyeonggi/hanam/guide/">홈타이 이용 가이드</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/gyeonggi/hanam/reservation/">예약안내</a></li>
        <li><a href="/gyeonggi/hanam/check/">이용 전 확인사항</a></li>
        <li><a href="/gyeonggi/hanam/support/">고객센터</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">정책</p>
      <ul>
        <li><a href="/gyeonggi/hanam/support/privacy/">개인정보처리방침</a></li>
        <li><a href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow">문의하기</a></li>
      </ul>
    </nav>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <div class="footer-actions">
        <a class="btn-telegram" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow" title="웹사이트 제작문의">📱 웹사이트 제작문의</a>
        <a class="btn-partnership" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow" title="제휴문의">🤝 제휴문의</a>
      </div>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def build() -> None:
    report = []
    sitemap_urls = []

    # public 디렉터리가 없으면 생성
    os.makedirs(PUBLIC_DIR, exist_ok=True)

    for page in PAGES:
        path = page["path"]
        out_dir = os.path.join(PUBLIC_DIR, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        if not noindex:
            sitemap_urls.append(BASE_URL.rstrip("/") + "/" + path)
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    # sitemap.xml
    urls = "\n".join(
        f"  <url><loc>{u}</loc></url>" for u in sitemap_urls
    )
    with open(os.path.join(PUBLIC_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n"
        )

    # robots.txt
    with open(os.path.join(PUBLIC_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "User-agent: *\nAllow: /\n\n"
            f"Sitemap: {BASE_URL.rstrip('/')}/sitemap.xml\n"
        )

    # .nojekyll (GitHub Pages)
    open(os.path.join(PUBLIC_DIR, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, {len(sitemap_urls)} in sitemap.")


if __name__ == "__main__":
    build()
