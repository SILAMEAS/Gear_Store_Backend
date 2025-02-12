from rest_framework import serializers
from .models import User, Category, Product, Order, OrderItem, Cart, Payment, ShippingAddress, Review, Wishlist
from django.contrib.auth.hashers import make_password
from django.db import transaction
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
        fields = ['id', 'name']

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)  # Required during creation
    name = serializers.CharField(required=True)  # Required during creation
    description = serializers.CharField(required=True)  # Required during creation
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)  # Required during creation
    category = serializers.PrimaryKeyRelatedField(required=True,
                                                  queryset=Category.objects.all())  # Required during creation
    class Meta:
        model = Product
        fields = "__all__"

    def validate(self, attrs):
        # Check if the request is for creation or update
        if self.context['request'].method == 'POST':
            # In creation (POST), require all fields
            for field in ['image', 'name', 'description', 'price', 'category']:
                if field not in attrs:
                    raise serializers.ValidationError({field: f'This field is required.'})
        # If it's an update (PATCH), no extra validation needed
        return attrs

    def update(self, instance, validated_data):
        # Update fields based on what is provided in validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']  # Remove 'order' field

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'items']

    def validate(self, data):
        for item in data.get('items', []):
            product = item['product']
            quantity = item['quantity']

            if quantity > product.stock:  # Assuming `product.stock` represents available stock
                raise serializers.ValidationError({
                    'items': f"Not enough stock for product '{product.name}'. Available: {product.stock}, Requested: {quantity}."
                })

        return data
    # =======================================================
    #                CREAT ORDER
    # =======================================================
    def create(self, validated_data):
        items_data = validated_data.pop('items')

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item in items_data:
                product = item['product']
                quantity = item['quantity']

                # Create order item
                OrderItem.objects.create(order=order, **item)

                # Subtract stock if order is delivered
                if order.status == 'delivered':  # Ensure 'delivered' matches your status choices
                    if product.stock < quantity:
                        raise serializers.ValidationError({
                            'items': f"Not enough stock for product '{product.name}'. Available: {product.stock}, Ordered: {quantity}."
                        })
                    product.stock -= quantity
                    product.save()

        return order

    # =======================================================
    #                UPDATE ORDER
    # =======================================================
    def update(self, instance, validated_data):
        order_item_data = validated_data.pop('items', None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if order_item_data is not None:
                # Clear all
                instance.items.all().delete()
                # Passing
                for order_item in order_item_data:
                    OrderItem.objects.create(order=instance, **order_item)
        return instance


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
