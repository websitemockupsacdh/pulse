import asyncio
import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import SessionLocal, get_db
from ..models import Item, PageSection, Source, Topic
from ..services import search as search_svc
from .schemas import ItemOut, SourceOut, TopicOut

router = APIRouter(prefix="/api")
HOURS = {"1h": 1, "6h": 6, "24h": 24, "7d": 168}


def item_out(it: Item, topic_slug: str | None = None) -> ItemOut:
    return ItemOut(id=it.id, title=it.title, snippet=it.snippet, url=it.url, kind=it.kind, platform=it.platform,
                   category=it.category, region=it.region, author=it.author, publisher=it.source.name,
                   published_at=it.published_at, engagement=it.engagement, live_status=it.live_status,
                   severity=it.severity, syndicated=it.syndicated, topic_slug=topic_slug)


def _items(db: Session, *, kind=None, region=None, category=None, categories=None, hours=None, platform=None,
           live=None, limit=20) -> list[ItemOut]:
    q = select(Item).order_by(desc(Item.published_at)).limit(limit)
    if kind: q = q.where(Item.kind == kind)
    if region: q = q.where(Item.region == region)
    if category: q = q.where(Item.category == category)
    if categories: q = q.where(Item.category.in_(categories))
    if platform: q = q.where(Item.platform == platform)
    if live: q = q.where(Item.live_status == live)
    if hours: q = q.where(Item.published_at >= datetime.now(timezone.utc) - timedelta(hours=hours))
    return [item_out(i) for i in db.scalars(q)]


def _topics(db: Session, *, status=None, region=None, category=None, hours=None, limit=20, sort="velocity") -> list[Topic]:
    q = select(Topic).where(Topic.status != "archived") if not status else select(Topic).where(Topic.status == status)
    if region: q = q.where(Topic.region == region)
    if category: q = q.where(Topic.category == category)
    if hours: q = q.where(Topic.last_updated_at >= datetime.now(timezone.utc) - timedelta(hours=hours))
    col = {"velocity": desc(Topic.velocity), "recent": desc(Topic.last_updated_at), "size": desc(Topic.item_count)}[sort]
    return list(db.scalars(q.order_by(col, desc(Topic.source_count)).limit(limit)))


@router.get("/health")
def health():
    return {"ok": True}


@router.get("/home")
def home(region: str = "PH", db: Session = Depends(get_db)):
    """Layout and content in one payload. Sections come from the page_sections table."""
    out = []
    for sec in db.scalars(select(PageSection).where(PageSection.page == "home", PageSection.enabled).order_by(PageSection.position)):
        q = sec.query or {}
        body: dict = {}
        if q.get("topics"):
            body["topics"] = [TopicOut.model_validate(t) for t in _topics(
                db, status=q.get("status"), region=region, limit=q.get("limit", 8), hours=q.get("hours"))]
        elif sec.key != "briefing":
            r = q.get("region", region if q.get("region") != "INTL" else "INTL")
            body["items"] = _items(db, kind=q.get("kind"), region=r, category=q.get("category"),
                                   categories=q.get("categories"), hours=q.get("hours"), limit=q.get("limit", 6))
        out.append({"key": sec.key, "title": sec.title, **body})
    return {"region": region, "generated_at": datetime.now(timezone.utc), "sections": out}


@router.get("/trending", response_model=list[TopicOut])
def trending(region: str | None = None, category: str | None = None, window: str | None = Query(None, pattern="^(1h|6h|24h|7d)$"),
             status: str | None = None, sort: str = Query("velocity", pattern="^(velocity|recent|size)$"),
             limit: int = 40, db: Session = Depends(get_db)):
    return _topics(db, status=status, region=region, category=category, hours=HOURS.get(window or ""), limit=limit, sort=sort)


@router.get("/feed", response_model=list[ItemOut])
def feed(kind: str | None = None, category: str | None = None, region: str | None = None, platform: str | None = None,
         live: str | None = Query(None, pattern="^(live|upcoming|completed)$"), window: str | None = None,
         limit: int = Query(30, le=100), db: Session = Depends(get_db)):
    return _items(db, kind=kind, category=category, region=region, platform=platform, live=live,
                  hours=HOURS.get(window or ""), limit=limit)


