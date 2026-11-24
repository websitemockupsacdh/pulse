from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from time import mktime
from urllib.parse import urljoin

import feedparser
import httpx

from ..config import settings
from .base import Connector, ConnectorError, RawItem

TAG = re.compile(r"<[^>]+>")
IMG = re.compile(r"""<img\b[^>]*?\bsrc\s*=\s*["']([^"']+)["']""", re.I)


class FeedLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "link":
            return
        values = dict(attrs)
        rel = values.get("rel", "").lower().split()
        media_type = values.get("type", "").lower()
        href = values.get("href")
        if href and "alternate" in rel and any(t in media_type for t in ("rss", "atom", "xml")):
            self.urls.append(href)


def clean(text: str, limit: int = 280) -> str:
    text = unescape(TAG.sub(" ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "..."


class RSSConnector(Connector):
    """Publisher RSS/Atom. Discovers feed links from publisher pages; stores no article body."""
    name = "rss"

    def fetch(self) -> list[RawItem]:
        try:
            r = httpx.get(self.url, headers={"User-Agent": settings.user_agent}, timeout=15, follow_redirects=True)
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise ConnectorError(f"fetch failed: {e}") from e
        feed = feedparser.parse(r.content)
        if not feed.entries:
            links = FeedLinks()
            if "html" in r.headers.get("content-type", "").lower() or b"<html" in r.content[:512].lower():
                links.feed(r.text)
            for candidate in links.urls:
                try:
                    response = httpx.get(urljoin(str(r.url), candidate), headers={"User-Agent": settings.user_agent},
                                         timeout=15, follow_redirects=True)
                    response.raise_for_status()
                except httpx.HTTPError:
                    continue
                discovered = feedparser.parse(response.content)
                if discovered.entries:
                    feed = discovered
                    break
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
            image = None
            for candidate in (e.get("media_content") or []) + (e.get("media_thumbnail") or []):
                if isinstance(candidate, dict) and candidate.get("url"):
                    image = candidate["url"]
                    break
            if not image:
                for content in e.get("content") or []:
                    match = IMG.search(content.get("value", ""))
                    if match:
                        image = match.group(1)
                        break
            if not image:
                for enclosure in e.get("enclosures") or []:
                    if enclosure.get("type", "").startswith("image/"):
                        image = enclosure.get("href") or enclosure.get("url")
                        break
            if not image:
                match = IMG.search(e.get("summary", ""))
                if match:
                    image = match.group(1)
            if image and not image.startswith(("http://", "https://")):
                image = urljoin(link, image)
            out.append(RawItem(
                title=title, url=link, published_at=published,
                snippet=clean(e.get("summary", "")), author=e.get("author", ""),
                kind=self.config.get("kind", "news"),
                category=self.config.get("category"),
                image_url=image if image and image.startswith(("http://", "https://")) else None,
                syndicated=bool(self.config.get("syndicated", False)),
                severity=f"{level} alert level (GDACS)" if level else None,
            ))
        return out
