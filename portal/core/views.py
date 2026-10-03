import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from .services import flights, onthisday
from .services.content import ANNOUNCEMENT_TAGS, ANNOUNCEMENTS, FEEDBACK_FORM_URL, MAP_POINTS

logger = logging.getLogger(__name__)

NEW_ANNOUNCEMENT_DAYS = 14
HOME_ANNOUNCEMENTS = 3


def home(request):
    today = timezone.localdate()
    announcements = [
        {
            **item,
            "tag_label": ANNOUNCEMENT_TAGS[item["tag"]],
            "is_new": (today - item["date"]).days <= NEW_ANNOUNCEMENT_DAYS,
        }
        for item in sorted(ANNOUNCEMENTS, key=lambda item: item["date"], reverse=True)
    ]
    used_tags = {item["tag"] for item in announcements}
    return render(
        request,
        "core/home.html",
        {
            "today": today,
            "announcements": announcements[:HOME_ANNOUNCEMENTS],
            "older_announcements": announcements[HOME_ANNOUNCEMENTS:],
            "announcement_tags": [
                (key, label) for key, label in ANNOUNCEMENT_TAGS.items() if key in used_tags
            ],
        },
    )


def on_this_day(request):
    """Loaded by HTMX after the home page appears."""
    try:
        events = onthisday.todays_events(get_language())
    except Exception:
        logger.warning("On this day request failed", exc_info=True)
        events = None
    return render(
        request, "core/_on_this_day.html", {"events": events, "today": timezone.localdate()}
    )


def feedback(request):
    return render(request, "core/feedback.html", {"form_url": FEEDBACK_FORM_URL})


def radars(request):
    return render(
        request,
        "core/radars.html",
        {
            "map_points": MAP_POINTS,
            "flight_area_center": flights.CENTER,
            # Text the flight tracker script writes into the page.
            # {time} is filled in by the script.
            "flight_labels": {
                "aircraft": _("Aircraft"),
                "altitude": _("Altitude:"),
                "speed": _("Speed:"),
                "heading": _("Heading:"),
                "unknown": _("unknown"),
                "live": _("Live"),
                "paused": _("Paused"),
                "unavailable": _("Unavailable"),
                "liveNote": _("Updated {time}. Click a plane for details."),
                "pausedNote": _("Showing positions from {time}. Live data will resume shortly."),
                "unavailableNote": _("Live data is unavailable right now. Please try again later."),
            },
        },
    )


def live_flights(request):
    return JsonResponse(flights.live_flights())
