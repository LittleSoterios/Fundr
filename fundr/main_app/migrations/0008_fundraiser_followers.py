# Generated by Django 4.2.2 on 2023-06-23 13:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main_app', '0007_profile_saved_fundrs'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundraiser',
            name='followers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
