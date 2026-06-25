import json
from .site import BRAND, BASE_URL, PHONE

_BASE = BASE_URL.rstrip("/")

# 메타 설명 (80자 이내)
DESC = "하남 출장마사지·홈타이 예약 전 미사, 감일, 위례, 덕풍, 신장, 하남검단산 생활권을 확인하세요."

# 자주 묻는 질문 (FAQ 스키마)
_FAQ = [
    ("하남은 구별 페이지를 만들어야 하나요?",
     "하남은 행정구가 없으므로 구별 페이지를 만들지 않습니다. 하남 메인, 대표 지역, 역세권, 생활권 구조로 안내하며, 미사·감일·위례·덕풍·신장·하남검단산 생활권을 먼저 확인하면 됩니다."),

    ("미사1동, 미사2동, 미사3동을 각각 확인해야 하나요?",
     "1차 안내에서는 미사 생활권으로 묶어 안내합니다. 미사강변도시, 망월동, 선동, 풍산동 인접권을 함께 설명하므로, 미사 생활권 페이지에서 방문 가능 지역을 확인하는 방식이 좋습니다."),

    ("위례동은 송파 위례와 같은 지역인가요?",
     "위례는 하남·송파·성남으로 행정구역이 나뉩니다. 본 안내는 하남 위례 기준이며, 송파 위례·성남 위례는 별도 행정구역이므로 인접 생활권으로만 설명합니다."),

    ("예약 전 꼭 확인해야 할 사항은 무엇인가요?",
     "방문 가능 주소, 예약 가능 시간, 추가 이동비 여부, 건물 출입 방식, 자택·숙소·오피스텔 이용 기준, 결제 방식, 예약 변경 기준, 개인정보 처리 기준을 먼저 확인하고 예약하는 방식이 좋습니다."),

    ("강일역이나 상일동역도 하남 역세권인가요?",
     "강일역과 상일동역은 서울 강동구 성격이 강해 하남에서는 감북·초이·미사 인접 생활권으로만 안내합니다. 마천역은 송파 성격이 강해 감일·하남 위례 인접권으로만 설명합니다."),
]

_faq_schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "@id": f"#faq-{i+1}",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for i, (q, a) in enumerate(_FAQ)
    ],
}
_faq_schema_str = json.dumps(_faq_schema, ensure_ascii=False, indent=2)

# Organization 스키마 (오프라인 주소 없는 방문형이므로 LocalBusiness 미사용)
_org_schema = {
    "@context": "https://schema.org",
    "@type": "HealthAndBeautyBusiness",
    "name": BRAND,
    "telephone": PHONE,
    "url": _BASE + "/",
    "image": _BASE + "/assets/og-image.png",
    "description": "하남시 출장마사지·홈타이 안내 사이트",
    "areaServed": {"@type": "AdministrativeArea", "name": "경기도 하남시"},
    "openingHoursSpecification": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "00:00",
        "closes": "23:59",
    },
}
_org_schema_str = json.dumps(_org_schema, ensure_ascii=False, indent=2)

_breadcrumb_schema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "하남 출장마사지", "item": _BASE + "/"},
    ],
}
_breadcrumb_schema_str = json.dumps(_breadcrumb_schema, ensure_ascii=False, indent=2)

_EXTRA_HEAD = f"""<script type="application/ld+json">
{_org_schema_str}
</script>
<script type="application/ld+json">
{_breadcrumb_schema_str}
</script>
<script type="application/ld+json">
{_faq_schema_str}
</script>"""

_HERO = """<div class="hero">
  <div class="hero-content">
    <div class="hero-badge">하남시 전지역 방문 관리</div>
    <h1 class="hero-title">하남 출장마사지<br><span class="hero-accent">하남 홈타이</span><br>지역별 예약 안내</h1>
    <p class="hero-lead">미사, 감일, 위례, 덕풍, 신장, 하남검단산, 하남시청역 생활권별 방문 가능 지역과 예약 전 확인사항을 안내합니다.</p>
    <div class="hero-cta">
      <a href="#areas" class="btn btn-primary">지역별 안내 보기</a>
      <a href="#stations" class="btn btn-secondary">가까운 역 찾기</a>
      <a href="/reservation/" class="btn btn-secondary">예약 안내 보기</a>
      <a href="/check/" class="btn btn-secondary">이용 전 확인사항</a>
    </div>
  </div>
  <div class="hero-stats">
    <div class="stat"><div class="stat-number">16</div><div class="stat-label">지역 페이지</div></div>
    <div class="stat"><div class="stat-number">8</div><div class="stat-label">역세권 안내</div></div>
    <div class="stat"><div class="stat-number">13</div><div class="stat-label">생활권 안내</div></div>
    <div class="stat"><div class="stat-number">24H</div><div class="stat-label">상담 가능</div></div>
  </div>
</div>"""

