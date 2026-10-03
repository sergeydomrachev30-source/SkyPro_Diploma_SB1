from rest_framework.routers import SimpleRouter
from ads.views import AdViewSet, ReviewViewSet
from django.urls import path, include

# Создаем объект роутера
router = SimpleRouter()

# Регистрируем наш контроллер.
# Первый аргумент 'ads' — это то, какой префикс будет у урлов (получится /ads/)
# Второй аргумент — наш класс контроллера
router.register("api/ads", AdViewSet, basename="ads")

# Передаем сгенерированные роутером пути в стандартный список urlpatterns Django
urlpatterns = [
    # Сюда попадают стандартные урлы объявлений: /api/ads/ и /api/ads/<id>/
    path("", include(router.urls)),
    # здесь мы вручную создаем вложенный маршрут для отзывов конкретного объявления!
    # <int:ad_id> — это та самая переменная, которую наш ReviewViewSet поймает через self.kwargs.get("ad_id")
    path(
        "api/ads/<int:ad_id>/reviews/",
        ReviewViewSet.as_view(
            {
                "get": "list",  # Если пришел GET-запрос — показать список отзывов к этому объявлению
                "post": "create",  # Если пришел POST-запрос — создать новый отзыв к этому объявлению
            }
        ),
        name="ad-reviews",
    ),
    # Дополнительный маршрут, если нужно отредактировать или удалить конкретный отзыв по его собственному ID
    path(
        "api/ads/<int:ad_id>/reviews/<int:pk>/",
        ReviewViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="ad-review-detail",
    ),
]
