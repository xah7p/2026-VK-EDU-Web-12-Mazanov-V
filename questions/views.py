from typing import Any

from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import TemplateView

ANSWERS = [
    {
        'accepted': i == 0,
        'user_avatar': '/static/default_user_avatar.png',
        'user': f"user {i}",
        'text': f"Text {i}",
        'vote_count': 20 - i,
        'posting_time': f'{i} mins',
    }
    for i in range(30)
]

QUESTIONS = [
    {
        'id': i,
        'title': f"Title {i}",
        'text': f"Text {i}",
        'user': f"user{i}",
        'user_avatar': '/static/default_user_avatar.png',
        'tags': [f"tag{i}", f"tag{i + 1}"],
        'vote_count': 5,
        'viewed': i,
        'answers': ANSWERS,
        'answers_count': len(ANSWERS),
        'posting_time': '10 mins',
    }
    for i in range(30)
]


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

def paginate(objects_list, request, per_page=10):
    page_number = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.get_page(page_number)
    except PageNotAnInteger or EmptyPage:
        page = paginator.get_page(1)
    return page

class HomePageView(TemplateView):
    template_name = 'questions/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = paginate(QUESTIONS, self.request)
        context['page_obj'] = page
        context['questions'] = page.object_list
        context['best_members'] = BEST_MEMBERS
        context['popular_tags'] = POPULAR_TAGS
        return context

class HotPageView(TemplateView):
    template_name = 'questions/hot.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = paginate(QUESTIONS[::-1], self.request)
        context['page_obj'] = page
        context['questions'] = page.object_list
        context['best_members'] = BEST_MEMBERS
        context['popular_tags'] = POPULAR_TAGS
        return context

class TagPageView(TemplateView):
    template_name = 'questions/tag.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = paginate(QUESTIONS[1:11], self.request, 4)
        context['tag_name'] = kwargs['tag_name']
        context['page_obj'] = page
        context['questions'] = page.object_list
        context['best_members'] = BEST_MEMBERS
        context['popular_tags'] = POPULAR_TAGS
        return context
    
class AskPageView(TemplateView):
    template_name = 'questions/ask.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['best_members'] = BEST_MEMBERS
        context['popular_tags'] = POPULAR_TAGS
        return context

class QuestionPageView(TemplateView):
    template_name = 'questions/question.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = kwargs['question_id']
        try:
            question_id = int(question_id)
        except ValueError:
            question_id = 1
        context['question'] = QUESTIONS[question_id]
        context['best_members'] = BEST_MEMBERS
        context['popular_tags'] = POPULAR_TAGS
        return context
