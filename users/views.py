from drf_yasg.utils import swagger_auto_schema

# Инструмент Django для динамического поиска нашей кастомной модели пользователя
from django.contrib.auth import get_user_model

# Готовые утилиты Django для генерации одноразовых ключей сброса пароля
from django.contrib.auth.tokens import default_token_generator

# Утилиты Django для безопасного кодирования ID пользователя в формат base64 для ссылок
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Служебные инструменты Django для перевода текстовых строк в байты (нужно для base64) и обратно
from django.utils.encoding import force_bytes, force_str

# Статус-коды ответов API (например, 201 Created, 400 Bad Request) от DRF
from rest_framework import status

# Класс DRF для формирования красивых JSON-ответов клиенту/фронтенду
from rest_framework.response import Response

# Базовый класс DRF для создания контроллеров (View) вручную
from rest_framework.views import APIView

# Глобальное разрешение DRF, открывающее доступ к эндпоинту абсолютно всем (анонимам тоже)
from rest_framework.permissions import AllowAny

# Импортируем наших созданных ранее "таможенников"-сериализаторов из соседнего файла
from .serializers import (
    UserRegistrationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

# Сохраняем нашу кастомную модель пользователя в переменную для работы с ней
User = get_user_model()


class UserRegistrationView(APIView):
    """
    Эндпоинт для самостоятельной регистрации новых пользователей.
    Использует стандартный базовый класс APIView из Django REST Framework.
    """

    # Разрешаем доступ всем пользователям, так как аноним должен иметь возможность зарегистрироваться
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def post(self, request):
        """
        Обрабатывает входящий POST-запрос от фронтенда для создания аккаунта.
        request.data содержит в себе сырые данные, присланные пользователем.
        """
        # Передаем сырые данные из запроса в наш сериализатор-таможенник для проверки
        serializer = UserRegistrationSerializer(data=request.data)

        # Запускаем автоматическую валидацию полей (email, имя, фамилия, телефон, пароль)
        if serializer.is_valid():
            # Если ошибок нет, вызываем метод create() внутри сериализатора и сохраняем юзера
            serializer.save()
            # Возвращаем фронтенду успешный ответ со статус-кодом 201 Created
            return Response(
                {"detail": "Пользователь успешно зарегистрирован."},
                status=status.HTTP_201_CREATED,
            )

        # Если в данных были ошибки (например, неверный email), возвращаем список ошибок и статус 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Эндпоинт (View) для запроса на сброс пароля.
    Принимает email, генерирует секретные ключи (uid, token) и высылает ссылку.
    """

    # Разрешаем доступ всем, так как неавторизованный пользователь должен иметь возможность восстановить пароль
    permission_classes = [AllowAny]
    # Указываем сериализатор, чтобы Swagger знал, какое тело запроса (email) мы ждем
    serializer_class = PasswordResetRequestSerializer

    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        """
        Обрабатывает входящий POST-запрос с email для сброса пароля.
        Проверяет данные через сериализатор, ищет пользователя в базе,
        кодирует его ID в base64 и генерирует одноразовый токен.
        """
        # Передаем входящие данные (email) нашему сериализатору для проверки корректности
        serializer = PasswordResetRequestSerializer(data=request.data)

        # Если формат email невалидный (например, нет значка @), возвращаем ошибку 400
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Забираем очищенный и проверенный email из словаря validated_data
        email = serializer.validated_data["email"]

        try:
            # Пытаемся найти пользователя в базе данных по его электронной почте
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # БЕЗОПАСНОСТЬ: Если пользователя нет, мы все равно возвращаем статус 200 OK.
            # Это нужно, чтобы хакеры не могли перебором email выяснить, кто зарегистрирован на сайте.
            return Response(
                {
                    "detail": "Инструкции по восстановлению пароля отправлены на указанный email."
                },
                status=status.HTTP_200_OK,
            )

        # Переводим числовой ID пользователя в байты, а затем кодируем в безопасный текст base64
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Генерируем уникальный временный одноразовый хэш-токен безопасности для этого пользователя
        token = default_token_generator.make_token(user)

        # Формируем URL-путь строго по шаблону из ТЗ: /<url>/{uid}/{token}
        reset_url = f"/users/reset_password_confirm/{uid}/{token}/"

        # Печатаем сгенерированную ссылку прямо в терминал PyCharm (так как включен консольный EMAIL_BACKEND)
        print(f"ССЫЛКА ДЛЯ СБРОСА ПАРОЛЯ ДЛЯ {email}:")
        print(reset_url)

        # Возвращаем успешный JSON-ответ фронтенду с такой же красивой и понятной фразой
        return Response(
            {
                "detail": "Инструкции по восстановлению пароля отправлены на указанный email."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    Эндпоинт (View) для подтверждения сброса пароля.
    Принимает uid, токен и новый пароль, проверяет их и меняет пароль в базе данных.
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
    def post(self, request):
        """
        Обрабатывает входящий POST-запрос для подтверждения смены пароля.
        Принимает uid (base64), одноразовый токен и новый пароль.
        """
        # Передаем входящие данные (uid, token, new_password) в сериализатор на проверку
        serializer = PasswordResetConfirmSerializer(data=request.data)

        # Если какое-то из трех полей не передано, возвращаем ошибку 400 Bad Request
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Извлекаем проверенные данные из словаря validated_data
        uidb64 = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            # Расшифровываем текстовую строку base64 обратно в байты, а затем в обычную строку с ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            # Находим пользователя в базе данных по его первичному ключу (pk / id)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # Если ссылка повреждена или пользователя не существует, возвращаем ошибку
            return Response(
                {"detail": "Неверный или поврежденный идентификатор ссылки."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверяем, валиден ли одноразовый секретный токен для этого конкретного пользователя
        if default_token_generator.check_token(user, token):
            # Если токен верный и его время жизни не истекло, хэшируем и устанавливаем новый пароль
            user.set_password(new_password)
            # Сохраняем обновленного пользователя в базу данных PostgreSQL
            user.save()
            return Response(
                {
                    "detail": "Пароль успешно изменен. Теперь вы можете войти в систему с новым паролем."
                },
                status=status.HTTP_200_OK,
            )

        # Если токен оказался поддельным или уже был использован ранее, возвращаем ошибку 400
        return Response(
            {
                "detail": "Ссылка для сброса пароля устарела или является недействительной."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
