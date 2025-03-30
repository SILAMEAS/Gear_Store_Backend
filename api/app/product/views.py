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
    queryset = Product.objects.annotate(avg_rating=Avg('reviews__rating'))  # Compute rating dynamically
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPagination
    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Define filter fields
    filterset_fields = ['category', 'price']

    # Define search fields (uses `icontains` lookup by default)
    search_fields = ['name','description']

    # Define ordering fields (default: ordering by 'id')
    ordering_fields = ['price', 'name','id','avg_rating',"stock",'updated_at']
    ordering = ['id']
    # /api/products/?ordering=price    # Ascending price
    # /api/products/?ordering=-price   # Descending price
    # /api/products/?search=laptop
    # /api/products/?category=electronics&price=100
    # /api/products/?min_price=50&max_price=200

    def perform_create(self, serializer):
        product = serializer.save()
        thumbnails = self.request.FILES.getlist('thumbnails')  # Get multiple uploaded files

        for image in thumbnails:
            ProductThumbnail.objects.create(product=product, image=image)

    @action(detail=False, methods=['GET'], permission_classes=[permissions.AllowAny])
    def filter_fields(self, request):
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True).data
        # Get max and min price from Product model
        price_range = Product.objects.aggregate(
            max_price=Max("price"),
            min_price=Min("price")
        )
        """Expose filter fields to the frontend"""
        filters = {
            "filterset_fields": self.filterset_fields,
            "search_fields": self.search_fields,
            # "ordering_fields": self.ordering_fields
            "data_filter":{
                "category": serialized_categories,
                "price": {
                    "max": price_range["max_price"] if price_range["max_price"] is not None else 100,
                    # Default if no products
                    "min": price_range["min_price"] if price_range["min_price"] is not None else 0
                }
            }
        }
        return Response(filters)

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