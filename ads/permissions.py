from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Кастомное разрешение:
    Редактировать или удалять объект может только его автор или администратор.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет права на уровне конкретного объекта (объявления или отзыва).
        """
        # Если пользователь не авторизован, у него вообще нет прав на изменение/удаление
        if not request.user.is_authenticated:
            return False

        # Администратор имеет право на любые действия с любыми объектами по ТЗ
        if request.user.role == "admin":
            return True

        # Обычный пользователь может редактировать или удалять только СВОЙ объект
        return obj.author == request.user
