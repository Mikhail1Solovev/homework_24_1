from rest_framework import permissions
from courses.models import Course  # Импорт модели Course


class IsModerator(permissions.BasePermission):
    """
    Разрешение для пользователей, которые входят в группу 'Moderators'.
    """

    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(
            name='Moderators').exists()


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Разрешение для владельца объекта или модераторов.
    """

    def has_permission(self, request, view):
        # Разрешаем только аутентифицированным пользователям
        if not request.user or not request.user.is_authenticated:
            return False

        # Если это действие создания, проверяем владельца курса или модератора
        if request.method == 'POST':
            course_id = request.data.get('course')
            if course_id:
                try:
                    course = Course.objects.get(id=course_id)
                    return course.owner == request.user or request.user.groups.filter(
                        name='Moderators').exists()
                except Course.DoesNotExist:
                    return False
            return False

        # Для остальных действий разрешаем продолжить проверку объекта
        return True

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ, если пользователь является владельцем объекта или
        # модератором
        return obj.owner == request.user or request.user.groups.filter(
            name='Moderators').exists()
