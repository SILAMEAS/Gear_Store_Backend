# Generated by Django 5.1.1 on 2025-03-31 06:29

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='productthumbnail',
            name='image',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
    ]
