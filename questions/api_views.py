from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
import re

from questions.forms import AnswerVoteForm, MarkCorrectAnswerForm, QuestionVoteForm
from questions.models import Answer, AnswerLike, Question, QuestionLike


def json_error(message: str, code: str, status: int = 400):
    return JsonResponse({"ok": False, "error": message, "code": code}, status=status)


def form_errors_json(form):
    errors = form.errors.get_json_data()
    flat = []
    for _field, errs in errors.items():
        for e in errs:
            flat.append(e.get("message", str(e)))
    msg = "; ".join(flat) if flat else "Неверные данные."
    return json_error(msg, "validation_error", 400)


class JsonPostApiView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return json_error("Требуется POST.", "method_not_allowed", 405)
        return super().dispatch(request, *args, **kwargs)


class QuestionVoteView(JsonPostApiView):
    def post(self, request, question_id: int):
        if not request.user.is_authenticated:
            return json_error("Требуется вход.", "auth_required", 401)

        form = QuestionVoteForm(
            {
                "question_id": question_id,
                "vote_type": request.POST.get("vote_type"),
            }
        )
        if not form.is_valid():
            return form_errors_json(form)

        value = form.vote_value()
        with transaction.atomic():
            ok, rating, err, your_vote = QuestionLike.objects.cast_vote(
                request.user.id, question_id, value
            )
        if err == "invalid" or not ok or rating is None:
            return json_error("Не удалось обработать голос.", "invalid", 400)

        return JsonResponse(
            {
                "ok": True,
                "rating": rating,
                "your_vote": your_vote,
            }
        )


class AnswerVoteView(JsonPostApiView):
    def post(self, request, answer_id: int):
        if not request.user.is_authenticated:
            return json_error("Требуется вход.", "auth_required", 401)

        form = AnswerVoteForm(
            {
                "answer_id": answer_id,
                "vote_type": request.POST.get("vote_type"),
            }
        )
        if not form.is_valid():
            return form_errors_json(form)

        value = form.vote_value()
        with transaction.atomic():
            ok, rating, err, your_vote = AnswerLike.objects.cast_vote(
                request.user.id, answer_id, value
            )
        if err == "invalid" or not ok or rating is None:
            return json_error("Не удалось обработать голос.", "invalid", 400)

        return JsonResponse(
            {
                "ok": True,
                "rating": rating,
                "your_vote": your_vote,
            }
        )


class AnswerFragmentView(View):
    def get(self, request, question_id: int, answer_id: int):
        question = get_object_or_404(Question, pk=question_id)
        answer = get_object_or_404(
            Answer.objects.for_question(question_id),
            pk=answer_id,
        )

        answer_votes = {}
        user_is_question_author = False
        if request.user.is_authenticated:
            user_is_question_author = question.author_id == request.user.id
            vote = (
                AnswerLike.objects.filter(
                    user_id=request.user.id,
                    answer_id=answer_id,
                )
                .values_list("value", flat=True)
                .first()
            )
            if vote is not None:
                answer_votes[answer_id] = vote

        html = render_to_string(
            "questions/partials/answer.html",
            {
                "question": question,
                "answer": answer,
                "answer_votes": answer_votes,
                "user_is_question_author": user_is_question_author,
            },
            request=request,
        )
        return HttpResponse(html)


class MarkCorrectAnswerView(JsonPostApiView):
    def post(self, request, question_id: int):
        if not request.user.is_authenticated:
            return json_error("Требуется вход.", "auth_required", 401)

        question = get_object_or_404(Question, pk=question_id)
        if question.author_id != request.user.id:
            return json_error(
                "Только автор вопроса может отметить правильный ответ.",
                "forbidden",
                403,
            )

        form = MarkCorrectAnswerForm(
            {
                "question_id": question_id,
                "answer_id": request.POST.get("answer_id"),
            }
        )
        if not form.is_valid():
            return form_errors_json(form)

        answer = form.answer
        question.correct_answer = answer
        question.save(update_fields=["correct_answer"])

        return JsonResponse(
            {
                "ok": True,
                "correct_answer_id": answer.pk,
            }
        )

class QuestionSearchSuggestView(View):
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        if len(q) < 2:
            return JsonResponse({"ok": True, "items": []})

        terms = [t for t in re.split(r"\s+", q.lower()) if t]
        if not terms:
            return JsonResponse({"ok": True, "items": []})
        raw_query = " & ".join(f"{term}:*" for term in terms)

        vector = SearchVector("title", weight="A", config="simple") + SearchVector("text", weight="B", config="simple")
        query = SearchQuery(raw_query, search_type="raw", config="simple")

        qs = (
            Question.objects.annotate(rank=SearchRank(vector, query))
            .filter(rank__gt=0)
            .order_by("-rank", "-created_at")[:7]
        )

        items = [
            {"id": obj.id, "title": obj.title, "url": obj.get_absolute_url()}
            for obj in qs
        ]
        return JsonResponse({"ok": True, "items": items})