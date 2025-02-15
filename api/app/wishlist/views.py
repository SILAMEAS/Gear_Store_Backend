from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import permissions
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from api.models import Wishlist
from api.pagination import CustomPagination
from api.app.wishlist.serializer import WishlistSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Wishlist"])
class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data.get("product")  # Ensure "product" is in the serializer

        # Check if the product is already in the user's wishlist
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError({"error": "This product is already in your wishlist."})

        # Save the wishlist item if not already in the wishlist
        serializer.save(user=user)
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    @action(detail=True, methods=['DELETE'])
    def remove_wishlist(self, request, pk=None):
        """Remove a product from the user's wishlist"""
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        wishlist_item = get_object_or_404(Wishlist, user=user, product_id=pk)
        wishlist_item.delete()
        return Response({"message": "Product removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)
    @action(detail=False, methods=['DELETE'], permission_classes=[permissions.IsAdminUser])
    def clear_wishlists(self, request):
        """Delete all orders and return quantities to stock (Super Admin Only)"""
        if not request.user.is_superuser:
            return Response({"error": "Only super admins can clear wishlists."}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            wishlists = Wishlist.objects.all()  # Retrieve all orders before deleting
            # Delete all orders
            wishlists.delete()

        return Response({"message": "All wishlists have been deleted ."},
                        status=status.HTTP_204_NO_CONTENT)
