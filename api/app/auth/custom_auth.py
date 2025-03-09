
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


from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Admins can view, create, update, and delete any object.
    - Users can view their own data.
    - Users can create, update, and delete only their own data.
    """

    def has_permission(self, request, view):
        """
        Global permission check for view-level access.
        """
        if request.method in permissions.SAFE_METHODS:
            # Allow GET, HEAD, OPTIONS: Admins can view all, users can view their own
            return request.user and request.user.is_authenticated
        # Allow POST, PUT, DELETE for authenticated users only
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.
        """
        if request.user.is_superuser:
            return True  # Admins have full access

        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user  # Users can view their own data

        # Users can create, update, delete only their own objects
        return obj.user == request.user

    # How It Works
    # Role	View (GET)	Create (POST)	Update (PUT/PATCH)	Delete (DELETE)
    # Admin	✅ All	✅ All	✅ All	✅ All
    # Owner	✅ Own Data	✅ Own Data	✅ Own Data	✅ Own Data
    # Others	❌ No Access	❌ No Access	❌ No Access	❌ No Access