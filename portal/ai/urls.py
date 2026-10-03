from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("chatbot/", views.chatbot, name="chatbot"),
    path("chatbot/ask/", views.chatbot_ask, name="chatbot_ask"),
    path("quiz/", views.quiz, name="quiz"),
    path("quiz/generate/", views.quiz_generate, name="quiz_generate"),
    path("quiz/check/", views.quiz_check, name="quiz_check"),
]
