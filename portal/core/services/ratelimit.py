"""A per-visitor cooldown for the AI features, stored in the cache."""

import time

from django.core.cache import cache


def client_ip(request):
    # Render puts the visitor's address first in X-Forwarded-For.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def seconds_to_wait(request, action, cooldown_seconds):
    """Return 0 and start the cooldown, or return how many seconds are left."""
    key = f"cooldown:{action}:{client_ip(request)}"
    now = time.time()
    if cache.add(key, now, cooldown_seconds):
        return 0
    started = cache.get(key, now)
    return max(1, round(cooldown_seconds - (now - started)))
