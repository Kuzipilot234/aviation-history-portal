"""Historical events for today's date, from Wikipedia's "On this day" feed."""

import logging

import httpx
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

FEED_URL = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/{month:02d}/{day:02d}"
USER_AGENT = "KuzeyPortal/1.0 (https://kuzipilot.onrender.com)"
CACHE_SECONDS = 12 * 60 * 60
EVENT_COUNT = 4


def _parse(data):
    events = []
    for item in data.get("selected", []):
        pages = item.get("pages") or [{}]
        page = pages[0]
        events.append(
            {
                "year": item.get("year"),
                "text": item.get("text", ""),
                "url": page.get("content_urls", {}).get("desktop", {}).get("page", ""),
            }
        )
    # Oldest first reads like a timeline.
    events.sort(key=lambda event: event["year"] or 0)
    return events


def todays_events():
    """Return a few events for today's date. Raises if Wikipedia can't be reached."""
    today = timezone.localdate()
    key = f"onthisday:{today:%m-%d}"
    events = cache.get(key)
    if events is None:
        response = httpx.get(
            FEED_URL.format(month=today.month, day=today.day),
            headers={"User-Agent": USER_AGENT},
            timeout=10,
            follow_redirects=True,
        )
        response.raise_for_status()
        events = _parse(response.json())
        cache.set(key, events, CACHE_SECONDS)
    if len(events) <= EVENT_COUNT:
        return events
    # Spread the picks across the centuries instead of taking the first few.
    step = len(events) / EVENT_COUNT
    return [events[int(i * step)] for i in range(EVENT_COUNT)]
