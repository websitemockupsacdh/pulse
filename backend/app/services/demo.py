"""DEV ONLY. Inserts clearly labeled sample items through the real pipeline so the UI has data offline.
Never run in production. Everything it creates is attributed to the 'Demo data' source."""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..connectors.base import RawItem
from ..models import Source
from . import pipeline
from .trends import refresh_topics

H = lambda h: datetime.now(timezone.utc) - timedelta(hours=h, minutes=7)

SAMPLES = [
    ("news", "national", "Signal No. 2 raised over Bicol as tropical storm nears landfall", 0.5, None),
    ("news", "national", "Tropical storm nears Bicol, Signal No. 2 raised in Camarines Sur", 1.0, None),
    ("news", "national", "Bicol classes suspended as tropical storm nears landfall", 1.6, None),
    ("news", "business", "BSP holds policy rate as inflation eases to 2.1 percent", 2, None),
    ("news", "business", "Inflation eases to 2.1 percent, BSP keeps policy rate steady", 3, None),
    ("news", "technology", "DICT drafts national guidelines for artificial intelligence in government", 4, None),
    ("news", "technology", "Artificial intelligence guidelines for Philippine agencies open for comment", 5, None),
    ("news", "sports", "Gilas Pilipinas names 14 for Asian Cup qualifier in Manila", 7, None),
    ("news", "sports", "Gilas names final 14 for Manila qualifier against Chinese Taipei", 8, None),
    ("news", "international", "Global leaders agree on shipping emissions timetable", 6, None),
    ("social", "national", "Commuters share MRT-3 delays on the northbound line this morning", 1.2, None),
    ("video", "entertainment", "Manila street food crawl, Quiapo to Binondo", 9, "completed"),
    ("video", "sports", "LIVE: PBA game day pre-show from Araneta Coliseum", 0.2, "live"),
    ("video", "national", "Upcoming: Senate briefing on flood control projects", 0.1, "upcoming"),
]


class _Demo:
    def __init__(self, items): self.items = items
    def fetch(self): return self.items


def seed_demo(db: Session) -> None:
    src = db.query(Source).filter_by(slug="demo").one_or_none()
    if not src:
        src = Source(slug="demo", name="Demo data", connector="rss", kind="news", url="https://example.invalid", region="PH")
        db.add(src); db.commit()
    raws = []
    for i, (kind, cat, title, h, live) in enumerate(SAMPLES):
        raws.append(RawItem(title=title, url=f"https://example.invalid/demo/{i}", published_at=H(h), kind=kind, category=cat,
                            snippet="Demo item. Not real reporting.", live_status=live,
                            platform={"news": "web", "social": "reddit", "video": "youtube"}[kind],
                            region="INTL" if cat == "international" else "PH",
                            engagement={"viewCount": 1200 + i * 310} if kind == "video" and live != "upcoming" else None))
    orig = pipeline.build
    pipeline.build = lambda *a: _Demo(raws)
    try:
        pipeline.ingest_source(db, src)
    finally:
        pipeline.build = orig
    refresh_topics(db)
