from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import FormView

from questions.context import get_sidebar_context

from .forms import LoginForm, ProfileEditForm, SignUpForm
from .models import Profile
from .utils import safe_redirect_url


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_sidebar_context())
        return context


class LoginPageView(SidebarMixin, DjangoLoginView):
    template_name = "core/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        next_candidate = self.request.POST.get("next") or self.request.GET.get("next")
        safe = safe_redirect_url(self.request, next_candidate)
        if safe:
            return safe
        return reverse_lazy("questions:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_candidate = self.request.POST.get("next") or self.request.GET.get("next")
        context["safe_next"] = safe_redirect_url(self.request, next_candidate) or ""
        return context


class SignUpPageView(SidebarMixin, FormView):
    template_name = "core/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("questions:index")

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


class ProfilePageView(SidebarMixin, FormView):
    template_name = "core/profile.html"
    form_class = ProfileEditForm
    success_url = reverse_lazy("core:profile")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_row"], _ = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={"nickname": ""},
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        self.request.user.refresh_from_db(fields=["username", "email"])
        return redirect(self.success_url)


@method_decorator(require_POST, name="dispatch")
class LogoutView(View):
    def post(self, request):
        next_raw = request.POST.get("next") or "/"
        safe = safe_redirect_url(request, next_raw)
        target = safe or reverse("questions:index")
        logout(request)
        return redirect(target)
