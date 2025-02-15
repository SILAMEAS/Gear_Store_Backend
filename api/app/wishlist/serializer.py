from rest_framework import serializers
from api.models import Product,Wishlist

# Wishlist Serializer
class WishlistSerializer(serializers.ModelSerializer):
    user=serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = Wishlist
        fields = ['id','user','product']
