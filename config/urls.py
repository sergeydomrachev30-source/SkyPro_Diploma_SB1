from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка генератора схемы Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="SkyPro Diploma SB1 API",
      default_version='v1',
      description="Документация для бэкенд-части Доски объявлений",
   ),
   public=True,
   permission_classes=[permissions.AllowAny,],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Эндпоинты для документации Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
