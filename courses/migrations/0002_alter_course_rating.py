# Generated by Django 4.2 on 2024-05-14 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3),
        ),
    ]
