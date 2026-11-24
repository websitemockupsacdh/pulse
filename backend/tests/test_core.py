from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.connectors.base import RawItem
from app.db import Base
from app.models import Item, PageSection, Source
from app.services import pipeline, trends
from app.services.seed import seed
from app.services.text import canonical_url, jaccard, tokens


@pytest.fixture()
def db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(eng)
    s = sessionmaker(bind=eng, expire_on_commit=False)()
    seed(s)
    yield s
    s.close()


def fake_connector(items):
    class C:
        def __init__(self, *a): pass
        def fetch(self): return items
    return C


def run(db, items, slug="inquirer", monkeypatch=None):
    src = db.query(Source).filter_by(slug=slug).one()
    pipeline.build = lambda *a: fake_connector(items)()
    return pipeline.ingest_source(db, src)


def raw(title, url, hours_ago=1, **kw):
    return RawItem(title=title, url=url, published_at=datetime.now(timezone.utc) - timedelta(hours=hours_ago), **kw)


def test_canonical_url_strips_tracking_and_www():
    assert canonical_url("https://www.Example.com/a/?utm=1#x") == "https://example.com/a"


def test_dedup_by_url(db):
    a = raw("Typhoon signal raised over Bicol", "https://x.ph/a?utm=1")
    assert run(db, [a]) == 1
    assert run(db, [raw("Typhoon signal raised over Bicol", "https://www.x.ph/a")]) == 0


def test_rejects_future_and_bad_items(db):
    assert run(db, [raw("Bad", "ftp://x"), raw("Future thing happens now", "https://x.ph/f", hours_ago=-48)]) == 0


def test_cross_source_clustering_and_status(db):
    run(db, [raw("Typhoon signal raised over Bicol region", "https://a.ph/1", 2)], "inquirer")
    run(db, [raw("Signal raised as typhoon nears Bicol region", "https://b.ph/1", 1)], "rappler")
    trends.refresh_topics(db)
    topics = db.query(trends.Topic).all()
    assert len(topics) == 1 and topics[0].source_count == 2 and topics[0].status == "emerging"


def test_status_thresholds():
    assert trends.status_for(100, 0.1, 10, 5) == "declining"
    assert trends.status_for(10, 3.0, 1, 9) == "rising"
    assert trends.status_for(10, 1.0, 1, 9) == "active"
    assert trends.status_for(200, 0, 100, 5) == "archived"


def test_missing_engagement_is_null_not_zero(db):
    run(db, [raw("Some national news headline", "https://news.ph/1")])
    assert db.query(Item).one().engagement is None


def test_seed_preserves_source_state_and_retires_old_sections(db):
    youtube = db.query(Source).filter_by(slug="youtube-ph").one()
    youtube.enabled = False
    db.add(PageSection(page="home", position=9, key="video", title="Videos", query={}))
    db.commit()
    seed(db)
    assert db.query(Source).filter_by(slug="youtube-ph").one().enabled is False
    assert db.query(PageSection).filter_by(key="video").one().enabled is False
    assert db.query(Source).filter_by(slug="prc").one().config["category"] == "prc"
    assert db.query(Source).filter_by(slug="soompi").one().region == "INTL"
    assert db.query(PageSection).filter_by(key="ppop").one().enabled is True


def test_source_enablement_is_persisted_and_sources_can_be_reenabled(db):
    disabled = {"abs-cbn", "mb", "mb-entertainment", "pna", "reddit-ph", "facebook", "instagram",
                "threads", "tiktok", "x", "ndrrmc", "pagasa", "phivolcs"}
    enabled = {"bbc-world", "gma", "inquirer", "philstar", "rappler", "gdacs", "youtube-ph"}
    rows = {source.slug: source for source in db.query(Source).all()}
    assert disabled.issubset(rows)
    assert all(not rows[slug].enabled for slug in disabled)
    assert all(rows[slug].enabled for slug in enabled)

    source = rows["reddit-ph"]
    source.enabled = True
    source.url = "https://reddit.example/custom"
    source.config = {"custom": True}
    seed(db)
    assert source.enabled is True
    assert source.url == "https://reddit.example/custom"
    assert source.config == {"custom": True}


def test_ingestion_attempts_only_enabled_sources_and_keeps_gma_ingestible(db, monkeypatch):
    from sqlalchemy import select

    from app.services.seed import DISABLED_SOURCE_SLUGS

    sources = list(db.scalars(select(Source)))
    enabled = {source.slug for source in sources if source.enabled}
    from collections import Counter

    expected = Counter((source.connector, source.url) for source in sources if source.enabled)
    calls = []

    def build(connector, config, url):
        calls.append((connector, url))

        class FakeConnector:
            def fetch(self):
                if url == "https://data.gmanetwork.com/gno/rss/news/feed.xml":
                    return [raw("GMA ingests new public headlines", "https://gma.example/story")]
                return []

        return FakeConnector()

    monkeypatch.setattr(pipeline, "build", build)
    pipeline.ingest_all(db)
    assert Counter(calls) == Counter(expected)
    assert not (enabled & DISABLED_SOURCE_SLUGS)
    assert db.query(Item).filter_by(title="GMA ingests new public headlines").count() == 1


def test_disabled_source_is_skipped_when_ingested_directly(db, monkeypatch):
    source = db.query(Source).filter_by(slug="reddit-ph").one()
    called = False

    def build(*args):
        nonlocal called
        called = True
        raise AssertionError("disabled sources must not be fetched")

    monkeypatch.setattr(pipeline, "build", build)
    assert pipeline.ingest_source(db, source) == 0
    assert not called


def test_image_url_is_saved_with_item(db):
    image = "https://news.ph/image.jpg"
    run(db, [raw("News with a preview image", "https://news.ph/story", image_url=image)])
    assert db.query(Item).one().image_url == image


def test_api(db, monkeypatch):
    from app import main as m
    from app.api import routes
    from app.db import get_db
    run(db, [raw("Philippine AI policy drafted by DICT", "https://a.ph/ai", 1)])
    m.app.dependency_overrides[get_db] = lambda: db
    c = TestClient(m.app)
    assert c.get("/api/health").json() == {"ok": True}
    r = c.get('/api/search', params={"q": '"AI policy"'}).json()
    assert r["total"] == 1 and r["items"][0]["engagement"] is None
    assert r["items"][0]["image_url"] is None
    assert c.get("/api/home").json()["sections"][0]["key"] == "breaking"
    slug = db.query(trends.Topic).one().slug
    assert c.get(f"/api/topics/{slug}").json()["briefing"]["text"] is None
    assert c.get("/api/topics/nope").status_code == 404
    m.app.dependency_overrides.clear()
