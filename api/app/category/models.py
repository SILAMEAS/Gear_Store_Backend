from django.db import models



# Category Model (for product categories)
class Category(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name

