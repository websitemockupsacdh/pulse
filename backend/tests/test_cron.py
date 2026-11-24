from fastapi.testclient import TestClient
from app import main as m
from app.config import settings
from app.db import get_db
from tests.test_core import db  # noqa: F401


def test_cron_requires_secret(db, monkeypatch):
    monkeypatch.setattr(settings, "cron_secret", "s3cret")
    m.app.dependency_overrides[get_db] = lambda: db
    c = TestClient(m.app)
    assert c.get("/api/cron/ingest").status_code == 401
    assert c.get("/api/cron/ingest", headers={"Authorization": "Bearer wrong"}).status_code == 401
    monkeypatch.setattr("app.services.pipeline.build", lambda *a: type("X", (), {"fetch": lambda s: []})())
    assert c.get("/api/cron/ingest", headers={"Authorization": "Bearer s3cret"}).status_code == 200
    m.app.dependency_overrides.clear()


def test_cron_disabled_without_secret(db, monkeypatch):
    monkeypatch.setattr(settings, "cron_secret", "")
    m.app.dependency_overrides[get_db] = lambda: db
    assert TestClient(m.app).get("/api/cron/ingest", headers={"Authorization": "Bearer "}).status_code == 401
    m.app.dependency_overrides.clear()


def test_db_url_normalized():
    from app.db import _normalize
    assert _normalize("postgresql://u:p@h/d?sslmode=require") == "postgresql+psycopg://u:p@h/d?sslmode=require"
    assert _normalize("postgres://u@h/d").startswith("postgresql+psycopg://")
    assert _normalize("sqlite:///x.db") == "sqlite:///x.db"
