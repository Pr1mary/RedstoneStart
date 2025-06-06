
from django.urls import path
from .views import UserLoginView, UserLogoutView, UserRegisterView, UserInfoDetailsView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('auth/login', UserLoginView.as_view(), name="auth_login"),
    path('auth/register', UserRegisterView.as_view(), name="auth_register"),
    path('auth/logout', UserLogoutView.as_view(), name="auth_logout"),
    path('details', UserInfoDetailsView.as_view(), name="details_info"),
]
