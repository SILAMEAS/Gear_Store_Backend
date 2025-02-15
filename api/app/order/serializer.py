from rest_framework import serializers
from django.db import transaction
from api.models import Order,Product,OrderItem

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
