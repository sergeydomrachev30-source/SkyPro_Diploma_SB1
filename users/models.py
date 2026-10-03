from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    """
    Менеджер для создания пользователей и суперпользователей
    с авторизацией по email вместо стандартного username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает, шифрует пароль и сохраняет пользователя в базе данных.
        """
        if not email:
            raise ValueError("Email является обязательным полем")

        email = self.normalize_email(email)

        # Устанавливаем роль по умолчанию, если она не передана
        extra_fields.setdefault("role", "user")

        # Создаем объект пользователя, все поля из REQUIRED_FIELDS
        # и регистрационной формы придут сюда внутри extra_fields
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя (администратора) с максимальными
        правами доступа и автоматическим назначением роли 'admin'.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь флаг is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь флаг is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя, где в качестве уникального идентификатора
    (логина) используется адрес электронной почты вместо username.
    """

    # Основные персональные данные пользователя (все поля обязательные по ТЗ)
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    phone = models.CharField(max_length=30, verbose_name="Телефон")

    # Главное поле авторизации, должно быть уникальным для каждого аккаунта
    email = models.EmailField(
        unique=True, max_length=254, verbose_name="Электронная почта"
    )

    # Ярлыки-константы для защиты от опечаток в коде
    USER = "user"
    ADMIN = "admin"

    # Варианты выбора для отображения в админ-панели Django
    ROLE_CHOICES = [(USER, "Пользователь"), (ADMIN, "Администратор")]

    # Роль пользователя с ограничением выбора (по умолчанию обычный пользователь)
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default=USER, verbose_name="Роль"
    )

    image = models.ImageField(
        upload_to="users_avatars/", null=True, blank=True, verbose_name="Аватарка"
    )

    # Служебные флаги Django для управления доступом и блокировками
    is_staff = models.BooleanField(default=False, verbose_name="Статус сотрудника")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    # Привязываем кастомный менеджер к модели для управления объектами в базе
    objects = UserManager()

    # Системные настройки Django для кастомной модели
    USERNAME_FIELD = "email"  # Указываем, какое поле является логином
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone",
    ]  # Поля, запрашиваемые при createsuperuser

    # Добавляем этот блок для перевода заголовков и кнопок в админке
    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Пользователи"
