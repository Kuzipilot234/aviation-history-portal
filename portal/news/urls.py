from django.urls import path

from . import views

app_name = "news"

urlpatterns = [
    path("news/", views.news, name="news"),
    path("news/results/", views.results, name="results"),
    path("news/briefing/", views.briefing, name="briefing"),
    path("news/<str:article_id>/translate/", views.translate, name="translate"),
]
