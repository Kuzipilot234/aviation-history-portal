from django.urls import include, path

urlpatterns = [
    path("", include("news.urls")),
    path("", include("ai.urls")),
    path("", include("games.urls")),
    path("", include("core.urls")),
]
