from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Content, Lesson


@receiver(post_save, sender=Content)
def update_lesson_passage_time(sender, instance, **kwargs):
    instance.lesson.calculate_passage_time()
    instance.lesson.module.course.calculate_passage_time()


