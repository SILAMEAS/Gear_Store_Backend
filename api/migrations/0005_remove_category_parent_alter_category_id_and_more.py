# Generated by Django 5.1.1 on 2025-02-09 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_product_id_alter_product_stock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='parent',
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
