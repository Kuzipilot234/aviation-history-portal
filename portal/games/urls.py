from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    path("history/", views.history, name="history"),
    path("history/timeline/<str:year>/", views.timeline, name="timeline"),
    path("history/guess/", views.guess, name="guess"),
    path("history/next/", views.next_figure, name="next_figure"),
]
