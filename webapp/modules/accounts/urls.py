
from django.urls import path
from .views import UserLoginView, UserLogoutView, UserRegisterView, UserInfoDetailsView
from django.contrib.auth.views import (
    LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

urlpatterns = [
    path('auth/login', UserLoginView.as_view(), name="auth_login"),
    path('auth/register', UserRegisterView.as_view(), name="auth_register"),
    path(
      'auth/reset',
      PasswordResetView.as_view(template_name="modules/accounts/templates/index-reset.html"),
      name="password_reset"),
    path(
      'auth/reset/done',
      PasswordResetDoneView.as_view(template_name="modules/accounts/templates/index-reset-requested.html"),
      name="password_reset_done"
      ),
    path(
      'auth/reset/confirm/<uidb64>/<token>',
      PasswordResetConfirmView.as_view(template_name="modules/accounts/templates/index-reset-confirm.html"),
      name="password_reset_confirm"
      ),
    path(
      'auth/reset/complete',
      PasswordResetCompleteView.as_view(template_name="modules/accounts/templates/index-reset-done.html"),
      name="password_reset_complete"
      ),
    path('auth/logout', UserLogoutView.as_view(), name="auth_logout"),
    path('details', UserInfoDetailsView.as_view(), name="details_info"),
]
