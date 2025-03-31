import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

# Custom User Model
class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    # profile_image = models.ImageField(
    #     upload_to='profile_images/',
    #     null=True,
    #     blank=True,
    #     default='profile_images/default.jpg'
    # )
    # profile_image = CloudinaryField('profile_images/', null=True, blank=True,default='profile_images/default.jpg')  # Use CloudinaryField

    # profile_image = CloudinaryField('image', null=True, blank=True)  # Use CloudinaryField
    profile_image = CloudinaryField('image', null=True, blank=True)  # Use CloudinaryField
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    ]

    role = models.CharField(choices=ROLE_CHOICES, max_length=10, default='user')

    phone = models.CharField(max_length=15, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)  # Date of Birth
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} : {self.id}"

