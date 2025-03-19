from django.db import models
import uuid
class Settings(models.Model):
    logo = models.ImageField(upload_to='logo/', null=True, blank=True)
    primary_main = models.CharField(max_length=7, default="#D6056A")
    secondary_main = models.CharField(max_length=7, default="#800080")
    background_default = models.CharField(max_length=7, default="#F8FAFC")
    background_paper = models.CharField(max_length=7, default="#FFFFFF")
    black_main = models.CharField(max_length=7, default="#000000")
    black_light = models.CharField(max_length=7, default="#FFFFFF")

    def __str__(self):
        return "Theme Colors Configuration"

