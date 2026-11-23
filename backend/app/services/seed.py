"""Initial source registry and home layout. Feed URLs are config: verify them with `python -m app.cli check-sources`."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import PageSection, Source

SOURCES = [
    # slug, name, connector, kind, url, config
    ("abs-cbn", "ABS-CBN News", "rss", "news", "https://news.abs-cbn.com/rss", {"category": "national"}),
    ("gma", "GMA Integrated News", "rss", "news", "https://data.gmanetwork.com/gno/rss/news/feed.xml", {"category": "national"}),
    ("rappler", "Rappler", "rss", "news", "https://www.rappler.com/feed/", {"category": "national"}),
    ("philstar", "Philstar.com", "rss", "news", "https://www.philstar.com/rss/headlines", {"category": "national"}),
    ("inquirer", "Inquirer.net", "rss", "news", "https://newsinfo.inquirer.net/feed", {"category": "national"}),
    ("mb", "Manila Bulletin", "rss", "news", "https://mb.com.ph/rss/articles", {"category": "national"}),
    ("pna", "Philippine News Agency", "rss", "news", "https://www.pna.gov.ph/latest.rss", {"category": "national"}),
    ("bbc-world", "BBC News World", "rss", "news", "https://feeds.bbci.co.uk/news/world/rss.xml", {"category": "international"}),
    ("youtube-ph", "YouTube Trending PH", "youtube", "video", "https://www.googleapis.com/youtube/v3", {"region_code": "PH"}),
    ("reddit-ph", "r/Philippines", "reddit", "social", "https://www.reddit.com/r/Philippines/hot.json?limit=25", {}),
    # Official agencies. Disabled until a feed URL is verified against the agency's own site.
    ("pagasa", "PAGASA", "rss", "official", "", {"category": "weather", "kind": "official"}),
    ("phivolcs", "PHIVOLCS", "rss", "official", "", {"category": "weather", "kind": "official"}),
    ("ndrrmc", "NDRRMC", "rss", "official", "", {"category": "weather", "kind": "official"}),
    ("x", "X", "social_unavailable", "social", "https://x.com", {"platform": "X"}),
    ("threads", "Threads", "social_unavailable", "social", "https://threads.net", {"platform": "Threads"}),
    ("facebook", "Facebook", "social_unavailable", "social", "https://facebook.com", {"platform": "Facebook"}),
    ("instagram", "Instagram", "social_unavailable", "social", "https://instagram.com", {"platform": "Instagram"}),
    ("tiktok", "TikTok", "social_unavailable", "social", "https://tiktok.com", {"platform": "TikTok"}),
]

HOME = [
    ("breaking", "Breaking", {"kind": "news", "hours": 3, "limit": 5}),
    ("trending", "Top trending topics", {"topics": True, "sort": "velocity", "limit": 8}),
    ("rising", "Fastest rising", {"topics": True, "status": "rising", "limit": 6}),
    ("briefing", "Daily briefing", {}),
    ("latest_news", "Latest Philippine news", {"kind": "news", "region": "PH", "limit": 10}),
    ("social", "Public discussions", {"kind": "social", "limit": 6}),
    ("video", "Videos and live", {"kind": "video", "limit": 6}),
    ("weather", "Weather and disasters", {"category": "weather", "limit": 5}),
    ("sports_ent", "Sports and entertainment", {"categories": ["sports", "entertainment"], "limit": 6}),
    ("international", "International", {"region": "INTL", "limit": 6}),
]


def seed(db: Session) -> None:
    have = set(db.scalars(select(Source.slug)))
    for slug, name, conn, kind, url, cfg in SOURCES:
        if slug not in have:
            db.add(Source(slug=slug, name=name, connector=conn, kind=kind, url=url, config=cfg,
                          region="INTL" if "bbc" in slug else "PH", enabled=bool(url)))
    if not db.scalar(select(PageSection.id)):
        for i, (key, title, q) in enumerate(HOME):
            db.add(PageSection(page="home", position=i, key=key, title=title, query=q))
    db.commit()
