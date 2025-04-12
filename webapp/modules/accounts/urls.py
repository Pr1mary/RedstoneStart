
from django.urls import path
from .views import UserLoginView, UserLogoutView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('auth/login', UserLoginView.as_view(), name="auth_login"),
    path('auth/logout', UserLogoutView.as_view(), name="auth_logout"),
]
