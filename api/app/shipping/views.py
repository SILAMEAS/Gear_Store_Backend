
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework import permissions
from django.db import transaction

from api.app.shipping.serializer import ShippingAddressSerializer
from api.models import ShippingAddress
from api.pagination import CustomPagination


@extend_schema(tags=["Shipping"])
class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return super().create(request, *args, **kwargs)
        return Response({"message": "Super can't be shipped order to themself"},
                        status=status.HTTP_204_NO_CONTENT)
    @action(detail=False, methods=['DELETE'], permission_classes=[permissions.IsAdminUser])
    def clear_shipping_addresses(self, request):
        """Delete all shipping_addresses and return quantities to stock (Super Admin Only)"""
        if not request.user.is_superuser:
            return Response({"error": "Only super admins can clear orders."}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            # Delete all orders
            ShippingAddress.objects.all().delete()

        return Response({"message": "All orders have been deleted and quantities returned to stock."},
                        status=status.HTTP_204_NO_CONTENT)


