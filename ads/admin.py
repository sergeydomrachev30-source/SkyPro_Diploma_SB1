from django.contrib import admin
from ads.models import Ad, Review


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """
    Настройка отображения объявлений в админ-панели.
    """

    # Столбцы, которые будут видны в общем списке объявлений
    list_display = ("id", "title", "price", "author", "created_at")
    # Поля, по которым будет работать строка поиска вверху страницы
    search_fields = ("title", "description")
    # Боковая панель с фильтрами для удобной сортировки
    list_filter = ("created_at", "price")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Настройка отображения отзывов в админ-панели.
    """

    # Столбцы, которые будут видны в общем списке отзывов
    list_display = ("id", "author", "ad", "created_at")

    # Поиск по тексту отзыва или по email автора
    search_fields = ("text", "author__email")

    list_filter = ("created_at",)
