from rest_framework import serializers
from api.models import ShippingAddress
# ShippingAddress Serializer
class ShippingAddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ShippingAddress
        fields = "__all__"
