import logging

from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from core.services import ai
from core.services import news as news_service

logger = logging.getLogger(__name__)

# Filter values stay in English (they appear in shareable URLs); labels are translated.
CATEGORIES = {"All": _("All"), "Aviation": _("Aviation"), "History": _("History")}
SEARCH_MAX_CHARS = 80
TRANSLATION_CACHE_SECONDS = 24 * 60 * 60


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
    return {
        "articles": articles,
        "category": category,
        "category_label": CATEGORIES[category],
        "query": query,
    }


def news(request):
    context = _filtered(request)
    context["categories"] = list(CATEGORIES.items())
    return render(request, "news/news.html", context)


def results(request):
    """The article list alone, swapped in by HTMX as the filters change."""
    return render(request, "news/_results.html", _filtered(request))


def briefing(request):
    """Loaded when a visitor asks for the AI summary on the News page."""
    try:
        text = ai.daily_briefing(news_service.get_articles(), get_language())
    except Exception:
        logger.exception("Daily briefing failed")
        text = None
    return render(request, "news/_briefing.html", {"briefing": text})


@require_POST
def translate(request, article_id):
    """Translate one article into the visitor's language with the AI.

    Translations are cached per article and language, so each one is only
    paid for once.
    """
    article = news_service.find_article(article_id)
    language = get_language()
    if article is None or language not in ai.LANGUAGE_NAMES or language == "en":
        raise Http404("Article not found")

    key = f"translation:{language}:{article_id}"
    translation = cache.get(key)
    if translation is None:
        try:
            translation = ai.translate_article(article["title"], article["summary"], language)
        except Exception:
            logger.exception("Article translation failed")
            return render(request, "news/_translation.html", {"article": article, "failed": True})
        cache.set(key, translation, TRANSLATION_CACHE_SECONDS)
    return render(
        request, "news/_translation.html", {"article": article, "translation": translation}
    )
