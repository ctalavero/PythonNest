# Generated by Django 4.2 on 2024-05-16 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_course_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='logo',
            field=models.ImageField(blank=True, default='logos/course-logo-default.jpg', null=True, upload_to='logos'),
        ),
    ]