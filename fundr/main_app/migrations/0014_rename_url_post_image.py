# Generated by Django 4.2.2 on 2023-06-24 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0013_remove_post_image_post_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='url',
            new_name='image',
        ),
    ]
