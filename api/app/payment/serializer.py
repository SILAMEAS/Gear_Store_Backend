from rest_framework import serializers
from api.models import Payment
import uuid
# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    transaction_id = serializers.UUIDField(default=uuid.uuid4)
    class Meta:
        model = Payment
        fields = ["id","user", "transaction_id","amount","order","payment_method"]