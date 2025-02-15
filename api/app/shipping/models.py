# Create your models here.
import uuid
from django.db import models
from api.app.user.models import User
from api.models import Order
# Shipping Address Model
class ShippingAddress(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.address}"

