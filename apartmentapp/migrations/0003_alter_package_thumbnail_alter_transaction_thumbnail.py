# Generated by Django 4.2.17 on 2025-01-01 07:53

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apartmentapp', '0002_alter_user_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='thumbnail',
            field=cloudinary.models.CloudinaryField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='thumbnail',
            field=cloudinary.models.CloudinaryField(max_length=255, null=True),
        ),
    ]
