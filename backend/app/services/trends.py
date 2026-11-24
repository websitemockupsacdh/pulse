"""Topic clustering and status. Status comes from measured velocity and configurable thresholds."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Item, Topic
from .text import jaccard, slugify, tokens

JOIN_THRESHOLD = 0.45
CANDIDATE_WINDOW_H = 72


def attach_to_topic(db: Session, item: Item) -> Topic | None:
    if item.kind in ("official",):
        return None
    toks = tokens(item.title)
    if len(toks) < 2:
        return None
    since = datetime.now(timezone.utc) - timedelta(hours=CANDIDATE_WINDOW_H)
    best, best_score = None, 0.0
    for t in db.scalars(select(Topic).where(Topic.last_updated_at >= since, Topic.region == item.region)):
        score = jaccard(toks, set(t.keywords))
        if score > best_score:
            best, best_score = t, score
    if best and best_score >= JOIN_THRESHOLD:
        topic = best
        topic.keywords = sorted(set(topic.keywords) | toks)[:40]
    else:
        slug = slugify(item.title)
        if db.scalar(select(Topic.id).where(Topic.slug == slug)):
            slug = f"{slug}-{item.id}"
        topic = Topic(slug=slug, title=item.title, category=item.category, region=item.region,
                      keywords=sorted(toks), first_detected_at=item.published_at)
        db.add(topic)
        db.flush()
    item.topic_id = topic.id
    topic.last_updated_at = max(item.published_at, topic.last_updated_at.replace(tzinfo=timezone.utc)
                                if topic.last_updated_at.tzinfo is None else topic.last_updated_at)
    return topic


def status_for(age_h: float, velocity: float, idle_h: float, items: int) -> str:
    s = settings
    if idle_h >= s.trend_archive_after_h:
        return "archived"
    if age_h <= s.trend_emerging_max_age_h and items >= 1:
        return "emerging"
    if velocity >= s.trend_rising_velocity:
        return "rising"
    if velocity <= s.trend_declining_velocity:
        return "declining"
    return "active"


def refresh_topics(db: Session) -> int:
    now = datetime.now(timezone.utc)
    window = now - timedelta(hours=6)
    n = 0
    for t in db.scalars(select(Topic).where(Topic.status != "archived")):
        total, srcs = db.execute(select(func.count(Item.id), func.count(func.distinct(Item.source_id)))
                                 .where(Item.topic_id == t.id)).one()
        recent = db.scalar(select(func.count(Item.id)).where(Item.topic_id == t.id, Item.published_at >= window)) or 0
        last = db.scalar(select(func.max(Item.published_at)).where(Item.topic_id == t.id)) or t.first_detected_at
        first = t.first_detected_at if t.first_detected_at.tzinfo else t.first_detected_at.replace(tzinfo=timezone.utc)
        last = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
        t.item_count, t.source_count = total, srcs
        t.velocity = round(recent / 6, 2)
        t.last_updated_at = last
        t.status = status_for((now - first).total_seconds() / 3600, t.velocity, (now - last).total_seconds() / 3600, total)
        n += 1
    db.commit()
    return n
