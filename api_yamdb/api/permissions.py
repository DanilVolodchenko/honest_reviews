from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin
                or request.user.is_superuser
                or request.user.is_staff)


class IsAdminModerOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and (obj.author == request.user
                     or request.user.is_admin
                     or request.user.is_moderator)
                or request.method in SAFE_METHODS)

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in SAFE_METHODS)
