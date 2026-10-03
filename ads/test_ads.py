import pytest
from django.urls import reverse
from rest_framework import status
from ads.models import Ad, Review


# 1. ТЕСТЫ ДЛЯ АНОНИМНОГО ПОЛЬЗОВАТЕЛЯ (Разграничение прав по ТЗ)


@pytest.mark.django_db
def test_anonymous_can_get_ads_list(api_client, test_user):
    """Проверка ТЗ: Аноним может получать СПИСОК объявлений."""
    # Создаем тестовое объявление в базе данных
    Ad.objects.create(
        title="Тестовый товар", price=100, description="Описание", author=test_user
    )

    url = reverse("ads-list")  # Эндпоинт /api/ads/
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data  # Проверяем наличие структуры пагинации


@pytest.mark.django_db
def test_anonymous_cannot_get_single_ad(api_client, test_user):
    """Проверка ТЗ: Аноним НЕ может получать ОДНО объявление (оно закрыто IsAuthenticated)."""
    ad = Ad.objects.create(
        title="Секретный товар", price=500, description="Лог", author=test_user
    )

    url = reverse("ads-detail", kwargs={"pk": ad.pk})  # Эндпоинт /api/ads/<id>/
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_anonymous_cannot_create_ad(api_client):
    """Проверка ТЗ: Аноним НЕ может создавать объявления."""
    url = reverse("ads-list")
    data = {"title": "Новый товар", "price": 1000, "description": "Попытка взлома"}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 2. ТЕСТЫ ДЛЯ АВТОРИЗОВАННОГО ПОЛЬЗОВАТЕЛЯ (CRUD и Свои объекты)


@pytest.mark.django_db
def test_authenticated_user_can_create_ad(auth_client):
    """Проверка ТЗ: Авторизованный пользователь может успешно создать объявление."""
    url = reverse("ads-list")
    data = {"title": "Продам гитару", "price": 15000, "description": "Отличный Fender"}
    response = auth_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "Продам гитару"
    assert Ad.objects.count() == 1


@pytest.mark.django_db
def test_user_can_update_own_ad(auth_client, test_user):
    """Проверка ТЗ: Пользователь может редактировать СВОЕ объявление."""
    ad = Ad.objects.create(
        title="Старое имя", price=10, description="Текст", author=test_user
    )

    url = reverse("ads-detail", kwargs={"pk": ad.pk})
    data = {"title": "Новое имя", "price": 20, "description": "Текст"}
    response = auth_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    ad.refresh_from_db()
    assert ad.title == "Новое имя"


@pytest.mark.django_db
def test_user_cannot_update_foreign_ad(auth_client, django_user_model):
    """Проверка ТЗ: Пользователь НЕ может редактировать ЧУЖОЕ объявление."""
    another_user = django_user_model.objects.create_user(
        email="other@test.com",
        first_name="А",
        last_name="Б",
        phone="1",
        role="user",
        password="1",
    )
    foreign_ad = Ad.objects.create(
        title="Чужой товар", price=100, description="Текст", author=another_user
    )

    url = reverse("ads-detail", kwargs={"pk": foreign_ad.pk})
    data = {"title": "Пытаюсь изменить", "price": 50, "description": "Текст"}
    response = auth_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


# 3. ТЕСТЫ ДЛЯ АДМИНИСТРАТОРА (Максимальный доступ)


@pytest.mark.django_db
def test_admin_can_delete_foreign_ad(api_client, test_user, django_user_model):
    """Проверка ТЗ: Администратор может удалять объявления ЛЮБЫХ других пользователей."""
    # Создаем админа
    admin_user = django_user_model.objects.create_user(
        email="admin@test.com",
        first_name="Админ",
        last_name="Сайта",
        phone="2",
        role="admin",
        password="1",
    )
    # Авторизуем клиента как админа
    api_client.force_authenticate(user=admin_user)

    # Объявление создано обычным юзером
    user_ad = Ad.objects.create(
        title="Товар юзера", price=100, description="Текст", author=test_user
    )

    url = reverse("ads-detail", kwargs={"pk": user_ad.pk})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Ad.objects.count() == 0


# 4. ТЕСТЫ НА ПАГИНАЦИЮ И ПОИСК (Этап IV)


@pytest.mark.django_db
def test_ads_pagination_limit(api_client, test_user):
    """Проверка ТЗ: Пагинация отдает не более 4 объектов на страницу."""
    # Создаем 6 объявлений
    for i in range(6):
        Ad.objects.create(
            title=f"Товар {i}", price=10, description="Текст", author=test_user
        )

    url = reverse("ads-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 4  # Ровно 4 объекта по ТЗ!


@pytest.mark.django_db
def test_ads_search_by_title(api_client, test_user):
    """Проверка ТЗ: Реализован поиск товаров по названию."""
    Ad.objects.create(
        title="Искомый Смартфон", price=10, description="Текст", author=test_user
    )
    Ad.objects.create(
        title="Обычный Кирпич", price=10, description="Текст", author=test_user
    )

    url = reverse("ads-list")
    response = api_client.get(url, {"search": "Смартфон"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["title"] == "Искомый Смартфон"


@pytest.mark.django_db
def test_authenticated_user_can_create_review(auth_client, test_user):
    """Тестируем ads/views.py: создание отзыва."""
    ad = Ad.objects.create(
        title="Товар", price=10, description="Текст", author=test_user
    )

    # URL для создания отзыва: /api/ads/<ad_id>/reviews/
    url = reverse("ad-reviews", kwargs={"ad_id": ad.pk})
    data = {"text": "Отличный товар, рекомендую!"}
    response = auth_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Review.objects.count() == 1
    assert Review.objects.first().text == "Отличный товар, рекомендую!"


@pytest.mark.django_db
def test_get_reviews_only_for_specific_ad(auth_client, test_user):
    """Тестируем ads/views.py: фильтрация отзывов по ad_id."""
    ad_1 = Ad.objects.create(
        title="Товар 1", price=10, description="Текст", author=test_user
    )
    ad_2 = Ad.objects.create(
        title="Товар 2", price=10, description="Текст", author=test_user
    )

    # Создаем отзыв только для первого товара
    Review.objects.create(text="Отзыв к товару 1", author=test_user, ad=ad_1)

    # Запрашиваем список отзывов для ВТОРОГО товара
    url = reverse("ad-reviews", kwargs={"ad_id": ad_2.pk})
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    # Проверяем длину списка внутри ключа 'results'
    assert len(response.data["results"]) == 0
