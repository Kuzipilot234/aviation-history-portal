import logging

from django.shortcuts import render

from core.services import ai
from core.services import news as news_service

logger = logging.getLogger(__name__)

CATEGORIES = ["All", "Aviation", "History"]
SEARCH_MAX_CHARS = 80


def _filtered(request):
    """Articles matching the ?category= and ?q= filters."""
    category = request.GET.get("category", "All")
    if category not in CATEGORIES:
        category = "All"
    query = request.GET.get("q", "").strip()[:SEARCH_MAX_CHARS]

    articles = news_service.get_articles()
    if category != "All":
        articles = news_service.by_category(articles, category)
    if query:
        needle = query.lower()
        articles = [
            article
            for article in articles
            if needle in article["title"].lower() or needle in article["summary"].lower()
        ]
    return {"articles": articles, "category": category, "query": query}


def news(request):
    context = _filtered(request)
    context["categories"] = CATEGORIES
    return render(request, "news/news.html", context)


def results(request):
    """The article list alone, swapped in by HTMX as the filters change."""
    return render(request, "news/_results.html", _filtered(request))


def briefing(request):
    """Loaded when a visitor asks for the AI summary on the News page."""
    try:
        text = ai.daily_briefing(news_service.get_articles())
    except Exception:
        logger.exception("Daily briefing failed")
        text = None
    return render(request, "news/_briefing.html", {"briefing": text})
