"""Fetching and cleaning the RSS news feeds."""

import html
import logging
from datetime import datetime

import feedparser
import nh3
from django.core.cache import cache

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "Aviation": "https://simpleflying.com/feed/",
    "History": "https://www.worldhistory.org/rss/",
}
ARTICLES_PER_FEED = 10
CACHE_KEY = "rss_articles"
CACHE_SECONDS = 15 * 60
PREVIEW_LENGTH = 150


def strip_html(text):
    """Turn an HTML snippet from a feed into plain text."""
    plain = html.unescape(nh3.clean(text or "", tags=set()))
    return " ".join(plain.split())


def make_preview(text, length=PREVIEW_LENGTH):
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "..."


def published_label(entry):
    """A short date like '3 Oct 2026, 09:23', or the feed's own text."""
    parsed = entry.get("published_parsed")
    if parsed:
        moment = datetime(*parsed[:6])
        return f"{moment.day} {moment:%b %Y, %H:%M}"
    return entry.get("published", "Unknown date")


def fetch_articles():
    """Download every feed. A feed that fails is skipped."""
    articles = []
    for category, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            logger.exception("Could not read the %s feed", category)
            continue
        for entry in feed.entries[:ARTICLES_PER_FEED]:
            summary = strip_html(entry.get("summary", "")) or "No summary available."
            articles.append(
                {
                    "category": category,
                    "title": strip_html(entry.get("title", "")) or "Untitled",
                    "summary": summary,
                    "preview": make_preview(summary),
                    "url": entry.get("link", ""),
                    "published": published_label(entry),
                }
            )
    return articles


def get_articles():
    """Return the articles, fetching them at most once every 15 minutes."""
    articles = cache.get(CACHE_KEY)
    if articles is None:
        articles = fetch_articles()
        # Keep an empty result only briefly, so a feed outage recovers quickly.
        cache.set(CACHE_KEY, articles, CACHE_SECONDS if articles else 60)
    return articles


def by_category(articles, category):
    return [article for article in articles if article["category"] == category]
