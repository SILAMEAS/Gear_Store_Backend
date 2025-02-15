
from rest_framework import permissions


class SuperAdminOnly(permissions.BasePermission):
    """
    Custom permission to allow only super admins to modify data.
    """

    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow PUT, POST, DELETE only for super admins
        return request.user and request.user.is_superuser
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user  # Only allow access to the owner
