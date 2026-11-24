from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    name: str
    kind: str
    region: str
    url: str
    enabled: bool
    last_status: str
    last_run_at: datetime | None


class ItemOut(BaseModel):
    id: int
    title: str
    snippet: str
    image_url: str | None = None
    url: str
    kind: str
    platform: str
    category: str
    region: str
    author: str
    publisher: str
    published_at: datetime
    engagement: dict[str, int] | None  # null = unavailable from source
    live_status: str | None
    severity: str | None
    syndicated: bool
    topic_slug: str | None = None


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    title: str
    category: str
    region: str
    first_detected_at: datetime
    last_updated_at: datetime
    item_count: int
    source_count: int
    velocity: float
    status: str
    summary: str


class PushSubscriptionIn(BaseModel):
    endpoint: str = Field(min_length=12, max_length=2048)
    keys: dict[str, str]
    categories: list[str] = Field(default_factory=list, max_length=20)
    keywords: list[str] = Field(default_factory=list, max_length=10)


class PushUnsubscribeIn(BaseModel):
    endpoint: str = Field(min_length=12, max_length=2048)
