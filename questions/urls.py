from django.urls import path

from questions import api_views, views

app_name = "questions"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="index"),
    path("index", views.HomePageView.as_view(), name="index_alt"),
    path("ask/", views.AskPageView.as_view(), name="ask"),
    path("hot/", views.HotPageView.as_view(), name="hot"),
    path(
        "api/question/<int:question_id>/vote/",
        api_views.QuestionVoteView.as_view(),
        name="question_vote",
    ),
    path(
        "api/answer/<int:answer_id>/vote/",
        api_views.AnswerVoteView.as_view(),
        name="answer_vote",
    ),
    path(
        "api/question/<int:question_id>/correct/",
        api_views.MarkCorrectAnswerView.as_view(),
        name="mark_correct",
    ),
    path(
        "api/question/<int:question_id>/answer/<int:answer_id>/fragment/",
        api_views.AnswerFragmentView.as_view(),
        name="answer_fragment",
    ),
    path(
        "question/<int:question_id>/",
        views.QuestionPageView.as_view(),
        name="question",
    ),
    path("tag/<str:tag_name>/", views.TagPageView.as_view(), name="tag"),
]
