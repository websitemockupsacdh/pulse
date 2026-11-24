"""Universal search. Indexed retrieval first. AI only expands queries afterward.

SQL backend is the default so local dev needs no OpenSearch. `opensearch_url` switches the
backend; the interface stays the same.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.orm import Session

from ..models import Item, Source, Topic


def parse_query(q: str) -> tuple[list[str], list[str]]:
    phrases = re.findall(r'"([^"]+)"', q)
    rest = re.sub(r'"[^"]+"', " ", q)
    words = [w for w in re.findall(r"\w+", rest.lower()) if len(w) > 1]
    return [p.lower() for p in phrases], words


def search(db: Session, q: str, *, kind: str | None = None, platform: str | None = None,
           publisher: str | None = None, category: str | None = None, region: str | None = None,
           since_hours: int | None = None, sort: str = "relevance", limit: int = 30, offset: int = 0) -> dict:
    phrases, words = parse_query(q)
    stmt = select(Item, Source).join(Source, Source.id == Item.source_id).where(Item.kind.notin_(("social", "video")))
    for term in phrases + words:
        like = f"%{term}%"
        stmt = stmt.where(or_(Item.title.ilike(like), Item.snippet.ilike(like)))
    if kind: stmt = stmt.where(Item.kind == kind)
    if platform: stmt = stmt.where(Item.platform == platform)
    if publisher: stmt = stmt.where(Source.slug == publisher)
    if category: stmt = stmt.where(Item.category == category)
    if region: stmt = stmt.where(Item.region == region)
    if since_hours: stmt = stmt.where(Item.published_at >= datetime.now(timezone.utc) - timedelta(hours=since_hours))
    rows = db.execute(stmt.order_by(desc(Item.published_at)).limit(500)).all()

    def score(it: Item) -> float:
        t = it.title.lower()
        s = sum(3 for term in phrases + words if term in t) + sum(1 for term in phrases + words if term in it.snippet.lower())
        return s
    def pop(it: Item) -> int:
        e = it.engagement or {}
        return e.get("viewCount") or e.get("score") or 0
    if sort == "relevance": rows.sort(key=lambda r: (score(r[0]), r[0].published_at), reverse=True)
    elif sort == "popularity": rows.sort(key=lambda r: pop(r[0]), reverse=True)
    page = rows[offset: offset + limit]

    topics = []
    if words or phrases:
        tstmt = select(Topic).where(Topic.status != "archived")
        for term in phrases + words:
            tstmt = tstmt.where(Topic.title.ilike(f"%{term}%"))
        topics = db.scalars(tstmt.order_by(desc(Topic.velocity)).limit(6)).all()
    return {"total": len(rows), "items": page, "topics": topics}
