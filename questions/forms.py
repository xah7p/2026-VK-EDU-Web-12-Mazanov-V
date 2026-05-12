import re

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Answer, Question, QuestionTag, Tag


class AskQuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label="Теги",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "questionTags",
                "placeholder": "e.g. boss-guides hardmode weapons",
            }
        ),
    )

    class Meta:
        model = Question
        fields = ("title", "text")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "questionTitle",
                    "placeholder": "e.g. Is Hytale a killer of Terraria?",
                    "minlength": "15",
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "id": "questionBody",
                    "rows": 10,
                    "placeholder": "Write your question details here...",
                    "style": "resize: vertical;",
                }
            ),
        }

    def __init__(self, user, *args, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 15:
            raise ValidationError(
                "Title cannot be empty and must be at least 15 characters long."
            )
        return title

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise ValidationError("Body cannot be empty.")
        if len(text) > 10000:
            raise ValidationError("Maximum length is 10,000 characters.")
        return text

    def clean_tags(self):
        raw = self.cleaned_data.get("tags") or ""
        parts = [t for t in re.split(r"\s+", raw.strip()) if t]
        if len(parts) > 3:
            raise ValidationError(
                "Add up to 3 tags, separated by spaces."
            )
        for name in parts:
            if len(name) > 32:
                raise ValidationError(
                    f"Tag «{name[:16]}…» is too long (max 32 characters)."
                )
        self._parsed_tags = parts
        return raw

    @transaction.atomic
    def save(self, commit=True):
        question = super().save(commit=False)
        question.author = self._user
        question.save()
        QuestionTag.objects.filter(question=question).delete()
        for name in getattr(self, "_parsed_tags", []):
            tag, _ = Tag.objects.get_or_create(name=name)
            QuestionTag.objects.get_or_create(question=question, tag=tag)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Write your answer here...",
                    "style": "resize: vertical;",
                    "maxlength": "10000",
                }
            )
        }

    def __init__(self, user, question, *args, **kwargs):
        self._user = user
        self._question = question
        super().__init__(*args, **kwargs)

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise ValidationError("Answer text cannot be empty.")
        if len(text) > 10000:
            raise ValidationError("Maximum length is 10,000 characters.")
        return text

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self._user
        answer.question = self._question
        if commit:
            answer.save()
        return answer
