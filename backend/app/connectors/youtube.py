from __future__ import annotations

from datetime import datetime, timezone

import httpx

from ..config import settings
from .base import Connector, ConnectorError, RawItem

API = "https://www.googleapis.com/youtube/v3"


class YouTubeConnector(Connector):
    """Official YouTube Data API only. Live status comes from liveBroadcastContent, not from titles."""
    name = "youtube"

    def fetch(self) -> list[RawItem]:
        if not settings.youtube_api_key:
            raise ConnectorError("YOUTUBE_API_KEY not set")
        region = self.config.get("region_code", "PH")
        try:
            r = httpx.get(f"{API}/videos", timeout=15, params={
                "part": "snippet,statistics,liveStreamingDetails", "chart": "mostPopular",
                "regionCode": region, "maxResults": 25, "key": settings.youtube_api_key})
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise ConnectorError(f"youtube request failed: {type(e).__name__}") from e
        out = []
        for v in r.json().get("items", []):
            sn, st = v["snippet"], v.get("statistics", {})
            lbc = sn.get("liveBroadcastContent", "none")
            live = {"live": "live", "upcoming": "upcoming"}.get(lbc)
            if lbc == "none" and v.get("liveStreamingDetails", {}).get("actualEndTime"):
                live = "completed"
            eng = {k: int(st[k]) for k in ("viewCount", "likeCount", "commentCount") if k in st} or None
            out.append(RawItem(
                title=sn["title"], url=f"https://www.youtube.com/watch?v={v['id']}",
                published_at=datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00")).astimezone(timezone.utc),
                snippet=sn.get("description", "")[:280], author=sn.get("channelTitle", ""),
                kind="video", platform="youtube", category=self.config.get("category", "entertainment"),
                region=region, engagement=eng, live_status=live, extra={"video_id": v["id"]}))
        return out
