# Generated by Django 5.1.1 on 2025-02-22 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_payment_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, default='profile_images/default.jpg', null=True, upload_to='profile_images/'),
        ),
    ]
