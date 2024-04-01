from rest_framework import permissions


class IsEmployee(permissions.BasePermission):
    """
    Разрешение для сотрудника
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_employee)
