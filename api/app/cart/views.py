from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework import permissions
from django.db import transaction
from api.app.cart.serializer import CartSerializer
from api.models import Cart,Product
from api.pagination import CustomPagination


@extend_schema(tags=["Cart"])
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    pagination_class = CustomPagination
    # permission_classes = [IsAuthenticated]
    # Automatically set the user to the currently authenticated user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs


    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        product = Product.objects.get(pk=pk)
        user = request.user

        cart_item, created = Cart.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return Response({"message": "Product added to cart!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['DELETE'], permission_classes=[permissions.IsAdminUser])
    def clear_carts(self, request):
        """Delete all orders and return quantities to stock (Super Admin Only)"""
        if not request.user.is_superuser:
            return Response({"error": "Only super admins can clear orders."}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            carts = Cart.objects.all()  # Retrieve all orders before deleting
            serializer = CartSerializer(carts, many=True)

            for item in serializer.data:
                product = item.product  # Assuming OrderItem has a ForeignKey to Product
                product.stock += item.quantity  # Return quantity to stock
                product.save()
            # Delete all orders
            carts.delete()

        return Response({"message": "All orders have been deleted and quantities returned to stock."},
                        status=status.HTTP_204_NO_CONTENT)
