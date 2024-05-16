# Generated by Django 4.2 on 2024-05-15 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('courses', '0003_alter_course_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='content_type',
            field=models.ForeignKey(limit_choices_to={'model__in': ('text', 'video', 'image', 'file')}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='content',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='courses.lesson'),
        ),
    ]