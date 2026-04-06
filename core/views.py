from typing import Any

from django.shortcuts import render
from django.views.generic import TemplateView

BEST_MEMBERS = [
    {
        'name': f'user{i}',
        'avatar': '/static/default_user_avatar.png'
    }
    for i in range(4)
]

POPULAR_TAGS = [
    f'tag{i}'
    for i in range(5)
]

class SignUpPageView(TemplateView):
    template_name = 'core/signup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['best_members'] = BEST_MEMBERS
        context['popular_tags'] = POPULAR_TAGS
        return context

class LoginPageView(TemplateView):
    template_name = 'core/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['best_members'] = BEST_MEMBERS
        context['popular_tags'] = POPULAR_TAGS
        return context
    
class ProfilePageView(TemplateView):
    template_name = 'core/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['best_members'] = BEST_MEMBERS
        context['popular_tags'] = POPULAR_TAGS
        return context
