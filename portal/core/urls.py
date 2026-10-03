from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("feedback/", views.feedback, name="feedback"),
    path("radars/", views.radars, name="radars"),
]
