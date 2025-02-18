# Generated by Django 5.1.4 on 2025-01-06 12:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart_orders', '0009_orderitem_order_status'),
        ('products', '0005_alter_productvariant_sku'),
        ('vendors', '0003_vendordetails_shop_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommissionAndGST',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_price', models.DecimalField(decimal_places=2, help_text='Price of the product (inclusive of GST)', max_digits=10)),
                ('commission_rate', models.DecimalField(decimal_places=2, help_text='Commission rate based on price slabs', max_digits=5)),
                ('commission_amount', models.DecimalField(decimal_places=2, help_text='Commission amount calculated on product price', max_digits=10)),
                ('gst_on_commission', models.DecimalField(decimal_places=2, help_text='GST calculated on the commission amount', max_digits=10)),
                ('total_commission_with_gst', models.DecimalField(decimal_places=2, help_text='Total commission amount including GST', max_digits=10)),
                ('total_deduction', models.DecimalField(decimal_places=2, help_text='Total deduction (commission + GST)', max_digits=10)),
                ('vendor_earnings', models.DecimalField(decimal_places=2, help_text='Final earnings for the vendor after deductions', max_digits=10)),
                ('calculated_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the calculation was made')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commission_details', to='cart_orders.orderitem')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commission_details', to='products.product')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commission_details', to='vendors.vendordetails')),
            ],
        ),
    ]
