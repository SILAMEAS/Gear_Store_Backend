from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework import permissions
from django.db import transaction
from api.models import Order,OrderItem
from api.app.order.serializer import OrderSerializer, OrderItemSerializer
from api.pagination import CustomPagination


@extend_schema(tags=["Order"])
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.order_by('-created_at')
    serializer_class = OrderSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in
    # Automatically set the user to the currently authenticated user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Allow partial updates
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user.id)
        return qs

    def destroy(self, request, *args, **kwargs):
        """Delete an order and return its quantities to stock."""
        instance = self.get_object()

        with transaction.atomic():
            # Return quantity to product stock
            for item in instance.items.all():
                product = item.product  # Assuming OrderItem has a ForeignKey to Product
                product.stock += item.quantity
                product.save()

            # Delete the order
            instance.delete()

        return Response({"message": "Order deleted and quantities returned to stock."},
                 status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['DELETE'], permission_classes=[permissions.IsAdminUser])
    def clear_orders(self, request):
        """Delete all orders and return quantities to stock (Super Admin Only)"""
        if not request.user.is_superuser:
            return Response({"error": "Only super admins can clear orders."}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            orders = Order.objects.all()  # Retrieve all orders before deleting
            for order in orders:
                for item in order.items.all():
                    product = item.product  # Assuming OrderItem has a ForeignKey to Product
                    product.stock += item.quantity  # Return quantity to stock
                    product.save()

            # Delete all orders
            orders.delete()

        return Response({"message": "All orders have been deleted and quantities returned to stock."},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def cancel(self, request, pk=None):
        """Cancel an order and return its quantities to stock."""
        order = self.get_object()

        with transaction.atomic():
            # Return quantity to product stock
            for item in order.items.all():
                product = item.product  # Assuming OrderItem has a ForeignKey to Product
                product.stock += item.quantity
                product.save()

            # Optionally mark the order as canceled instead of deleting it
            order.status = 'canceled'  # Make sure 'canceled' is a valid status in your model
            order.save()

        return Response({"message": "Order canceled and quantities returned to stock."}, status=status.HTTP_200_OK)

@extend_schema(tags=["OrderItem"])
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    pagination_class = CustomPagination
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
