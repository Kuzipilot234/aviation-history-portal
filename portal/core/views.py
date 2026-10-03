from django.shortcuts import render

from .services.content import FEEDBACK_FORM_URL, MAP_POINTS


def feedback(request):
    return render(request, "core/feedback.html", {"form_url": FEEDBACK_FORM_URL})


def radars(request):
    return render(request, "core/radars.html", {"map_points": MAP_POINTS})
