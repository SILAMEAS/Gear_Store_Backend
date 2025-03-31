# In api/models.py
from django.db import models
from api.models import Category
from cloudinary.models import CloudinaryField
import uuid
from django.db import models
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = CloudinaryField('image', null=True, blank=True)  # Use CloudinaryField
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    colors = models.JSONField(default=list)
    sizes = models.JSONField(default=list)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class ProductThumbnail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="thumbnails")
    image = CloudinaryField('image')  # Use CloudinaryField

    def __str__(self):
        return f"Thumbnail for {self.product.name}"