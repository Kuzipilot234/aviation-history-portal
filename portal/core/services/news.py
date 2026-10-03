"""Fetching and cleaning the RSS news feeds."""

import hashlib
import html
import logging
from datetime import datetime, timezone

import feedparser
import nh3
from django.core.cache import cache

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "Aviation": "https://simpleflying.com/feed/",
    "History": "https://www.worldhistory.org/rss/",
}
ARTICLES_PER_FEED = 10
CACHE_KEY = "rss_articles:v2"
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


def published_at(entry):
    """The publish time as an aware UTC datetime, or None if the feed has none.

    Templates format it with the date filter, so it shows in the visitor's
    language and the site's time zone.
    """
    parsed = entry.get("published_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc)
    return None


def article_id(url, title):
    """A short stable ID, used to find an article again (e.g. to translate it)."""
    return hashlib.sha1((url or title).encode("utf-8")).hexdigest()[:12]


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
            summary = strip_html(entry.get("summary", ""))
            title = strip_html(entry.get("title", ""))
            url = entry.get("link", "")
            articles.append(
                {
                    "id": article_id(url, title),
                    "category": category,
                    "title": title,
                    "summary": summary,
                    "preview": make_preview(summary),
                    "url": url,
                    "published_at": published_at(entry),
                    "published": entry.get("published", ""),
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


def find_article(identifier):
    return next((a for a in get_articles() if a["id"] == identifier), None)
