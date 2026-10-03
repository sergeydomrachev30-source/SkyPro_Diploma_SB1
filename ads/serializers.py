from rest_framework import serializers
from ads.models import Ad, Review


class AdSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Объявления (Ad).

    Переводит объекты объявлений из базы данных PostgreSQL в формат JSON
    для передачи на фронтенд и валидирует входящие JSON-данные при создании постов.
    """

    # Вместо ID автора выводим его электронную почту
    author = serializers.ReadOnlyField(source="author.email")

    class Meta:
        model = Ad
        # Список полей, которые будут доступны в JSON
        fields = ["id", "title", "price", "description", "author", "created_at"]


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Отзыва (Review).

    Используется для перевода отзывов в JSON и автоматической подстановки
    человекочитаемых данных автора и объявления.
    """

    # Вместо ID автора выводим его электронную почту
    author = serializers.ReadOnlyField(source="author.email")

    # Делаем поле объявления только для чтения, чтобы не ломать создание
    ad = serializers.ReadOnlyField(source="ad.id")

    class Meta:
        model = Review
        # Список полей отзыва, передаваемых на фронтенд
        fields = ["id", "text", "ad", "author", "created_at"]
