"""Deliver source-linked web push notifications for reader-selected criteria."""
import json
import logging

from requests import RequestException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Item, PushSubscription

log = logging.getLogger("pulse.notifications")


def push_item(db: Session, item: Item) -> None:
    if not settings.vapid_public_key or not settings.vapid_private_key:
        return
    subscriptions = db.scalars(select(PushSubscription)).all()
    if not subscriptions:
        return

    from pywebpush import WebPushException, webpush

    payload = json.dumps({"title": item.title, "publisher": item.source.name, "url": item.url})
    for subscription in subscriptions:
        criteria = subscription.criteria or {}
        categories = criteria.get("categories", [])
        keywords = [word.casefold() for word in criteria.get("keywords", [])]
        text = f"{item.title} {item.snippet}".casefold()
        matches = item.category in categories or any(word in text for word in keywords)
        if not matches:
            continue
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": subscription.keys,
                },
                data=payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_subject},
                timeout=5,
            )
        except (WebPushException, RequestException) as error:
            response = getattr(error, "response", None)
            status = response.status_code if isinstance(error, WebPushException) and response is not None else None
            if status in (404, 410):
                db.delete(subscription)
                log.info("removed expired push subscription (HTTP %s)", status)
            else:
                log.warning("push delivery failed (HTTP %s): %s", status, error)
