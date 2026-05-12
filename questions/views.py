from django.views.generic import TemplateView

from questions.context import get_sidebar_context
from questions.models import Question


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_sidebar_context())
        return context


class HomePageView(SidebarMixin, TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(Question.objects.list_context_new(self.request))
        return context


class HotPageView(SidebarMixin, TemplateView):
    template_name = "questions/hot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(Question.objects.list_context_best(self.request))
        return context


class TagPageView(SidebarMixin, TemplateView):
    template_name = "questions/tag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            Question.objects.list_context_for_tag(
                self.request,
                self.kwargs["tag_name"],
            )
        )
        return context


class AskPageView(SidebarMixin, TemplateView):
    template_name = "questions/ask.html"


class QuestionPageView(SidebarMixin, TemplateView):
    template_name = "questions/question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            Question.objects.detail_context(
                self.request,
                self.kwargs["question_id"],
            )
        )
        return context
