# Generated by Django 5.1.4 on 2024-12-25 15:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0002_remove_productvariant_variant_images_variantimage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(help_text='The user associated with this cart.', on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, help_text='The quantity of this product in the cart.')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(help_text='The cart this item belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='cart_orders.cart')),
                ('product_variant', models.ForeignKey(help_text='The specific product variant added to the cart.', on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='products.productvariant')),
            ],
        ),
    ]
