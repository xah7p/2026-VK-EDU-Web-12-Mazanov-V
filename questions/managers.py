from django.apps import apps
from django.db import models
from django.db.models import Count, Prefetch, QuerySet
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from questions.pagination import paginate


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
                vote_count=Count("question_likes", distinct=True),
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
                vote_count=Count("question_likes", distinct=True),
            )
        )

    def list_context_new(self, request, per_page=10):
        page = paginate(self.new(), request, per_page)
        return {"page_obj": page, "questions": page.object_list}

    def list_context_best(self, request, per_page=10):
        page = paginate(self.best(), request, per_page)
        return {"page_obj": page, "questions": page.object_list}

    def list_context_for_tag(self, request, tag_name, per_page=10):
        Tag = apps.get_model("questions", "Tag")
        get_object_or_404(Tag, name=tag_name)
        page = paginate(self.by_tag(tag_name), request, per_page)
        return {
            "tag_name": tag_name,
            "page_obj": page,
            "questions": page.object_list,
        }

    def detail_context(self, request, question_id, per_page=10):
        Answer = apps.get_model("questions", "Answer")
        question = get_object_or_404(self.for_detail(), pk=question_id)
        page = paginate(
            Answer.objects.for_question(question_id),
            request,
            per_page,
        )
        return {
            "question": question,
            "page_obj": page,
            "answers": page.object_list,
        }


class QuestionLikeManager(models.Manager):
    def create_unique(self, user_id, question_id):
        props = {"user_id": user_id, "question_id": question_id}
        like = self.filter(**props).first()
        if like is not None:
            return like
        try:
            return self.create(**props)
        except IntegrityError:
            return self.filter(**props).first()


class AnswerLikeManager(models.Manager):
    def create_unique(self, user_id, answer_id):
        props = {"user_id": user_id, "answer_id": answer_id}
        like = self.filter(**props).first()
        if like is not None:
            return like
        try:
            return self.create(**props)
        except IntegrityError:
            return self.filter(**props).first()


class AnswerQuerySet(QuerySet):
    def for_question(self, question_id):
        return (
            self.filter(question_id=question_id)
            .select_related("author", "author__profile")
            .annotate(vote_count=Count("answer_likes", distinct=True))
            .order_by("-created_at", "-id")
        )


class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def for_question(self, question_id):
        return self.get_queryset().for_question(question_id)