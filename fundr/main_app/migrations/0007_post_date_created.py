# Generated by Django 4.2.2 on 2023-06-23 15:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_fundraiser_distance_from_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='date_created',
            field=models.DateField(default=datetime.date.today, verbose_name='Date'),
        ),
    ]
