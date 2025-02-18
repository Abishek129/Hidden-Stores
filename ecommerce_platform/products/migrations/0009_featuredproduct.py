# Generated by Django 5.1.4 on 2025-01-17 10:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_stock'),
        ('vendors', '0003_vendordetails_shop_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the product was marked as featured')),
                ('product', models.OneToOneField(help_text='The featured product', on_delete=django.db.models.deletion.CASCADE, related_name='featured_status', to='products.product')),
                ('vendor', models.ForeignKey(help_text='Vendor owning the featured product', on_delete=django.db.models.deletion.CASCADE, related_name='featured_products', to='vendors.vendordetails')),
            ],
        ),
    ]
