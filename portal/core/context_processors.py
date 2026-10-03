from django.urls import reverse

NAVIGATION = [
    ("news:news", "News"),
    ("ai:chatbot", "Chatbot"),
    ("ai:quiz", "Quiz"),
    ("games:history", "Games"),
    ("core:radars", "Radars"),
    ("core:feedback", "Feedback"),
]


def navigation(request):
    items = []
    for url_name, label in NAVIGATION:
        url = reverse(url_name)
        items.append({"url": url, "label": label, "active": request.path == url})
    return {"nav_items": items}