PAGE = {
    "path": "",
    "title": "하남 출장마사지｜미사·감일·위례·덕풍 홈타이 지역 안내",
    "desc": DESC,
    "h1": "하남 출장마사지 · 하남 홈타이 지역별 예약 안내",
    "hero": _HERO,
    "breadcrumb": [],
    "extra_head": _EXTRA_HEAD,
    "body": """
<section id="criteria">
  <h2>하남에서 출장마사지를 찾을 때 먼저 확인할 기준</h2>
  <p>하남시는 경기도 동부, 서울 강동·송파와 맞닿은 한강변 도시입니다. 행정구가 따로 없는 도시이기 때문에 구 단위로 지역을 나누지 않고, 생활권 단위로 방문 가능 지역을 확인하는 것이 출장마사지 예약 과정에서 가장 중요한 첫 번째 기준이 됩니다. 같은 하남시 안에서도 미사강변도시 신도시 생활권과 검단산 인접 외곽 생활권은 이동 거리와 예약 조건이 크게 다르기 때문입니다.</p>
  <p>미사는 미사역과 미사강변도시를 중심으로 한 신도시 생활권으로, 망월동·선동·풍산동까지 이어지는 한강변 주거지입니다. 덕풍과 신장은 하남풍산역·하남시청역과 스타필드 하남 인접 생활권으로, 하남 원도심과 상권이 모여 있는 중심권입니다. 감일과 위례는 서울 송파·강동과 인접해 검색 의도가 겹칠 수 있으므로, 예약 전에 하남 기준의 방문 가능 지역인지 분명히 확인하는 것이 좋습니다.</p>
  <p>천현, 춘궁, 초이, 감북은 역세권보다 차량 이동 기준과 추가 이동비 확인이 더 중요한 외곽 생활권입니다. 이런 지역은 방문 가능 주소와 예약 가능 시간을 먼저 확인하고, 기본 이동권 범위 안에 있는지 점검한 뒤 예약하면 과정이 한결 수월합니다. 아래 안내에서 자신의 위치에 맞는 대표 지역·역세권·생활권을 차례로 확인해 보세요.</p>
</section>

<section id="areas">
  <h2>하남 대표 지역별 방문 가능 지역 안내</h2>
  <p>하남 대표 생활권별 방문 가능 지역입니다. 각 카드를 눌러 인접 생활권과 예약 전 확인사항을 확인하세요.</p>
  <div class="card-grid">
    <a href="/misa-area/" class="card"><h3>미사 생활권</h3><p>미사역, 미사강변도시, 망월동, 선동 인접 생활권</p><span class="card-arrow">→</span></a>
    <a href="/mangwol-dong/" class="card"><h3>망월동</h3><p>미사역, 미사강변도시, 한강변 주거지 생활권</p></a>
    <a href="/seon-dong/" class="card"><h3>선동</h3><p>미사강변도시, 망월동, 미사역 인접 생활권</p></a>
    <a href="/pungsan-dong/" class="card"><h3>풍산동</h3><p>하남풍산역, 미사, 덕풍동 인접 생활권</p></a>
    <a href="/deokpung-dong/" class="card"><h3>덕풍동</h3><p>하남풍산역, 덕풍시장, 신장동 인접 생활권</p></a>
    <a href="/sinjang-dong/" class="card"><h3>신장동</h3><p>하남시청역, 스타필드 하남, 창우동 인접 생활권</p></a>
    <a href="/changu-dong/" class="card"><h3>창우동</h3><p>하남검단산역, 검단산, 신장동 인접 생활권</p></a>
    <a href="/cheonhyeon-dong/" class="card"><h3>천현동</h3><p>검단산, 창우동, 배알미동 인접 차량 이동 생활권</p></a>
    <a href="/gamil-dong/" class="card"><h3>감일동</h3><p>감일지구, 감이동, 위례·송파 인접 생활권</p></a>
    <a href="/gambuk-dong/" class="card"><h3>감북동</h3><p>감북동, 초이동, 강동 상일동 인접 생활권</p></a>
    <a href="/wirye-dong/" class="card"><h3>위례동</h3><p>하남 위례, 학암동, 감일동 인접 생활권</p></a>
    <a href="/chungung-dong/" class="card"><h3>춘궁동</h3><p>교산동, 춘궁동, 상사창동, 하사창동 인접 생활권</p></a>
    <a href="/choi-dong/" class="card"><h3>초이동</h3><p>초이동, 초일동, 감북동, 강동 인접 생활권</p></a>
    <a href="/misa-dong/" class="card"><h3>미사동</h3><p>미사강변도시 생활권 행정 중심 안내</p></a>
  </div>
</section>

<section id="stations">
  <h2>하남 주요 지하철역별 홈타이 안내</h2>
  <p>하남 핵심 역세권은 미사역, 하남풍산역, 하남시청역, 하남검단산역입니다. 각 역 인접 생활권과 예약 전 확인사항을 안내합니다.</p>
  <div class="card-grid">
    <a href="/station/misa-station/" class="card"><h3>미사역</h3><p>망월동, 미사강변도시, 선동 인접 생활권입니다. 방문 주소와 건물 출입 가능 여부를 먼저 확인하세요.</p><span class="card-arrow">상세보기 →</span></a>
    <a href="/station/hanam-pungsan-station/" class="card"><h3>하남풍산역</h3><p>풍산동, 덕풍동 인접 생활권입니다. 예약 가능 시간과 방문 주소를 먼저 확인하세요.</p><span class="card-arrow">상세보기 →</span></a>
    <a href="/station/hanam-cityhall-station/" class="card"><h3>하남시청역</h3><p>신장동, 덕풍동, 창우동 인접 생활권입니다. 자택·숙소·오피스텔 이용 가능 여부를 먼저 확인하세요.</p><span class="card-arrow">상세보기 →</span></a>
    <a href="/station/hanam-geomdansan-station/" class="card"><h3>하남검단산역</h3><p>창우동, 천현동, 검단산 인접 생활권입니다. 차량 이동 기준과 추가 이동비 여부를 확인하세요.</p><span class="card-arrow">상세보기 →</span></a>
    <a href="/station/gangil-nearby-area/" class="card"><h3>강일역 인접</h3><p>미사·감북 인접 이동 기준 안내</p></a>
    <a href="/station/sangil-dong-nearby-area/" class="card"><h3>상일동역 인접</h3><p>초이·감북 인접 이동 기준 안내</p></a>
    <a href="/station/macheon-nearby-area/" class="card"><h3>마천역 인접</h3><p>감일·하남 위례 인접 이동 기준 안내</p></a>
    <a href="/station/dunchon-oryun-nearby-area/" class="card"><h3>둔촌오륜역 인접</h3><p>감일 인접 이동 기준 안내</p></a>
  </div>
</section>

<section id="lifestyle">
  <h2>하남 생활권별 예약 기준</h2>
  <p>생활권 페이지는 지역 페이지와 역세권 페이지 사이를 연결하는 중간 허브 역할을 합니다. 지역과 역을 함께 묶어 더 정확한 방문 주소와 이동 시간을 확인할 수 있습니다.</p>
  <div class="card-grid">
    <a href="/area/misa-riverside-city/" class="card">미사강변도시</a>
    <a href="/area/misa-station-mangwol/" class="card">미사역·망월동</a>
    <a href="/area/hanam-pungsan-deokpung/" class="card">하남풍산·덕풍</a>
    <a href="/area/hanam-cityhall-sinjang/" class="card">하남시청·신장</a>
    <a href="/area/geomdansan-changu/" class="card">하남검단산·창우</a>
    <a href="/area/starfield-sinjang/" class="card">스타필드·신장</a>
    <a href="/area/gamil-district/" class="card">감일지구</a>
    <a href="/area/hanam-wirye/" class="card">하남 위례</a>
    <a href="/area/gambuk-choi/" class="card">감북·초이</a>
    <a href="/area/chungung-gyosan/" class="card">춘궁·교산</a>
    <a href="/area/cheonhyeon-geomdansan/" class="card">천현·검단산</a>
    <a href="/area/paldang-baealmi-nearby/" class="card">팔당·배알미 인접</a>
    <a href="/area/gangdong-gamil-nearby/" class="card">강동·감일 인접</a>
  </div>
</section>

<section id="check">
  <h2>하남 홈타이 예약 전 확인사항</h2>
  <p>예약을 진행하기 전에 다음 항목을 먼저 확인하면 방문 일정이 정확해집니다. 자세한 내용은 <a href="/check/">이용 전 확인사항</a>에서 확인하세요.</p>
  <ul>
    <li><strong>방문 가능 주소 확인</strong> — 자택, 숙소, 오피스텔 등 정확한 방문 주소와 건물 유형 확인</li>
    <li><strong>예약 가능 시간 확인</strong> — 희망 예약 시간이 가능한지 미리 확인</li>
    <li><strong>추가 이동비 여부 확인</strong> — 기본 이동권 외 추가 이동비 발생 여부</li>
    <li><strong>건물 출입 방식 확인</strong> — 공동현관, 자동문, 경비 출입 방식</li>
    <li><strong>자택·숙소·오피스텔 이용 기준 확인</strong> — 서비스 제공 장소 기준</li>
    <li><strong>결제 방식 확인</strong> — 가능한 결제 수단</li>
    <li><strong>예약 변경·취소 기준 확인</strong> — 변경·취소 절차</li>
    <li><strong>개인정보 처리 기준 확인</strong> — <a href="/support/privacy/">개인정보처리방침</a> 참조</li>
    <li><strong>불법·선정적 서비스 불가 안내</strong> — 건전한 방문 관리 서비스만 제공</li>
  </ul>
</section>

<section id="faq">
  <h2>하남 출장마사지 자주 묻는 질문</h2>
  <dl class="faq-list">
    <dt id="faq-1">하남은 구별 페이지를 만들어야 하나요?</dt>
    <dd>하남은 행정구가 없으므로 구별 페이지를 만들지 않습니다. 하남 메인, 대표 지역, 역세권, 생활권 구조로 안내하며, 미사·감일·위례·덕풍·신장·하남검단산 생활권을 먼저 확인하면 됩니다.</dd>

    <dt id="faq-2">미사1동, 미사2동, 미사3동을 각각 확인해야 하나요?</dt>
    <dd>1차 안내에서는 <a href="/misa-area/">미사 생활권</a>으로 묶어 안내합니다. 미사강변도시, 망월동, 선동, 풍산동 인접권을 함께 설명하므로 미사 생활권 페이지에서 방문 가능 지역을 확인하는 방식이 좋습니다.</dd>

    <dt id="faq-3">위례동은 송파 위례와 같은 지역인가요?</dt>
    <dd>위례는 하남·송파·성남으로 행정구역이 나뉩니다. 본 안내는 <a href="/wirye-dong/">하남 위례</a> 기준이며, 송파 위례·성남 위례는 별도 행정구역이므로 인접 생활권으로만 설명합니다.</dd>

    <dt id="faq-4">예약 전 꼭 확인해야 할 사항은 무엇인가요?</dt>
    <dd>방문 가능 주소, 예약 가능 시간, 추가 이동비 여부, 건물 출입 방식, 자택·숙소·오피스텔 이용 기준, 결제 방식, 예약 변경 기준, 개인정보 처리 기준을 먼저 확인하고 예약하는 방식이 좋습니다.</dd>

    <dt id="faq-5">강일역이나 상일동역도 하남 역세권인가요?</dt>
    <dd>강일역과 상일동역은 서울 강동구 성격이 강해 하남에서는 감북·초이·미사 인접 생활권으로만 안내합니다. 마천역은 송파 성격이 강해 감일·하남 위례 인접권으로만 설명합니다.</dd>
  </dl>
</section>
"""
}
