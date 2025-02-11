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

    # def list(self, request):
    #     pass

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

@extend_schema(tags=["Product"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPagination

@extend_schema(tags=["Order"])
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user.id)
        return qs
    #
    # def retrieve(self, request, pk=None):
    #     pass
    #
    # def update(self, request, pk=None):
    #     pass
    #
    # def partial_update(self, request, pk=None):
    #     pass
    #
    # def destroy(self, request, pk=None):
    #     pass



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

