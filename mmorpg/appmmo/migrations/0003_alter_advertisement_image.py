# Generated by Django 4.2.1 on 2023-05-17 12:18

import appmmo.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmmo', '0002_advertisement_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=appmmo.models.user_directory_path),
        ),
    ]