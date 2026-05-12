from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, TemplateView

from questions.context import get_sidebar_context
from questions.forms import AnswerForm, AskQuestionForm
from questions.models import Answer, Question


def _answer_page_number(question_id: int, answer_id: int, per_page: int = 10) -> int:
    ids = list(
        Answer.objects.for_question(question_id).values_list("pk", flat=True)
    )
    try:
        idx = ids.index(answer_id)
    except ValueError:
        return 1
    return idx // per_page + 1


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


class AskPageView(LoginRequiredMixin, SidebarMixin, FormView):
    template_name = "questions/ask.html"
    form_class = AskQuestionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        question = form.save()
        return redirect(question.get_absolute_url())


class QuestionPageView(SidebarMixin, TemplateView):
    template_name = "questions/question.html"

    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=kwargs["question_id"])
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        form = AnswerForm(request.user, question, request.POST)
        if form.is_valid():
            answer = form.save()
            page = _answer_page_number(question.pk, answer.pk)
            url = f"{question.get_absolute_url()}?page={page}#answer-{answer.pk}"
            return redirect(url)
        context = self.get_context_data(answer_form=form, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, answer_form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            Question.objects.detail_context(
                self.request,
                self.kwargs["question_id"],
            )
        )
        question = context["question"]
        if answer_form is not None:
            context["answer_form"] = answer_form
        elif self.request.user.is_authenticated:
            context["answer_form"] = AnswerForm(self.request.user, question)
        else:
            context["answer_form"] = None
        return context
