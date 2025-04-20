from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrTeacherLimitedEdit(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_admin or user.is_teacher)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_admin:
            return True

        if user.is_teacher and request.method in ['PATCH', 'PUT']:
            allowed_fields = {'title'}
            incoming_fields = set(request.data.keys())

            return incoming_fields.issubset(allowed_fields)

        return False