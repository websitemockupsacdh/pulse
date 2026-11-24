from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def now() -> datetime:
    return datetime.now(timezone.utc)


class Source(Base):
    """Source registry. New publishers are rows, not code."""
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(128))
    connector: Mapped[str] = mapped_column(String(32))  # rss | youtube | pagasa | phivolcs ...
    kind: Mapped[str] = mapped_column(String(24))  # news | social | video | official | science
    region: Mapped[str] = mapped_column(String(8), default="PH")
    url: Mapped[str] = mapped_column(String(512))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_status: Mapped[str] = mapped_column(String(256), default="never run")


class Item(Base):
    """One normalized piece of public content with its original URL."""
    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("url_hash", name="uq_item_url"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    kind: Mapped[str] = mapped_column(String(24), index=True)
    platform: Mapped[str] = mapped_column(String(24), default="web")
    category: Mapped[str] = mapped_column(String(32), default="national", index=True)
    region: Mapped[str] = mapped_column(String(8), default="PH", index=True)
    title: Mapped[str] = mapped_column(String(512))
    snippet: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str | None] = mapped_column(String(1024))
    url: Mapped[str] = mapped_column(String(1024))
    url_hash: Mapped[str] = mapped_column(String(64))
    title_fp: Mapped[str] = mapped_column(String(64), index=True)
    author: Mapped[str] = mapped_column(String(256), default="")
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    # None means the platform did not supply it. Never coerce to zero.
    engagement: Mapped[dict | None] = mapped_column(JSON)
    live_status: Mapped[str | None] = mapped_column(String(16))  # live | upcoming | completed, from source
    severity: Mapped[str | None] = mapped_column(String(64))  # official wording only
    syndicated: Mapped[bool] = mapped_column(Boolean, default=False)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), index=True)
    source: Mapped[Source] = relationship()


class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    title: Mapped[str] = mapped_column(String(512))
    category: Mapped[str] = mapped_column(String(32), default="national")
    region: Mapped[str] = mapped_column(String(8), default="PH")
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    first_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    velocity: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(16), default="emerging", index=True)
    summary: Mapped[str] = mapped_column(Text, default="")  # filled by the AI layer, always source-backed


class PageSection(Base):
    """Home layout lives in data so new categories need no frontend release."""
    __tablename__ = "page_sections"
    id: Mapped[int] = mapped_column(primary_key=True)
    page: Mapped[str] = mapped_column(String(32), default="home")
    position: Mapped[int] = mapped_column(Integer)
    key: Mapped[str] = mapped_column(String(48))
    title: Mapped[str] = mapped_column(String(128))
    query: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class PushSubscription(Base):
    """Browser push endpoint and reader-selected alert criteria."""
    __tablename__ = "push_subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    endpoint: Mapped[str] = mapped_column(String(2048), unique=True)
    keys: Mapped[dict] = mapped_column(JSON)
    criteria: Mapped[dict] = mapped_column(JSON, default=dict)


class AppSetting(Base):
    """Persist one-time data initialization markers without overwriting managed records."""
    __tablename__ = "app_settings"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(256))
