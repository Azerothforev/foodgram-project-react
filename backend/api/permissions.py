from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение: только автор может изменять, остальные могут только читать.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь право доступа к представлению.
        """
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь право доступа к объекту.
        """
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешение: только администратор может изменять,
    остальные могут только читать.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь право доступа к представлению.
        """
        return (
            request.method in SAFE_METHODS
            or request.user.is_admin
        )
