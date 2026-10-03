import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .services import flights, onthisday
from .services.content import ANNOUNCEMENTS, FEEDBACK_FORM_URL, MAP_POINTS

logger = logging.getLogger(__name__)

NEW_ANNOUNCEMENT_DAYS = 14
HOME_ANNOUNCEMENTS = 3
ANNOUNCEMENT_TAGS = ["New feature", "Update", "Fix"]


def home(request):
    today = timezone.localdate()
    announcements = [
        {**item, "is_new": (today - item["date"]).days <= NEW_ANNOUNCEMENT_DAYS}
        for item in sorted(ANNOUNCEMENTS, key=lambda item: item["date"], reverse=True)
    ]
    return render(
        request,
        "core/home.html",
        {
            "today": today,
            "announcements": announcements[:HOME_ANNOUNCEMENTS],
            "older_announcements": announcements[HOME_ANNOUNCEMENTS:],
            "announcement_tags": [
                tag for tag in ANNOUNCEMENT_TAGS if any(a["tag"] == tag for a in announcements)
            ],
        },
    )


def on_this_day(request):
    """Loaded by HTMX after the home page appears."""
    try:
        events = onthisday.todays_events()
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
        {"map_points": MAP_POINTS, "flight_area_center": flights.CENTER},
    )


def live_flights(request):
    return JsonResponse(flights.live_flights())
