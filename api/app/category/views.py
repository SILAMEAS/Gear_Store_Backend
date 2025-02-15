from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from api.app.auth.custom_auth import SuperAdminOnly
from api.models import Category
from api.app.category.serializer import CategorySerializer
from api.pagination import CustomPagination


@extend_schema(tags=["Category"])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination
    permission_classes = [SuperAdminOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"detail": "Category not found"}, status=404)

        # Example: Custom logic before deletion (optional)
        if instance.is_locked:  # If the instance is locked, don't allow deletion
            return Response({"detail": "This object cannot be deleted."}, status=status.HTTP_400_BAD_REQUEST)

        # Perform the actual deletion
        self.perform_destroy(instance)

        # Return a custom response message
        return Response({"message": "Delete successfully"}, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        # This is where the actual deletion takes place
        instance.delete()
