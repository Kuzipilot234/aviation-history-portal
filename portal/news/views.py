import logging
import random

from django.shortcuts import render
from django.utils import timezone

from core.services import ai, news
from core.services.content import ANNOUNCEMENTS, QUOTES

logger = logging.getLogger(__name__)


def home(request):
    articles = news.get_articles()
    return render(
        request,
        "news/home.html",
        {
            "today": timezone.localdate(),
            "quote": random.choice(QUOTES),
            "announcements": ANNOUNCEMENTS,
            "aviation_articles": news.by_category(articles, "Aviation"),
            "history_articles": news.by_category(articles, "History"),
        },
    )


def briefing(request):
    """Loaded by HTMX after the home page appears, so a slow AI call can't delay it."""
    try:
        text = ai.daily_briefing(news.get_articles())
    except Exception:
        logger.exception("Daily briefing failed")
        text = None
    return render(request, "news/_briefing.html", {"briefing": text})
