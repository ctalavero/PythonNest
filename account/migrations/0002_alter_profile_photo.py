# Generated by Django 4.2 on 2024-05-20 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(blank=True, default='logos/default_user_logo.jpg', upload_to='users/%Y/%m/%d'),
        ),
    ]
