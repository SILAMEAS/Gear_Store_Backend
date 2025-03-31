from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status,filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework import permissions
from django.db import transaction
from django.db.models import Max, Min
from api.app.category.models import Category
from api.app.category.serializer import CategorySerializer
from api.pagination import CustomPagination
from api.models import Product,ProductThumbnail
from api.app.product.serializers import ProductSerializer
from django.db.models import Avg

@extend_schema(tags=["Product"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.annotate(avg_rating=Avg('reviews__rating'))
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'id', 'avg_rating', 'stock', 'updated_at']
    ordering = ['id']

    def perform_create(self, serializer):
        product = serializer.save()
        thumbnails = self.request.FILES.getlist('thumbnails', [])
        for image in thumbnails:
            ProductThumbnail.objects.create(product=product, image=image)

    @action(detail=False, methods=['GET'], permission_classes=[permissions.AllowAny])
    def filter_fields(self, request):
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True).data
        price_range = Product.objects.aggregate(max_price=Max("price"), min_price=Min("price"))
        filters = {
            "filterset_fields": self.filterset_fields,
            "search_fields": self.search_fields,
            "data_filter": {
                "category": serialized_categories,
                "price": {
                    "max": price_range["max_price"] or 100,
                    "min": price_range["min_price"] or 0
                }
            }
        }
        return Response(filters)

    @action(detail=False, methods=['DELETE'], permission_classes=[permissions.IsAdminUser])
    def clear_products(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Only super admins can clear products."}, status=status.HTTP_403_FORBIDDEN)
        with transaction.atomic():
            Product.objects.all().delete()
        return Response({"message": "All products deleted."}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        product_ids = request.data.get("product_ids")

        if not product_ids:
            return Response({"error": "No product ID(s) provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Handle single ID case
        if isinstance(product_ids, (str, int)):  # Single ID case
            product_ids = [int(product_ids)]  # Convert to list for uniform handling

        # Handle multiple IDs case
        elif isinstance(product_ids, list):
            try:
                product_ids = [int(pid) for pid in product_ids]  # Ensure all are integers
            except ValueError:
                return Response({"error": "Invalid product ID format"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid data format, expected a string, integer, or list of IDs"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Perform deletion
        deleted_count, _ = Product.objects.filter(id__in=product_ids).delete()

        if deleted_count == 0:
            return Response({"message": "No products deleted, check IDs"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": f"{deleted_count} product(s) deleted successfully"}, status=status.HTTP_200_OK)