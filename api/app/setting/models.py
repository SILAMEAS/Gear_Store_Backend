from django.db import models
import uuid
class Settings(models.Model):
    MODE = [
        ('light', 'light'),
        ('dark', 'dark')
    ]
    logo = models.ImageField(upload_to='logo/', null=True, blank=True)
    mode = models.CharField(max_length=10, choices=MODE, default='light')
    Primary = models.CharField(max_length=7, default="#D6056A")
    Secondary = models.CharField(max_length=7, default="#800080")
    Success = models.CharField(max_length=7, default="#28a745")
    Warning = models.CharField(max_length=7, default="#ffc107")
    Danger = models.CharField(max_length=7, default="#dc3545")
    Info = models.CharField(max_length=7, default="#007bff")

    def __str__(self):
        return "Theme Colors Configuration"

