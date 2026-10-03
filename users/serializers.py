from rest_framework import serializers
from django.contrib.auth import get_user_model

# Динамически подключаем нашу кастомную модель пользователя (User) из настроек проекта
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""

    # Поле пароля. write_only=True запрещает бэкенду отправлять пароль обратно в браузер
    password = serializers.CharField(label="Пароль", write_only=True)

    class Meta:
        # Указываем, какую модель обслуживает этот сериализатор-таможенник
        model = User
        # Список из 5 полей, которые пользователю разрешено заполнить при регистрации
        fields = ["email", "first_name", "last_name", "phone", "password"]

    def create(self, validated_data):
        """
        Метод вызывается автоматически после успешной проверки (валидации) всех полей.
        validated_data — это проверенный и чистый словарь, созданный сериализатором.
        Передаем эти данные в наш UserManager (из models.py) для шифрования пароля и сохранения в БД.
        """
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
            password=validated_data["password"],
        )
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Сериализатор для приема email при запросе на сброс пароля"""

    email = serializers.EmailField(label="Электронная почта")


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля.
    Принимает uid, токен безопасности и новый пароль пользователя.
    """

    # Идентификатор пользователя, закодированный в безопасный текстовый формат
    # base64 для передачи в URL без ошибок и скрытия прямой цифры ID
    uid = serializers.CharField(label="User ID (base64)")

    # Одноразовый токен подтверждения, сгенерированный Django
    token = serializers.CharField(label="Токен подтверждения")

    # Новый пароль. write_only=True гарантирует, что пароль не улетит обратно в сеть в JSON-ответе
    new_password = serializers.CharField(label="Новый пароль", write_only=True)
