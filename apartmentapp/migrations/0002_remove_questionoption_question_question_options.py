# Generated by Django 4.2.17 on 2025-01-10 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apartmentapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionoption',
            name='question',
        ),
        migrations.AddField(
            model_name='question',
            name='options',
            field=models.ManyToManyField(to='apartmentapp.questionoption'),
        ),
    ]
