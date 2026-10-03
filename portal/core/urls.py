from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("on-this-day/", views.on_this_day, name="on_this_day"),
    path("feedback/", views.feedback, name="feedback"),
    path("radars/", views.radars, name="radars"),
    path("radars/flights.json", views.live_flights, name="live_flights"),
]
