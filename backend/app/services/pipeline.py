"""Normalize -> validate -> deduplicate -> store -> attach to topic."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..connectors.base import ConnectorError, RawItem
from ..connectors.registry import build
from ..models import Item, Source
from .text import title_fp, url_hash

log = logging.getLogger("pulse.pipeline")
VALID_LIVE = {"live", "upcoming", "completed", None}


def validate(raw: RawItem) -> bool:
    if not raw.title or not raw.url.startswith(("http://", "https://")):
        return False
    if raw.live_status not in VALID_LIVE:
        return False
    return raw.published_at <= datetime.now(timezone.utc).replace(microsecond=0) + __import__("datetime").timedelta(hours=1)


def ingest_source(db: Session, source: Source) -> int:
    try:
        raws = build(source.connector, source.config or {}, source.url).fetch()
    except ConnectorError as e:
        source.last_status = f"error: {e}"[:250]
        source.last_run_at = datetime.now(timezone.utc)
        db.commit()
        log.warning("source %s failed: %s", source.slug, e)
        return 0

    from .trends import attach_to_topic  # local import avoids cycle
    added = 0
    for raw in raws:
        if not validate(raw):
            continue
        h = url_hash(raw.url)
        if db.scalar(select(Item.id).where(Item.url_hash == h)):
            continue
        item = Item(
            source_id=source.id, kind=raw.kind, platform=raw.platform,
            category=raw.category or "national", region=raw.region or source.region,
            title=raw.title, snippet=raw.snippet, image_url=raw.image_url, url=raw.url, url_hash=h, title_fp=title_fp(raw.title),
            author=raw.author, published_at=raw.published_at, engagement=raw.engagement,
            live_status=raw.live_status, severity=raw.severity, syndicated=raw.syndicated)
        db.add(item)
        db.flush()
        attach_to_topic(db, item)
        from .notifications import push_item
        push_item(db, item)
        added += 1
    source.last_status = f"ok: {added} new of {len(raws)}"
    source.last_run_at = datetime.now(timezone.utc)
    db.commit()
    return added


def ingest_all(db: Session, budget_s: float | None = None) -> dict[str, int]:
    """Stalest sources first. Stops when the time budget is spent so serverless calls finish in time."""
    import time
    start = time.monotonic()
    srcs = sorted(db.scalars(select(Source).where(Source.enabled)),
                  key=lambda s: (s.last_run_at is not None, s.last_run_at or 0) if s.last_run_at is None else (True, s.last_run_at.timestamp()))
    out: dict[str, int] = {}
    for s in srcs:
        if budget_s is not None and time.monotonic() - start > budget_s:
            break
        out[s.slug] = ingest_source(db, s)
    return out
