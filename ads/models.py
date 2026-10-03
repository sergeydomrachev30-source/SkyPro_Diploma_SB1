from django.conf import settings
from django.db import models


class Ad(models.Model):
    """
    Модель объявления на сайте.
    Описывает структуру таблицы объявлений в базе данных PostgreSQL.
    """

    # Основные текстовые и числовые поля объявления
    title = models.CharField(max_length=200, verbose_name="Название товара")
    price = models.PositiveIntegerField(verbose_name="Цена товара")
    description = models.TextField(verbose_name="Описание товара")

    # Связываем объявление с кастомным пользователем через settings.AUTH_USER_MODEL.
    # on_delete=models.CASCADE означает, что при удалении пользователя удалятся и его объявления.
    # related_name="ads" позволяет получить все объявления юзера через конструкцию user.ads.all().
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ads",
        verbose_name="Автор объявления",
    )

    # auto_now_add=True автоматически фиксирует дату и время создания в момент сохранения в БД
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        # Человекочитаемые названия для отображения в админ-панели Django
        verbose_name = "объявление"
        verbose_name_plural = "Объявления"

        # Сортировка по умолчанию: знак минус означает обратный порядок (от новых к старым)
        ordering = ["-created_at"]

    def __str__(self):
        """
        Метод возвращает понятное имя объекта (заголовок товара)
        вместо системного <Ad object (id)>
        """
        return self.title


class Review(models.Model):
    """
    Модель отзыва под конкретным объявлением.
    Связана одновременно и с автором отзыва, и с самим объявлением.
    """

    text = models.TextField(verbose_name="Текст отзыва")

    # Связь с автором отзыва (пользователем)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор отзыва",
    )

    # Связь с объявлением. При удалении объявления все отзывы к нему удаляются автоматически (CASCADE)
    ad = models.ForeignKey(
        Ad, on_delete=models.CASCADE, related_name="reviews", verbose_name="Объявление"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        """
        Превращение self.ad в строку автоматически вызывает
        метод __str__ модели Ad и подставляет название товара
        """
        return f"Отзыв от {self.author} к объявлению {self.ad}"
