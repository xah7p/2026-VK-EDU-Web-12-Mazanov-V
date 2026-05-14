from django.apps import apps
from django.db import models
from django.db.models import Count, OuterRef, Prefetch, QuerySet, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from questions.pagination import paginate


def _question_votes_for_user(user, question_ids):
    if not user.is_authenticated or not question_ids:
        return {}
    QuestionLike = apps.get_model("questions", "QuestionLike")
    return dict(
        QuestionLike.objects.filter(
            user_id=user.id, question_id__in=question_ids
        ).values_list("question_id", "value")
    )


def _attach_question_votes(page_obj, user):
    if not hasattr(page_obj, "object_list"):
        return
    qids = [q.pk for q in page_obj.object_list]
    votes = _question_votes_for_user(user, qids)
    for q in page_obj.object_list:
        q.user_vote = votes.get(q.pk)


def _question_vote_count_annotation():
    QuestionLike = apps.get_model("questions", "QuestionLike")
    total = (
        QuestionLike.objects.filter(question_id=OuterRef("pk"))
        .values("question_id")
        .annotate(total=Sum("value"))
        .values("total")[:1]
    )
    return Coalesce(
        Subquery(total, output_field=models.IntegerField()),
        Value(0),
    )


def _answer_vote_count_annotation():
    AnswerLike = apps.get_model("questions", "AnswerLike")
    total = (
        AnswerLike.objects.filter(answer_id=OuterRef("pk"))
        .values("answer_id")
        .annotate(total=Sum("value"))
        .values("total")[:1]
    )
    return Coalesce(
        Subquery(total, output_field=models.IntegerField()),
        Value(0),
    )


class QuestionQuerySet(QuerySet):
    def for_list(self):
        QuestionTag = apps.get_model("questions", "QuestionTag")
        return (
            self.select_related("author", "author__profile")
            .prefetch_related(
                Prefetch(
                    "questiontag_set",
                    queryset=QuestionTag.objects.select_related("tag"),
                ),
            )
            .annotate(
                answers_count=Count("answers", distinct=True),
                vote_count=_question_vote_count_annotation(),
            )
        )

    def new(self):
        return self.for_list().order_by("-created_at", "-id")

    def best(self):
        return self.for_list().order_by("-vote_count", "-created_at", "-id")

    def by_tag(self, tag_name: str):
        return self.for_list().filter(
            questiontag__tag__name=tag_name,
        ).distinct()


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def new(self):
        return self.get_queryset().new()

    def best(self):
        return self.get_queryset().best()

    def by_tag(self, tag_name: str):
        return self.get_queryset().by_tag(tag_name)

    def for_detail(self):
        QuestionTag = apps.get_model("questions", "QuestionTag")
        return (
            self.get_queryset()
            .select_related("author", "author__profile")
            .prefetch_related(
                Prefetch(
                    "questiontag_set",
                    queryset=QuestionTag.objects.select_related("tag"),
                ),
            )
            .annotate(
                answers_count=Count("answers", distinct=True),
                vote_count=_question_vote_count_annotation(),
            )
        )

    def list_context_new(self, request, per_page=10):
        page = paginate(self.new(), request, per_page)
        _attach_question_votes(page, request.user)
        return {"page_obj": page, "questions": page.object_list}

    def list_context_best(self, request, per_page=10):
        page = paginate(self.best(), request, per_page)
        _attach_question_votes(page, request.user)
        return {"page_obj": page, "questions": page.object_list}

    def list_context_for_tag(self, request, tag_name, per_page=10):
        Tag = apps.get_model("questions", "Tag")
        get_object_or_404(Tag, name=tag_name)
        page = paginate(self.by_tag(tag_name), request, per_page)
        _attach_question_votes(page, request.user)
        return {
            "tag_name": tag_name,
            "page_obj": page,
            "questions": page.object_list,
        }

    def detail_context(self, request, question_id, per_page=10):
        Answer = apps.get_model("questions", "Answer")
        QuestionLike = apps.get_model("questions", "QuestionLike")
        AnswerLike = apps.get_model("questions", "AnswerLike")

        question = get_object_or_404(self.for_detail(), pk=question_id)
        page = paginate(
            Answer.objects.for_question(question_id),
            request,
            per_page,
        )
        answers = list(page.object_list)

        user_question_vote = None
        answer_votes = {}
        user_is_question_author = False

        if request.user.is_authenticated:
            user_is_question_author = question.author_id == request.user.id
            row = (
                QuestionLike.objects.filter(
                    user_id=request.user.id,
                    question_id=question_id,
                )
                .values_list("value", flat=True)
                .first()
            )
            if row is not None:
                user_question_vote = row
            if answers:
                a_ids = [a.pk for a in answers]
                for aid, val in AnswerLike.objects.filter(
                    user_id=request.user.id,
                    answer_id__in=a_ids,
                ).values_list("answer_id", "value"):
                    answer_votes[aid] = val

        return {
            "question": question,
            "page_obj": page,
            "answers": answers,
            "user_question_vote": user_question_vote,
            "answer_votes": answer_votes,
            "user_is_question_author": user_is_question_author,
        }


