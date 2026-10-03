"""Live aircraft positions over Türkiye from adsb.lol.

adsb.lol is a free, open ADS-B network. Its API returns aircraft within
250 nautical miles of a point, so Türkiye is covered with three circles.
OpenSky was used first, but it blocks requests from cloud hosts like Render.

Results are shared through the cache. When adsb.lol is unavailable, the
last good result is shown.
"""

import logging
import time

import httpx
from django.core.cache import cache

logger = logging.getLogger(__name__)

POINT_URL = "https://api.adsb.lol/v2/point/{lat}/{lon}/{radius}"
USER_AGENT = "KuzeyPortal/1.0 (https://kuzipilot.onrender.com)"
# West, central and east Türkiye; 250 nm is the API's largest radius.
SEARCH_CIRCLES = [(39.8, 29.0), (39.0, 35.0), (39.0, 41.0)]
RADIUS_NM = 250
CENTER = [39.0, 35.2]
FRESH_SECONDS = 2 * 60
STALE_SECONDS = 24 * 60 * 60
CACHE_KEY = "flights:turkiye"
MAX_AIRCRAFT = 500


def _number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _parse(aircraft_list):
    aircraft = {}
    for plane in aircraft_list or []:
        lat, lon = _number(plane.get("lat")), _number(plane.get("lon"))
        # adsb.lol reports "ground" as the altitude of taxiing aircraft.
        if lat is None or lon is None or plane.get("alt_baro") == "ground":
            continue
        icao = plane.get("hex", "")
        altitude = _number(plane.get("alt_geom")) or _number(plane.get("alt_baro"))
        speed, heading = _number(plane.get("gs")), _number(plane.get("track"))
        aircraft[icao] = {
            "id": icao,
            "callsign": (plane.get("flight") or "").strip() or plane.get("r") or icao.upper(),
            "type": plane.get("t") or "",
            "registration": plane.get("r") or "",
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "altitude_ft": round(altitude) if altitude is not None else None,
            "speed_kt": round(speed) if speed is not None else None,
            "heading": round(heading) if heading is not None else 0,
        }
    return list(aircraft.values())[:MAX_AIRCRAFT]


def _fetch():
    combined = []
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=15) as client:
        for lat, lon in SEARCH_CIRCLES:
            response = client.get(POINT_URL.format(lat=lat, lon=lon, radius=RADIUS_NM))
            response.raise_for_status()
            combined += response.json().get("ac") or []
    # Overlapping circles report some aircraft twice; _parse keys by ICAO address.
    return _parse(combined)


def live_flights():
    """Return {"aircraft": [...], "updated": unix time, "stale": bool}."""
    cached = cache.get(CACHE_KEY)
    if cached and time.time() - cached["updated"] < FRESH_SECONDS:
        return {**cached, "stale": False}

    try:
        result = {"aircraft": _fetch(), "updated": int(time.time())}
    except Exception:
        logger.warning("adsb.lol request failed", exc_info=True)
        if cached:
            return {**cached, "stale": True}
        return {"aircraft": [], "updated": None, "stale": True}

    cache.set(CACHE_KEY, result, STALE_SECONDS)
    return {**result, "stale": False}
