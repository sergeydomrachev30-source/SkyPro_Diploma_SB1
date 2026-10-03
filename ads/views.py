from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from ads.models import Ad, Review
from ads.serializers import AdSerializer, ReviewSerializer

from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from ads.permissions import IsOwnerOrAdmin


class AdPagination(PageNumberPagination):
    """
    Этот класс делит список объявлений на страницы
    и показывает ровно по 4 штуки на каждой.
    """

    page_size = 4


class AdViewSet(viewsets.ModelViewSet):
    """
    Контроллер (ViewSet) для обработки всех CRUD-операций с объявлениями.
    Автоматически генерирует эндпоинты для списка, создания, удаления и редактирования.
    """

    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    pagination_class = AdPagination

    # Подключаем бэкенды фильтрации и указываем поле для поиска
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title"]

    def get_permissions(self):
        """Управление правами доступа"""
        if self.action == "list":
            # Список объявлений доступен всем (включая анонимов)
            return [AllowAny()]
        elif self.action in ["retrieve", "create"]:
            # Просматривать детально сущность и создавать новые записи могут ТОЛЬКО авторизованные
            return [IsAuthenticated()]
        # Редактировать и удалять (update, destroy) могут только авторы или админы
        return [IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        """
        Автоматически назначает автора объявления на основе текущего
        авторизованного пользователя (из JWT-токена).
        """
        serializer.save(author=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Контроллер (ViewSet) для работы с отзывами.
    Позволяет просматривать, создавать, редактировать и удалять отзывы
    строго в рамках конкретного объявления.
    """

    serializer_class = ReviewSerializer

    def get_queryset(self):
        """
        Этот метод автоматически берёт id объявления из URL-пути
        и возвращает из базы данных отзывы ТОЛЬКО для этого объявления.
        """
        # Извлекаем id объявления из параметров URL (например, из /api/ads/<ad_id>/reviews/)
        ad_id = self.kwargs.get("ad_id")
        # Фильтруем таблицу отзывов по этому id
        return Review.objects.filter(ad_id=ad_id)

    def get_permissions(self):
        """Управление правами доступа"""
        if self.action == "list":
            # Список объявлений доступен всем (включая анонимов)
            return [AllowAny()]
        elif self.action in ["retrieve", "create"]:
            # Просматривать детально сущность и создавать новые записи могут ТОЛЬКО авторизованные
            return [IsAuthenticated()]
        # Редактировать и удалять (update, destroy) могут только авторы или админы
        return [IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        """
        Автоматически связывает отзыв с текущим авторизованным пользователем
        и конкретным объявлением, ID которого передается в URL-адресе.
        """
        # Извлекаем id объявления из параметров URL (например, из /ads/1/reviews/)
        ad_id = self.kwargs.get("ad_id")

        # Достаем это объявление из базы данных. Если его нет — вернем ошибку 404
        ad_obj = get_object_or_404(Ad, id=ad_id)

        # Сохраняем отзыв, принудительно передав ему и автора, и само объявление
        serializer.save(author=self.request.user, ad=ad_obj)
