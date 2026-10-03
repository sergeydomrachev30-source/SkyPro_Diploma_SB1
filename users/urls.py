from django.urls import path
from .views import (
    UserRegistrationView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    # Регистрация пользователей
    path("users/", UserRegistrationView.as_view(), name="user-registration"),
    # Запрос сброса пароля
    path(
        "users/reset_password/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    # Подтверждение сброса пароля
    path(
        "users/reset_password_confirm",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
