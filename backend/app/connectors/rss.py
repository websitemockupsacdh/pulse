from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from time import mktime

import feedparser
import httpx

from ..config import settings
from .base import Connector, ConnectorError, RawItem

TAG = re.compile(r"<[^>]+>")


def clean(text: str, limit: int = 280) -> str:
    text = unescape(TAG.sub(" ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "..."


class RSSConnector(Connector):
    """Publisher RSS/Atom. Stores title, short snippet, link. Never the full article."""
    name = "rss"

    def fetch(self) -> list[RawItem]:
        try:
            r = httpx.get(self.url, headers={"User-Agent": settings.user_agent}, timeout=15, follow_redirects=True)
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise ConnectorError(f"fetch failed: {e}") from e
        feed = feedparser.parse(r.content)
        if feed.bozo and not feed.entries:
            raise ConnectorError("feed did not parse")
        out: list[RawItem] = []
        for e in feed.entries:
            link, title = e.get("link"), clean(e.get("title", ""), 512)
            if not link or not title:
                continue
            needle = self.config.get("filter_contains")
            if needle and needle.lower() not in (title + " " + e.get("summary", "") + " " + str(e.get("gdacs_country", ""))).lower():
                continue
            level = e.get("gdacs_alertlevel")
            ts = e.get("published_parsed") or e.get("updated_parsed")
            published = datetime.fromtimestamp(mktime(ts), tz=timezone.utc) if ts else datetime.now(timezone.utc)
            out.append(RawItem(
                title=title, url=link, published_at=published,
                snippet=clean(e.get("summary", "")), author=e.get("author", ""),
                kind=self.config.get("kind", "news"),
                category=self.config.get("category"),
                syndicated=bool(self.config.get("syndicated", False)),
                severity=f"{level} alert level (GDACS)" if level else None,
            ))
        return out
