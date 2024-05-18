from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from courses.models import Content, Lesson, Video, Text


@receiver(post_save, sender=Content)
def update_lesson_passage_time(sender, instance, **kwargs):
    instance.lesson.calculate_passage_time()
    instance.lesson.module.course.calculate_passage_time()

@receiver(post_save, sender=Video)
def update_video_passage_time(sender, instance, **kwargs):
    video_content_type = ContentType.objects.get_for_model(instance)
    content = Content.objects.filter(content_type=video_content_type, object_id=instance.id).first()
    if content:
        lesson = content.lesson
        lesson.calculate_passage_time()
        lesson.module.course.calculate_passage_time()

@receiver(post_save, sender=Text)
def update_text_passage_time(sender, instance, **kwargs):
    text_content_type = ContentType.objects.get_for_model(instance)
    content = Content.objects.filter(content_type=text_content_type, object_id=instance.id).first()
    if content:
        lesson = content.lesson
        lesson.calculate_passage_time()
        lesson.module.course.calculate_passage_time()
