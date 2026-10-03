import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для анонимного клиента API"""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Фикстура для создания обычного пользователя"""
    return User.objects.create_user(
        email="user@test.com",
        first_name="Иван",
        last_name="Тестовый",
        phone="+79991112233",
        role="user",
        password="test_password123"
    )


@pytest.fixture
def auth_client(test_user):
    """Фикстура для авторизованного пользователя (имитация JWT-авторизации)"""

    client = APIClient()
    client.force_authenticate(user=test_user)
    return client
