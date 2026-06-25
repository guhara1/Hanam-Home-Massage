# 하남시 출장마사지 사이트 공통 설정

BASE_URL = "https://hanam-home-massage.pages.dev"

BRAND = "바로 GO"
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

# 상단 메뉴 — 키워드 반복 없음, 지역명·역명만 표시
NAV = [
    ("하남 홈", "/gyeonggi/hanam/", []),
    ("지역별 안내", "/gyeonggi/hanam/", [
        ("미사 생활권", "/gyeonggi/hanam/misa-area/"),
        ("미사동", "/gyeonggi/hanam/misa-dong/"),
        ("망월동", "/gyeonggi/hanam/mangwol-dong/"),
        ("선동", "/gyeonggi/hanam/seon-dong/"),
        ("풍산동", "/gyeonggi/hanam/pungsan-dong/"),
        ("덕풍동", "/gyeonggi/hanam/deokpung-dong/"),
        ("신장동", "/gyeonggi/hanam/sinjang-dong/"),
        ("창우동", "/gyeonggi/hanam/changu-dong/"),
        ("천현동", "/gyeonggi/hanam/cheonhyeon-dong/"),
        ("감일동", "/gyeonggi/hanam/gamil-dong/"),
        ("감북동", "/gyeonggi/hanam/gambuk-dong/"),
        ("위례동", "/gyeonggi/hanam/wirye-dong/"),
        ("춘궁동", "/gyeonggi/hanam/chungung-dong/"),
        ("초이동", "/gyeonggi/hanam/choi-dong/"),
        ("교산 생활권", "/gyeonggi/hanam/gyosan-area/"),
        ("검단산 생활권", "/gyeonggi/hanam/geomdansan-area/"),
    ]),
    ("역세권 안내", "/gyeonggi/hanam/", [
        ("미사역", "/gyeonggi/hanam/station/misa-station/"),
        ("하남풍산역", "/gyeonggi/hanam/station/hanam-pungsan-station/"),
        ("하남시청역", "/gyeonggi/hanam/station/hanam-cityhall-station/"),
        ("하남검단산역", "/gyeonggi/hanam/station/hanam-geomdansan-station/"),
        ("강일역 인접", "/gyeonggi/hanam/station/gangil-nearby-area/"),
        ("상일동역 인접", "/gyeonggi/hanam/station/sangil-dong-nearby-area/"),
        ("둔촌오륜역 인접", "/gyeonggi/hanam/station/dunchon-oryun-nearby-area/"),
        ("마천역 인접", "/gyeonggi/hanam/station/macheon-nearby-area/"),
    ]),
    ("생활권 안내", "/gyeonggi/hanam/", [
        ("미사강변도시", "/gyeonggi/hanam/area/misa-riverside-city/"),
        ("미사역·망월동", "/gyeonggi/hanam/area/misa-station-mangwol/"),
        ("하남풍산·덕풍", "/gyeonggi/hanam/area/hanam-pungsan-deokpung/"),
        ("하남시청·신장", "/gyeonggi/hanam/area/hanam-cityhall-sinjang/"),
        ("하남검단산·창우", "/gyeonggi/hanam/area/geomdansan-changu/"),
        ("스타필드·신장", "/gyeonggi/hanam/area/starfield-sinjang/"),
        ("감일지구", "/gyeonggi/hanam/area/gamil-district/"),
        ("하남 위례", "/gyeonggi/hanam/area/hanam-wirye/"),
        ("감북·초이", "/gyeonggi/hanam/area/gambuk-choi/"),
        ("춘궁·교산", "/gyeonggi/hanam/area/chungung-gyosan/"),
        ("천현·검단산", "/gyeonggi/hanam/area/cheonhyeon-geomdansan/"),
        ("팔당·배알미 인접", "/gyeonggi/hanam/area/paldang-baealmi-nearby/"),
        ("강동·감일 인접", "/gyeonggi/hanam/area/gangdong-gamil-nearby/"),
    ]),
    ("예약 안내", "/gyeonggi/hanam/reservation/", []),
    ("이용 전 확인사항", "/gyeonggi/hanam/check/", []),
    ("홈타이 이용 가이드", "/gyeonggi/hanam/guide/", []),
    ("고객센터", "/gyeonggi/hanam/support/", [
        ("개인정보처리방침", "/gyeonggi/hanam/support/privacy/"),
    ]),
]
