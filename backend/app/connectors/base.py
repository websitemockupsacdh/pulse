from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RawItem:
    """What a connector hands the pipeline. Connectors never touch the database."""
    title: str
    url: str
    published_at: datetime
    snippet: str = ""
    author: str = ""
    kind: str = "news"
    platform: str = "web"
    category: str | None = None
    region: str | None = None
    engagement: dict[str, int] | None = None  # None = unavailable, never 0
    live_status: str | None = None
    severity: str | None = None
    syndicated: bool = False
    image_url: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class ConnectorError(Exception):
    pass


class Connector(ABC):
    """Contract every source adapter implements."""
    name: str = ""

    def __init__(self, source_config: dict[str, Any], source_url: str):
        self.config = source_config
        self.url = source_url

    @abstractmethod
    def fetch(self) -> list[RawItem]:
        """Return items or raise ConnectorError. Must not invent data."""
