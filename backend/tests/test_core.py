from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.connectors.base import RawItem
from app.db import Base
from app.models import Item, Source
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
    run(db, [raw("Some discussion thread about transport", "https://r.com/1", kind="social")], "reddit-ph")
    assert db.query(Item).one().engagement is None


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
    assert c.get("/api/home").json()["sections"][0]["key"] == "breaking"
    slug = db.query(trends.Topic).one().slug
    assert c.get(f"/api/topics/{slug}").json()["briefing"]["text"] is None
    assert c.get("/api/topics/nope").status_code == 404
    m.app.dependency_overrides.clear()
