from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.core.paginator import Paginator

QUESTIONS = [
    {
        'id': 1,
        'title': f"Title {i}",
        'text': f"Text {i}",
        'user': f"user {i}",
        'user_avatar': '',
        'tags': [f"tag {i}", f"tag {i + 1}"],
        'vote_count': 5,
        'answers': 3,
    }
    for i in range(30)
]

# todo заменить на классы

def index(request):
    page_number = request.GET.get('page', 1)

    paginator = Paginator(QUESTIONS, 3)
    page_obj = paginator.get_page(page_number)

    return render(request, 'questions/index.html', context={
        'questions': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
    })

def hot(request):
    return render(request, 'questions/hot.html', context={'questions': QUESTIONS[::-1]})

def ask(request):
    return render(request, 'questions/ask.html')

def question(request):
    return render(request, 'questions/question.html')
