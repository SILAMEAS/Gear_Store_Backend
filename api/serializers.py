from rest_framework import serializers
from .models import User, Category, Product, Order, OrderItem, Cart, Payment, ShippingAddress, Review, Wishlist
from django.contrib.auth.hashers import make_password

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password","is_active","is_staff","is_superuser"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    # category = CategorySerializer(read_only=True)
    image = serializers.ImageField(required=True)
    class Meta:
        model = Product
        fields = "__all__"

# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True  # Allow passing only product_id
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'quantity']  # Remove 'order' field

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)  # Nested input for order items
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Auto-assign user

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'items']
        read_only_fields = ['total_price', 'status', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])  # Safely pop items

        # Initialize total price to 0
        total_price = 0

        # Create the order instance (without total_price for now)
        order = Order.objects.create(**validated_data)

        order_items = []

        for item_data in items_data:
            product = item_data['product_id']  # Get product from product_id
            quantity = item_data['quantity']
            price = product.price * quantity  # Calculate price based on current product price

            # Ensure sufficient stock
            if product.stock < quantity:
                raise serializers.ValidationError(f"Not enough stock for {product.name}")

            product.stock -= quantity  # Reduce stock
            product.save()

            # Create the OrderItem instance with the correct order reference
            order_item = OrderItem(order=order, product=product, quantity=quantity, price=price)
            order_items.append(order_item)
            total_price += price  # Accumulate total price

        # Bulk create the OrderItem instances
        OrderItem.objects.bulk_create(order_items)

        # Assign the total_price to the order
        order.total_price = total_price

        # Save the order with the total price
        order.save()

        return order



# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"

# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

# ShippingAddress Serializer
class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"

# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"

# Wishlist Serializer
class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"
