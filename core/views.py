from django.views.generic import TemplateView

from questions.context import get_sidebar_context


class SignUpPageView(TemplateView):
    template_name = "core/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_sidebar_context())
        return context


class LoginPageView(TemplateView):
    template_name = "core/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_sidebar_context())
        return context


class ProfilePageView(TemplateView):
    template_name = "core/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_sidebar_context())
        return context
