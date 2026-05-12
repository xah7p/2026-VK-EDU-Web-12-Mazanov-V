from django.urls import path

from core import views

app_name = 'core'

urlpatterns = [
    path('signup/', views.SignUpPageView.as_view(), name='signup'),
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.ProfilePageView.as_view(), name='profile'),
]
