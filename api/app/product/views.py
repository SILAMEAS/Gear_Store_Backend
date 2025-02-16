from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework import permissions
from django.db import transaction
from api.pagination import CustomPagination
from api.models import Product,ProductThumbnail
from api.app.product.serializers import ProductSerializer


@extend_schema(tags=["Product"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        product = serializer.save()
        thumbnails = self.request.FILES.getlist('thumbnails')  # Get multiple uploaded files

        for image in thumbnails:
            ProductThumbnail.objects.create(product=product, image=image)

    @action(detail=False, methods=['DELETE'], permission_classes=[permissions.IsAdminUser])
    def clear_products(self, request):
        """Delete all orders and return quantities to stock (Super Admin Only)"""
        if not request.user.is_superuser:
            return Response({"error": "Only super admins can clear products."}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            products = Product.objects.all()  # Retrieve all orders before deleting
            # Delete all products
            products.delete()

        return Response({"message": "All products have been deleted."},
                        status=status.HTTP_204_NO_CONTENT)
