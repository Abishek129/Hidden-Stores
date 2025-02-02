# Generated by Django 5.1.4 on 2024-12-27 15:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authusers', '0003_address'),
        ('cart_orders', '0005_orderitem_created_at_orderitem_updated_at'),
        ('vendors', '0003_vendordetails_shop_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='vendor',
            field=models.ForeignKey(blank=True, help_text='The vendor associated with this product.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='vendors.vendordetails'),
        ),
        migrations.CreateModel(
            name='DeliveryDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_delivery_date', models.DateField(help_text='The expected date of delivery.')),
                ('delivery_charges', models.DecimalField(decimal_places=2, default=0.0, help_text='Charges for the delivery service.', max_digits=10)),
                ('platform_price', models.DecimalField(decimal_places=2, default=0.0, help_text="Platform's service fee for this order.", max_digits=10)),
                ('overall_price', models.DecimalField(decimal_places=2, editable=False, help_text='The total price including delivery charges and platform price.', max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when this delivery detail was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time when this delivery detail was last updated.')),
                ('address', models.ForeignKey(help_text='The delivery address for the order.', on_delete=django.db.models.deletion.CASCADE, related_name='delivery_details', to='authusers.address')),
                ('order', models.OneToOneField(help_text='The order associated with these delivery details.', on_delete=django.db.models.deletion.CASCADE, related_name='delivery_detail', to='cart_orders.order')),
            ],
        ),
    ]
