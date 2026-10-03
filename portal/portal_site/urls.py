from django.urls import include, path

urlpatterns = [
    # POST /i18n/setlang/ switches the language (used by the menu in the top bar).
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("news.urls")),
    path("", include("ai.urls")),
    path("", include("games.urls")),
    path("", include("core.urls")),
]
