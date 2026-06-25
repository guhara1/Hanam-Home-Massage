# 하남시 출장마사지 사이트 공통 설정

BASE_URL = "https://hanam-home-massage.pages.dev"

BRAND = "바로 GO"
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

# 사이트 메타 (RSS·스키마용)
SITE_DESC = "경기도 하남시 전지역 방문 출장마사지·홈타이 안내. 미사·감일·위례·덕풍·신장·하남검단산 생활권별 예약 안내."

# IndexNow 키 — 빙·네이버 즉시 색인 통보용.
# 빌드 시 루트에 "<INDEXNOW_KEY>.txt" 파일이 생성되며 내용은 키와 동일해야 한다.
INDEXNOW_KEY = "379f163d97078fcf3e7d717edbcce2d7"

# 상단 메뉴 — 키워드 반복 없음, 지역명·역명만 표시
NAV = [
    ("하남 홈", "/", []),
    ("지역별 안내", "/", [
        ("미사 생활권", "/misa-area/"),
        ("미사동", "/misa-dong/"),
        ("망월동", "/mangwol-dong/"),
        ("선동", "/seon-dong/"),
        ("풍산동", "/pungsan-dong/"),
        ("덕풍동", "/deokpung-dong/"),
        ("신장동", "/sinjang-dong/"),
        ("창우동", "/changu-dong/"),
        ("천현동", "/cheonhyeon-dong/"),
        ("감일동", "/gamil-dong/"),
        ("감북동", "/gambuk-dong/"),
        ("위례동", "/wirye-dong/"),
        ("춘궁동", "/chungung-dong/"),
        ("초이동", "/choi-dong/"),
        ("교산 생활권", "/gyosan-area/"),
        ("검단산 생활권", "/geomdansan-area/"),
    ]),
    ("역세권 안내", "/", [
        ("미사역", "/station/misa-station/"),
        ("하남풍산역", "/station/hanam-pungsan-station/"),
        ("하남시청역", "/station/hanam-cityhall-station/"),
        ("하남검단산역", "/station/hanam-geomdansan-station/"),
        ("강일역 인접", "/station/gangil-nearby-area/"),
        ("상일동역 인접", "/station/sangil-dong-nearby-area/"),
        ("둔촌오륜역 인접", "/station/dunchon-oryun-nearby-area/"),
        ("마천역 인접", "/station/macheon-nearby-area/"),
    ]),
    ("생활권 안내", "/", [
        ("미사강변도시", "/area/misa-riverside-city/"),
        ("미사역·망월동", "/area/misa-station-mangwol/"),
        ("하남풍산·덕풍", "/area/hanam-pungsan-deokpung/"),
        ("하남시청·신장", "/area/hanam-cityhall-sinjang/"),
        ("하남검단산·창우", "/area/geomdansan-changu/"),
        ("스타필드·신장", "/area/starfield-sinjang/"),
        ("감일지구", "/area/gamil-district/"),
        ("하남 위례", "/area/hanam-wirye/"),
        ("감북·초이", "/area/gambuk-choi/"),
        ("춘궁·교산", "/area/chungung-gyosan/"),
        ("천현·검단산", "/area/cheonhyeon-geomdansan/"),
        ("팔당·배알미 인접", "/area/paldang-baealmi-nearby/"),
        ("강동·감일 인접", "/area/gangdong-gamil-nearby/"),
    ]),
    ("예약 안내", "/reservation/", []),
    ("이용 전 확인사항", "/check/", []),
    ("홈타이 이용 가이드", "/guide/", []),
    ("고객센터", "/support/", [
        ("개인정보처리방침", "/support/privacy/"),
    ]),
]
