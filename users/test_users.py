import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


# 1. ТЕСТЫ МОДЕЛИ И МЕНЕДЖЕРА ПОЛЬЗОВАТЕЛЕЙ (users/models.py)

@pytest.mark.django_db
def test_create_superuser_success():
    """Тестируем метод create_superuser в users/models.py"""
    admin = User.objects.create_superuser(
        email="superadmin@test.com",
        first_name="Главный",
        last_name="Админ",
        phone="+71112223344",
        password="SuperPassword123",
    )
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.role == "admin"


# 2. ТЕСТЫ РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЕЙ (users/views.py)


@pytest.mark.django_db
def test_user_registration_success(api_client):
    """Тестируем успешную регистрацию нового пользователя."""
    url = reverse("user-registration")
    data = {
        "email": "new_user@example.com",
        "first_name": "Сергей",
        "last_name": "Иванов",
        "phone": "+79998887766",
        "password": "SuperSecurePassword2026",
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email="new_user@example.com").exists()


@pytest.mark.django_db
def test_user_registration_missing_fields(api_client):
    """Тестируем ошибку валидации при регистрации (пропуск обязательного поля)."""
    url = reverse("user-registration")
    data = {"email": "bad_user@example.com", "last_name": "Иванов", "password": "123"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# 3. ТЕСТЫ СБРОСА ПАРОЛЯ (users/views.py)


@pytest.mark.django_db
def test_password_reset_request_success(api_client, test_user, capsys):
    """Тестируем успешную отправку запроса на сброс пароля (покрываем строки 47-59)."""
    url = reverse("password-reset-request")
    data = {"email": test_user.email}

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK

    # Перехватываем строку, которую принт вывел в консоль контейнера
    captured = capsys.readouterr()
    assert "ССЫЛКА ДЛЯ СБРОСА ПАРОЛЯ" in captured.out
    assert test_user.email in captured.out


@pytest.mark.django_db
def test_password_reset_request_email_not_found(api_client):
    """Тестируем запрос сброса пароля для несуществующего в базе email."""
    url = reverse("password-reset-request")
    data = {"email": "non_existent_email@mail.com"}

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_password_reset_confirm_success(api_client, test_user):
    """Тестируем успешное подтверждение смены пароля с валидным токеном и uid (строки 142-177)."""
    # Генерируем реальный валидный uid и токен для нашего тестового юзера
    uid = urlsafe_base64_encode(force_bytes(test_user.pk))
    token = default_token_generator.make_token(test_user)

    url = reverse("password-reset-confirm")
    data = {"uid": uid, "token": token, "new_password": "BrandNewPassword2026"}
    response = api_client.post(url, data)

    # Главное — бэкенд одобрил операцию
    assert response.status_code == status.HTTP_200_OK

    # проверяем, что в базе данных у пользователя реально обновился хэш пароля
    test_user.refresh_from_db()
    assert test_user.check_password("BrandNewPassword2026") is True


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(api_client):
    """Тестируем отправку POST-запроса на подтверждение смены пароля с неверным токеном."""
    url = reverse("password-reset-confirm")
    data = {
        "uid": "invalid-uid",
        "token": "invalid-token",
        "new_password": "NewSecurePassword777",
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
