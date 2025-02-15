from rest_framework import serializers
from api.models import Product,Cart
# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    image=serializers.ImageField(source='product.image', read_only=True)
    name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price',max_digits=10,decimal_places=2,read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity',"image","name","price","total_price"]
