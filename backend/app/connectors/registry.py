from .base import Connector
from .rss import RSSConnector
from .social import RedditConnector, UnavailableSocialConnector
from .youtube import YouTubeConnector

# Adding a connector type = one line here. Adding a publisher = one row in `sources`.
CONNECTORS: dict[str, type[Connector]] = {
    "rss": RSSConnector,
    "youtube": YouTubeConnector,
    "reddit": RedditConnector,
    "social_unavailable": UnavailableSocialConnector,
}


def build(connector: str, config: dict, url: str) -> Connector:
    if connector not in CONNECTORS:
        raise KeyError(f"unknown connector '{connector}'")
    return CONNECTORS[connector](config, url)
