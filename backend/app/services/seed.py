"""Publisher registry and home layout. RSS URLs are discovered from each publisher page."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import PageSection, Source


def _sources():
    rows = []

    def add(slug, name, url, category, *, region="PH", kind="news"):
        rows.append((slug, name, "rss", kind, url, {"category": category, "kind": kind}, region))

    # Sports
    add("onesports", "One Sports", "https://www.onesports.ph", "sports")
    add("inquirer-sports", "Inquirer Sports", "https://sports.inquirer.net", "sports")
    add("tribune-sport", "Daily Tribune Sport", "https://tribune.net.ph/sport", "sports")
    add("abscbn-sports", "ABS-CBN Sports", "https://www.abs-cbn.com/sports", "sports")
    add("philstar-sports", "Philstar.com", "http://philstar.com", "sports")
    add("gma-sports", "GMA Sports", "https://www.gmanetwork.com/news/sports", "sports")
    add("espn-ph", "ESPN Philippines", "https://www.espn.ph", "sports", region="INTL")

    # Weather, earthquakes, and disaster response
    add("pagasa", "PAGASA", "https://www.pagasa.dost.gov.ph", "weather", kind="official")
    add("phivolcs", "PHIVOLCS", "https://www.phivolcs.dost.gov.ph", "weather", kind="official")
    add("ndrrmc", "NDRRMC", "https://www.facebook.com/NDRRMC", "weather", kind="official")
    add("gma-weather", "GMA Weather", "https://www.gmanetwork.com/news/weather", "weather")
    add("inquirer-weather", "Inquirer.net", "http://inquirer.net", "weather")
    add("reliefweb", "ReliefWeb", "https://reliefweb.int", "weather", kind="official", region="INTL")
    add("wmo", "World Meteorological Organization", "https://wmo.int", "weather", kind="official", region="INTL")
    add("usgs-earthquakes", "USGS Earthquake Hazards", "https://www.usgs.gov/programs/earthquake-hazards",
        "weather", kind="official", region="INTL")

    # Science and technology
    add("science-ph", "Science.ph", "https://www.science.ph", "science")
    add("pcieerd", "DOST-PCIEERD", "https://pcieerd.dost.gov.ph/news", "science")
    add("asti", "DOST-ASTI", "https://asti.dost.gov.ph/innovation/news-articles", "science")
    add("gma-scitech", "GMA SciTech", "https://www.gmanetwork.com/news/scitech", "science")
    add("rappler-science", "Rappler Science", "https://www.rappler.com/science", "science")
    add("manilatimes-scitech", "The Manila Times", "https://www.manilatimes.net/business/science-technolog", "science")
    add("phys-org", "Phys.org", "https://phys.org", "science", region="INTL")
    add("science-daily", "ScienceDaily", "https://www.sciencedaily.com", "science", region="INTL")
    add("scitech-daily", "SciTechDaily", "https://scitechdaily.com", "science", region="INTL")
    add("science-news", "Science News", "https://www.sciencenews.org", "science", region="INTL")
    add("bbc-technology", "BBC Technology", "https://www.bbc.com/technology", "science", region="INTL")

    # Entertainment
    add("pep", "PEP.ph", "https://www.pep.ph", "entertainment")
    add("abscbn-entertainment", "ABS-CBN Entertainment", "https://www.abs-cbn.com/entertainment/showbiz", "entertainment")
    add("gma-entertainment", "GMA Entertainment", "https://www.gmanetwork.com/entertainment", "entertainment")
    add("inquirer-entertainment", "Inquirer Entertainment", "https://entertainment.inquirer.net", "entertainment")
    add("rappler-entertainment", "Rappler Entertainment", "https://www.rappler.com/entertainment", "entertainment")
    add("philstar-entertainment", "Philstar Entertainment", "https://www.philstar.com/entertainment", "entertainment")
    add("mb-entertainment", "Manila Bulletin Entertainment", "https://mb.com.ph/category/entertainment", "entertainment")

    # International K-pop news, plus Philippine coverage and event listings
    add("soompi", "Soompi", "https://www.soompi.com", "kpop", region="INTL")
    add("korea-joongang-kpop", "Korea JoongAng Daily", "https://www.koreajoongangdaily.com/entertainment/k-pop", "kpop", region="INTL")
    add("koreaboo", "Koreaboo", "https://www.koreaboo.com", "kpop", region="INTL")
    add("allkpop", "allkpop", "https://www.allkpop.com", "kpop", region="INTL")
    add("rappler-kpop", "Rappler K-pop", "https://www.rappler.com/entertainment/korean-popular-music", "kpop")
    add("philippineconcerts-kpop", "Philippine Concerts", "https://www.philippineconcerts.com/category/k-pop", "kpop")
    add("kpopofficial", "Kpop Official", "https://kpopofficial.com/schedule/philippines", "kpop")

    # Japanese music
    add("arama-japan", "Arama! Japan", "https://aramajapan.com", "jpop", region="INTL")
    add("j-generation", "J Generation", "https://j-generation.com", "jpop", region="INTL")
    add("neotokyo2099", "Neo Tokyo 2099", "https://neotokyo2099.com", "jpop", region="INTL")
    add("jrocknews", "JROCK NEWS", "https://jrocknews.com", "jpop", region="INTL")
    add("natalie-music", "Natalie Music", "https://natalie.mu/music", "jpop", region="INTL")
    add("jpopmanila", "J-Pop Manila", "https://jpopmanila.com", "jpop")
    add("philippineconcerts-jpop", "Philippine Concerts", "https://www.philippineconcerts.com", "jpop")

    # P-pop
    add("poppinph", "Poppin' PH", "https://poppinph.com", "ppop")
    add("ppopbeats", "P-POP Beats", "https://ppopbeats.com", "ppop")
    add("myx-ppop", "MYX P-pop", "https://myx.global/p-pop-news", "ppop")
    add("rappler-ppop", "Rappler P-pop", "https://www.rappler.com/topic/pinoy-pop", "ppop")
    add("pep-ppop", "PEP.ph P-pop", "https://www.pep.ph/tag/p-pop-news", "ppop")
    add("philstar-ppop", "Philstar P-pop", "https://www.philstar.com/tags/p-pop", "ppop")
    add("gma-ppop", "GMA P-pop", "https://www.gmanetwork.com/news/tracking/ppop", "ppop")
    add("philippineconcerts-ppop", "Philippine Concerts", "https://www.philippineconcerts.com", "ppop")

    # Professional Regulation Commission
    add("prc", "Professional Regulation Commission", "https://www.prc.gov.ph/", "prc", kind="official")

    # Keep older general news and international sources.
    add("abs-cbn", "ABS-CBN News", "https://news.abs-cbn.com/rss", "national")
    add("gma", "GMA Integrated News", "https://data.gmanetwork.com/gno/rss/news/feed.xml", "national")
    add("rappler", "Rappler", "https://www.rappler.com/feed/", "national")
    add("philstar", "Philstar.com", "https://www.philstar.com/rss/headlines", "national")
    add("inquirer", "Inquirer.net", "https://newsinfo.inquirer.net/feed", "national")
    add("mb", "Manila Bulletin", "https://mb.com.ph/rss/articles", "national")
    add("pna", "Philippine News Agency", "https://www.pna.gov.ph/latest.rss", "national")
    add("bbc-world", "BBC News World", "https://feeds.bbci.co.uk/news/world/rss.xml", "international", region="INTL")
    return rows


SOURCES = _sources()

HOME = [
    ("breaking", "Breaking", {"kind": "news", "hours": 3, "limit": 5}),
    ("trending", "Top trending topics", {"topics": True, "sort": "velocity", "limit": 8}),
    ("rising", "Fastest rising", {"topics": True, "status": "rising", "limit": 6}),
    ("briefing", "Daily briefing", {}),
    ("latest_news", "Latest Philippine news", {"kind": "news", "region": "PH", "limit": 8}),
    ("weather", "Weather and disasters", {"category": "weather", "limit": 5}),
    ("sports", "Sports", {"category": "sports", "limit": 5}),
    ("science", "Science and technology", {"category": "science", "limit": 5}),
    ("entertainment", "Entertainment and showbiz", {"category": "entertainment", "limit": 5}),
    ("kpop", "K-pop", {"category": "kpop", "limit": 5}),
    ("jpop", "J-pop", {"category": "jpop", "limit": 5}),
    ("ppop", "P-pop", {"category": "ppop", "limit": 5}),
    ("prc", "PRC exam updates", {"category": "prc", "limit": 5}),
    ("international", "International news", {"region": "INTL", "limit": 6}),
]


def seed(db: Session) -> None:
    sources = {s.slug: s for s in db.scalars(select(Source))}
    for slug, name, conn, kind, url, cfg, region in SOURCES:
        source = sources.get(slug)
        enable_source = source is None or (slug in {"pagasa", "phivolcs", "ndrrmc"} and not source.url)
        if source is None:
            source = Source(slug=slug)
            db.add(source)
        source.name = name
        source.connector = conn
        source.kind = kind
        source.url = url
        source.config = cfg
        source.region = region
        if enable_source:
            source.enabled = True

    # Retire the old social/video collection rather than continuing to poll it.
    for slug in ("youtube-ph", "reddit-ph", "x", "threads", "facebook", "instagram", "tiktok"):
        if slug in sources:
            sources[slug].enabled = False

    sections = {s.key: s for s in db.scalars(select(PageSection).where(PageSection.page == "home"))}
    for i, (key, title, query) in enumerate(HOME):
        section = sections.get(key)
        if section is None:
            section = PageSection(page="home", key=key)
            db.add(section)
        section.position = i
        section.title = title
        section.query = query
    for key in ("social", "video", "sports_ent"):
        if key in sections:
            sections[key].enabled = False
    db.commit()
