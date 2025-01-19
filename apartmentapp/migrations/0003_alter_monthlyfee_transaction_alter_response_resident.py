# Generated by Django 4.2.17 on 2025-01-19 03:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apartmentapp', '0002_auto_20250118_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthlyfee',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='monthly_fees', to='apartmentapp.transaction'),
        ),
        migrations.AlterField(
            model_name='response',
            name='resident',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='responses', to=settings.AUTH_USER_MODEL),
        ),
    ]
