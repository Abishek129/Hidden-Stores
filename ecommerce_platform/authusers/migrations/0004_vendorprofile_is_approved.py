# Generated by Django 5.1.4 on 2025-01-10 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authusers', '0003_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorprofile',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
