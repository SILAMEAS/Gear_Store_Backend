from django.db import models
from api.models import Category

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)

    # New Fields
    colors = models.JSONField(default=list)  # Stores an array of colors
    sizes = models.JSONField(default=list)  # Stores an array of sizes
    rating = models.FloatField(default=0.0)  # Stores the product's rating

    def __str__(self):
        return self.name
#ProductThumbnail
class ProductThumbnail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="thumbnails")
    image = models.ImageField(upload_to='products/thumbnails/')

    def __str__(self):
        return f"Thumbnail for {self.product.name}"