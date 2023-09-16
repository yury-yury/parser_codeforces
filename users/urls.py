from django.contrib import admin
from django.urls import path, include

from users.views import UserCreateView, LoginView, ProfileView, UpdatePasswordView

urlpatterns = [
    path('signup', UserCreateView.as_view()),
    path('login', LoginView.as_view()),
    path('profile', ProfileView.as_view()),
    path('update_password', UpdatePasswordView.as_view()),
]
