from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAdminUser,IsAuthenticated,AllowAny
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from .models import User, Category, Product, Order, OrderItem, Cart, Payment, ShippingAddress, Review, Wishlist
from .pagination import CustomPagination
from .serializers import UserSerializer, CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CartSerializer, PaymentSerializer, ShippingAddressSerializer, ReviewSerializer, WishlistSerializer
from rest_framework import permissions
from django.db import transaction
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

@extend_schema(tags=["User"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    # # GET
    def get_queryset(self):
        """Modify queryset based on action"""
        if self.action == "list":
            # If listing all users, return filtered queryset
            return User.objects.all()  # Example filter
        elif self.action == "retrieve" and self.request.user.is_superuser:
            # If retrieving a single user, return only that user
            return User.objects.filter(pk=self.kwargs["pk"])
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        """Customize list behavior"""
        if request.user.is_superuser:
            queryset = self.get_queryset()  # Admins see all active users
        elif request.user.is_staff:
            queryset = self.get_queryset()  # Admins see all active users
        else:
            queryset = self.get_queryset().filter(id=request.user.id)  # Regular users see only themselves
        serializer = self.get_serializer(queryset, many=True)
        if request.user.is_superuser:
            return Response(serializer.data)
        else:
            return Response(serializer.data[0])

    def retrieve(self, request, *args, **kwargs):
        """Customize retrieve behavior"""
        instance = self.get_object()
        if request.user.is_staff or instance == request.user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"detail": "Not allowed"}, status=403)


@extend_schema(tags=["Category"])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination
    permission_classes = [SuperAdminOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
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

@extend_schema(tags=["Product"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPagination

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


@extend_schema(tags=["Cart"])
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    pagination_class = CustomPagination
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

@extend_schema(tags=["Payment"])
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs


@extend_schema(tags=["Shipping"])
class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    pagination_class = CustomPagination
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs


@extend_schema(tags=["Review"])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination

@extend_schema(tags=["Wishlist"])
class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    pagination_class = CustomPagination
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

