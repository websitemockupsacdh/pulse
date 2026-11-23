"""Celery schedule. Run: celery -A app.tasks worker -B"""
from celery import Celery

from .config import settings
from .db import SessionLocal
from .services.pipeline import ingest_all
from .services.trends import refresh_topics

celery = Celery("pulse", broker=settings.redis_url or "memory://", backend=None)
celery.conf.beat_schedule = {
    "ingest": {"task": "app.tasks.ingest", "schedule": 300.0},
    "refresh": {"task": "app.tasks.refresh", "schedule": 120.0},
}


@celery.task(name="app.tasks.ingest")
def ingest():
    with SessionLocal() as db:
        return ingest_all(db)


@celery.task(name="app.tasks.refresh")
def refresh():
    with SessionLocal() as db:
        return refresh_topics(db)
