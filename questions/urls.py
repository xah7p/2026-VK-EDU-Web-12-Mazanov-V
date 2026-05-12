from django.urls import path

from questions import views

app_name = "questions"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="index"),
    path("index", views.HomePageView.as_view(), name="index_alt"),
    path("ask/", views.AskPageView.as_view(), name="ask"),
    path("hot/", views.HotPageView.as_view(), name="hot"),
    path(
        "question/<int:question_id>/",
        views.QuestionPageView.as_view(),
        name="question",
    ),
    path("tag/<str:tag_name>/", views.TagPageView.as_view(), name="tag"),
]
