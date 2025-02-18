# Generated by Django 5.1.4 on 2025-01-05 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_product_cancellation_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='sku',
            field=models.CharField(blank=True, help_text='Unique SKU for the product variant', max_length=14, unique=True),
        ),
    ]
