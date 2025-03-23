from django.db import models
import uuid
class Settings(models.Model):
    MODE = [
        ('light', 'light'),
        ('dark', 'dark')
    ]
    logo = models.ImageField(upload_to='logo/', null=True, blank=True)
    mode = models.CharField(max_length=10, choices=MODE, default='light')
    primary = models.CharField(max_length=7, default="#D6056A")
    secondary = models.CharField(max_length=7, default="#800080")
    success = models.CharField(max_length=7, default="#28a745")
    warning = models.CharField(max_length=7, default="#ffc107")
    danger = models.CharField(max_length=7, default="#dc3545")
    info = models.CharField(max_length=7, default="#007bff")
    Grey = models.CharField(max_length=7, default="#787671")

    def __str__(self):
        return "Theme Colors Configuration"

