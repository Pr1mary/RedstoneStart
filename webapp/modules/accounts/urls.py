
from django.urls import path
from .views import UserLoginView, UserLogoutView, UserRegisterView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('auth/login', UserLoginView.as_view(), name="auth_login"),
    path('auth/register', UserRegisterView.as_view(), name="auth_register"),
    path('auth/logout', UserLogoutView.as_view(), name="auth_logout"),
]
