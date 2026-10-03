from django.urls import reverse

NAVIGATION = [
    ("news:home", "🏠", "Global News Feed"),
    ("ai:chatbot", "🤖", "AI Chatbot"),
    ("games:history", "📜", "History Mini Games"),
    ("ai:quiz", "🏆", "Quiz"),
    ("core:feedback", "💬", "Feedback"),
    ("core:radars", "✈️", "Aviation Radars"),
]


def navigation(request):
    items = []
    for url_name, icon, label in NAVIGATION:
        url = reverse(url_name)
        items.append(
            {"url": url, "icon": icon, "label": label, "active": request.path == url}
        )
    return {"nav_items": items}
