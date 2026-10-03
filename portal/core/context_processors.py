from django.urls import reverse
from django.utils.translation import gettext_lazy as _

NAVIGATION = [
    ("news:news", _("News")),
    ("ai:chatbot", _("Chatbot")),
    ("ai:quiz", _("Quiz")),
    ("games:history", _("Games")),
    ("core:radars", _("Radars")),
    ("core:feedback", _("Feedback")),
]


def navigation(request):
    items = []
    for url_name, label in NAVIGATION:
        url = reverse(url_name)
        items.append({"url": url, "label": label, "active": request.path == url})
    return {
        "nav_items": items,
        # Read by the theme switch script in base.html.
        "theme_labels": {
            "toLight": _("Switch to light theme"),
            "toDark": _("Switch to dark theme"),
        },
    }