@router.get("/search")
def search(q: str = Query("", max_length=200), kind: str | None = None, platform: str | None = None,
           publisher: str | None = None, category: str | None = None, region: str | None = None,
           window: str | None = None, sort: str = Query("relevance", pattern="^(relevance|recent|popularity)$"),
           limit: int = Query(30, le=100), offset: int = 0, db: Session = Depends(get_db)):
    r = search_svc.search(db, q, kind=kind, platform=platform, publisher=publisher, category=category, region=region,
                          since_hours=HOURS.get(window or ""), sort=sort, limit=limit, offset=offset)
    return {"total": r["total"], "items": [item_out(i, None) for i, _ in r["items"]],
            "topics": [TopicOut.model_validate(t) for t in r["topics"]]}


@router.get("/topics/{slug}")
def topic_explorer(slug: str, db: Session = Depends(get_db)):
    t = db.scalar(select(Topic).where(Topic.slug == slug))
    if not t:
        raise HTTPException(404, "topic not found")
    items = list(db.scalars(select(Item).where(Item.topic_id == t.id).order_by(Item.published_at)))
    by = lambda pred: [item_out(i, t.slug) for i in items if pred(i)]
    related = [x for x in db.scalars(select(Topic).where(Topic.id != t.id, Topic.status != "archived").limit(200))
               if len(set(x.keywords) & set(t.keywords)) >= 2][:6]
    return {
        "topic": TopicOut.model_validate(t),
        # Briefing is only what sources state. Empty until the AI layer attaches cited text.
        "briefing": {"text": t.summary or None, "citations": [i.url for i in items[:5]] if t.summary else [],
                     "note": None if t.summary else "No AI briefing generated yet. Source list below is complete."},
        "timeline": [{"at": i.published_at, "title": i.title, "publisher": i.source.name, "url": i.url} for i in items],
        "ph_news": by(lambda i: i.kind == "news" and i.region == "PH"),
        "international": by(lambda i: i.kind == "news" and i.region != "PH"),
        "social": by(lambda i: i.kind == "social"),
        "videos": by(lambda i: i.kind == "video" and i.live_status in (None, "completed")),
        "live": by(lambda i: i.kind == "video" and i.live_status in ("live", "upcoming")),
        "official": by(lambda i: i.kind == "official"),
        "conflicts": [],  # populated by the intelligence engine when sources disagree
        "related_topics": [TopicOut.model_validate(x) for x in related],
        "sources": sorted({(i.source.name, i.url) for i in items}),
    }


@router.get("/sources", response_model=list[SourceOut])
def sources(db: Session = Depends(get_db)):
    return list(db.scalars(select(Source).order_by(Source.kind, Source.name)))


@router.get("/cron/ingest")
def cron_ingest(authorization: str | None = Header(None), db: Session = Depends(get_db)):
    """Collect from sources and refresh trends. Called by a scheduler with `Authorization: Bearer $CRON_SECRET`."""
    import hmac
    from ..services.pipeline import ingest_all
    from ..services.trends import refresh_topics
    if not settings.cron_secret or not hmac.compare_digest(authorization or "", f"Bearer {settings.cron_secret}"):
        raise HTTPException(401, "unauthorized")
    result = ingest_all(db, budget_s=settings.ingest_budget_s)
    return {"ingested": result, "topics_refreshed": refresh_topics(db)}


@router.get("/stream")
async def stream():
    """Server-Sent Events: pushes a lightweight pulse so dashboards know when to refetch."""
    async def gen():
        last = None
        while True:
            with SessionLocal() as db:
                cur = db.scalar(select(Item.id).order_by(desc(Item.id)).limit(1))
            if cur != last:
                last = cur
                yield f"event: update\ndata: {json.dumps({'latest_item_id': cur})}\n\n"
            else:
                yield ": keepalive\n\n"
            await asyncio.sleep(15)
    return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
