from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import User


# Декоратор связывает модель User с классом настроек UserAdmin и регистрирует их в админке
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройка отображения кастомного пользователя в админке."""

    # Какие поля отображать в таблице со списком пользователей
    list_display = ("email", "first_name", "last_name", "phone", "role", "is_staff")

    # Поля, по которым можно фильтровать пользователей в правой панели
    list_filter = ("role", "is_staff", "is_active")

    # Сортируем по email
    ordering = ("email",)

    # Настройка группировки полей внутри карточки пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональные данные",
            {"fields": ("first_name", "last_name", "phone", "image")},
        ),
        (
            "Права доступа",
            {"fields": ("role", "is_active", "is_staff", "is_superuser")},
        ),
    )
