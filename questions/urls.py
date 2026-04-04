from django.urls import path

from questions import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('ask/', views.ask, name='ask'),
    path('question/', views.question, name='question'),
    path('hot/', views.hot, name='hot'),
]
