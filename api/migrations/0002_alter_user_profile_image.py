# Generated by Django 5.1.1 on 2025-03-31 08:41

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=cloudinary.models.CloudinaryField(blank=True, default='profile_images/default.jpg', max_length=255, null=True, verbose_name='profile_images'),
        ),
    ]