class QuestionLikeManager(models.Manager):
    def create_unique(self, user_id, question_id):
        props = {"user_id": user_id, "question_id": question_id}
        like = self.filter(**props).first()
        if like is not None:
            return like
        try:
            return self.create(**props, value=1)
        except IntegrityError:
            return self.filter(**props).first()

    def question_rating(self, question_id: int) -> int:
        Question = apps.get_model("questions", "Question")
        r = Question.objects.filter(pk=question_id).aggregate(
            rating=Coalesce(Sum("question_likes__value"), Value(0)),
        )["rating"]
        return int(r)

    def cast_vote(self, user_id: int, question_id: int, value: int):
        if value not in (1, -1):
            return False, None, "invalid", None
        props = {"user_id": user_id, "question_id": question_id}
        row = self.filter(**props).first()
        if row is None:
            try:
                self.create(user_id=user_id, question_id=question_id, value=value)
            except IntegrityError:
                row = self.filter(**props).first()
                if row is None:
                    return False, None, "invalid", None
                if row.value == value:
                    row.delete()
                    return True, self.question_rating(question_id), None, 0
                row.value = value
                row.save(update_fields=["value"])
            return True, self.question_rating(question_id), None, value
        if row.value == value:
            row.delete()
            return True, self.question_rating(question_id), None, 0
        row.value = value
        row.save(update_fields=["value"])
        return True, self.question_rating(question_id), None, value


class AnswerLikeManager(models.Manager):
    def create_unique(self, user_id, answer_id):
        props = {"user_id": user_id, "answer_id": answer_id}
        like = self.filter(**props).first()
        if like is not None:
            return like
        try:
            return self.create(**props, value=1)
        except IntegrityError:
            return self.filter(**props).first()

    def answer_rating(self, answer_id: int) -> int:
        Answer = apps.get_model("questions", "Answer")
        r = Answer.objects.filter(pk=answer_id).aggregate(
            rating=Coalesce(Sum("answer_likes__value"), Value(0)),
        )["rating"]
        return int(r)

    def cast_vote(self, user_id: int, answer_id: int, value: int):
        if value not in (1, -1):
            return False, None, "invalid", None
        props = {"user_id": user_id, "answer_id": answer_id}
        row = self.filter(**props).first()
        if row is None:
            try:
                self.create(user_id=user_id, answer_id=answer_id, value=value)
            except IntegrityError:
                row = self.filter(**props).first()
                if row is None:
                    return False, None, "invalid", None
                if row.value == value:
                    row.delete()
                    return True, self.answer_rating(answer_id), None, 0
                row.value = value
                row.save(update_fields=["value"])
            return True, self.answer_rating(answer_id), None, value
        if row.value == value:
            row.delete()
            return True, self.answer_rating(answer_id), None, 0
        row.value = value
        row.save(update_fields=["value"])
        return True, self.answer_rating(answer_id), None, value


class AnswerQuerySet(QuerySet):
    def for_question(self, question_id):
        return (
            self.filter(question_id=question_id)
            .select_related("author", "author__profile")
            .annotate(vote_count=_answer_vote_count_annotation())
            .order_by("-created_at", "-id")
        )


class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def for_question(self, question_id):
        return self.get_queryset().for_question(question_id)
