from __future__ import annotations

from .base import Connector, ConnectorError, RawItem


class UnavailableSocialConnector(Connector):
    """Adapter slot for X, Threads, Facebook, Instagram, TikTok.

    Each platform needs authorized API access under its own terms. Until credentials and
    approval exist, the adapter reports unavailable. It does not scrape and does not fabricate.
    """
    name = "social_unavailable"

    def fetch(self) -> list[RawItem]:
        raise ConnectorError(f"{self.config.get('platform', 'platform')} adapter has no authorized access configured")


class RedditConnector(Connector):
    """Reddit public listing JSON for configured subreddits. Subject to Reddit API terms and rate limits."""
    name = "reddit"

    def fetch(self) -> list[RawItem]:
        import httpx
        from datetime import datetime, timezone
        from ..config import settings
        try:
            r = httpx.get(self.url, headers={"User-Agent": settings.user_agent}, timeout=15, follow_redirects=True)
            r.raise_for_status()
            children = r.json()["data"]["children"]
        except (httpx.HTTPError, KeyError, ValueError) as e:
            raise ConnectorError(f"reddit fetch failed: {type(e).__name__}") from e
        out = []
        for c in children:
            d = c["data"]
            out.append(RawItem(
                title=d["title"], url="https://www.reddit.com" + d["permalink"],
                published_at=datetime.fromtimestamp(d["created_utc"], tz=timezone.utc),
                snippet=(d.get("selftext") or "")[:280], author=d.get("author", ""),
                kind="social", platform="reddit", category="national",
                engagement={"score": d["score"], "comments": d["num_comments"]}))
        return out
