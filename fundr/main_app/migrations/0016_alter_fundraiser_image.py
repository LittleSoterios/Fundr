# Generated by Django 4.2.2 on 2023-06-24 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0015_fundraiser_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundraiser',
            name='image',
            field=models.CharField(blank=True, default='http://localhost:8000/static/main_app/home_pic.png', max_length=200, null=True),
        ),
    ]
