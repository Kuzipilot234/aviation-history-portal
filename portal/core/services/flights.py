"""Live aircraft positions over Türkiye from the OpenSky Network.

Anonymous OpenSky access allows about 400 credits a day and this area costs
3 credits per request, so results are shared through the cache. When OpenSky
is unavailable or the daily limit is reached, the last good result is shown.
"""

import logging
import time

import httpx
from django.core.cache import cache

logger = logging.getLogger(__name__)

STATES_URL = "https://opensky-network.org/api/states/all"
# Türkiye, with a little of the surrounding airspace.
AREA = {"lamin": 35.8, "lomin": 25.6, "lamax": 42.2, "lomax": 44.9}
CENTER = [39.0, 35.2]
FRESH_SECONDS = 3 * 60
STALE_SECONDS = 24 * 60 * 60
CACHE_KEY = "flights:turkiye"
MAX_AIRCRAFT = 400

METERS_TO_FEET = 3.28084
MS_TO_KNOTS = 1.94384


def _parse(states):
    aircraft = []
    for state in states or []:
        icao24, callsign, country = state[0], (state[1] or "").strip(), state[2]
        lon, lat, baro_altitude, on_ground = state[5], state[6], state[7], state[8]
        velocity, heading, geo_altitude = state[9], state[10], state[13]
        if on_ground or lat is None or lon is None:
            continue
        altitude = geo_altitude if geo_altitude is not None else baro_altitude
        aircraft.append(
            {
                "id": icao24,
                "callsign": callsign or icao24.upper(),
                "country": country,
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "altitude_ft": round(altitude * METERS_TO_FEET) if altitude is not None else None,
                "speed_kt": round(velocity * MS_TO_KNOTS) if velocity is not None else None,
                "heading": round(heading) if heading is not None else 0,
            }
        )
    return aircraft[:MAX_AIRCRAFT]


def _fetch():
    response = httpx.get(STATES_URL, params=AREA, timeout=15)
    response.raise_for_status()
    return _parse(response.json().get("states"))


def live_flights():
    """Return {"aircraft": [...], "updated": unix time, "stale": bool}."""
    cached = cache.get(CACHE_KEY)
    if cached and time.time() - cached["updated"] < FRESH_SECONDS:
        return {**cached, "stale": False}

    try:
        result = {"aircraft": _fetch(), "updated": int(time.time())}
    except Exception:
        logger.warning("OpenSky request failed", exc_info=True)
        if cached:
            return {**cached, "stale": True}
        return {"aircraft": [], "updated": None, "stale": True}

    cache.set(CACHE_KEY, result, STALE_SECONDS)
    return {**result, "stale": False}
