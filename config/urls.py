from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from config import settings

# Настройка генератора схемы Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="SkyPro Diploma SB1 API",
        default_version="v1",
        description="Документация для бэкенд-части Доски объявлений",
    ),
    public=True,
    permission_classes=[
        permissions.AllowAny,
    ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Эндпоинты для документации Swagger
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Авторизация при помощи JWT-токенов
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include("users.urls")),
    # Подключаем маршруты объявлений. Префикс 'api/' добавим внутри самого ads.urls
    path("", include("ads.urls")),
]

# Подключение раздачи медиа-файлов (аватарок) и статики в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
