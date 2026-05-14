from django.db import models
from django.urls import reverse

from .managers import (
    AnswerLikeManager,
    AnswerManager,
    QuestionLikeManager,
    QuestionManager,
)

class Tag(models.Model):
    name = models.CharField(verbose_name="Название", max_length=32, unique=True)
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    
    def __str__(self):
        return self.name


class Question(models.Model):
    objects = QuestionManager()

    title = models.CharField(verbose_name="Заголовок", max_length=255)
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)

    author = models.ForeignKey(
        "auth.User",
        verbose_name="Автор",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
    )
    correct_answer = models.ForeignKey(
        "questions.Answer",
        verbose_name="Правильный ответ",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_correct_for_questions",
    )

    class Meta: 
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
    
    def __str__(self):
        return f"Вопрос #{self.id}: {self.title}"

    def get_absolute_url(self):
        return reverse("questions:question", kwargs={"question_id": self.pk})


class Answer(models.Model):
    objects = AnswerManager()

    question = models.ForeignKey(
        "questions.Question",
        verbose_name="Вопрос",
        on_delete=models.CASCADE,
        related_name="answers",
    )
    author = models.ForeignKey(
        "auth.User",
        verbose_name="Автор",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="answers",
    )
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f"Ответ #{self.id} на вопрос #{self.question_id}"


class QuestionTag(models.Model):
    question = models.ForeignKey(
        "questions.Question",
        verbose_name="Вопрос",
        on_delete=models.CASCADE,
    )
    
    tag = models.ForeignKey(
        "questions.Tag",
        verbose_name="Тег",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = [["question", "tag"]]
        verbose_name = "Тег вопроса"
        verbose_name_plural = "Теги вопросов"

    def __str__(self):
        return f"Вопрос #{self.question_id} — тег #{self.tag_id}"


class QuestionLike(models.Model):
    objects = QuestionLikeManager()

    user = models.ForeignKey(
        "auth.User",
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="given_question_likes",
    )
    question = models.ForeignKey(
        "questions.Question",
        verbose_name="Вопрос",
        on_delete=models.CASCADE,
        related_name="question_likes",
    )
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    value = models.SmallIntegerField(
        verbose_name="Значение голоса",
        default=1,
        choices=[(1, "Лайк"), (-1, "Дизлайк")],
    )

    class Meta:
        unique_together = [["user", "question"]]
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"

    def __str__(self):
        return f"Лайк вопроса #{self.question_id} от пользователя #{self.user_id}"


class AnswerLike(models.Model):
    objects = AnswerLikeManager()

    user = models.ForeignKey(
        "auth.User",
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="answer_likes",
    )
    answer = models.ForeignKey(
        "questions.Answer",
        verbose_name="Ответ",
        on_delete=models.CASCADE,
        related_name="answer_likes",
    )
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    value = models.SmallIntegerField(
        verbose_name="Значение голоса",
        default=1,
        choices=[(1, "Лайк"), (-1, "Дизлайк")],
    )

    class Meta:
        unique_together = [["user", "answer"]]
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"

    def __str__(self):
        return f"Лайк ответа #{self.answer_id} от пользователя #{self.user_id}"