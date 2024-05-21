from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.template.loader import render_to_string
from django.urls import reverse
from taggit.managers import TaggableManager

from account.storage import OverwriteStorage
from .fields import OrderField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

from .functions import get_video_id_from_url, get_youtube_video_duration, get_video_duration


class Course(models.Model):
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='courses_created')
    published = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='logos', blank=True, null=True, default='logos/course-logo-default.jpg',storage=OverwriteStorage())
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()
    user = models.ManyToManyField('auth.User', related_name='courses_joined', blank=True)
    passage_time = models.DurationField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2,blank=True, null=True)

    def clean_rating(self):
        if self.rating < 0 or self.rating > 5:
            raise ValidationError('Rating must be between 0 and 5')

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', args=[self.slug])

    def update_rating(self):
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        self.rating = avg_rating if avg_rating is not None else 0
        self.save()

    def calculate_passage_time(self):
        total_time = timedelta()
        for module in self.modules.all():
            for lesson in module.lessons.all():
                lesson.calculate_passage_time()
                if lesson.passage_time:
                    total_time += lesson.passage_time
        self.passage_time = total_time
        self.save()

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'({self.order}:{self.pk}) {self.title}'



class ItemABS(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'({self.pk}) '+self.title

    def render(self):
        return render_to_string(
            f'content/{self._meta.model_name}.html',
            {'item': self}
        )

class Text(ItemABS):
    content = models.TextField()

class File(ItemABS):
    file = models.FileField(upload_to='files',storage=OverwriteStorage())

class Image(ItemABS):
    file = models.FileField(upload_to='images',storage=OverwriteStorage())

class Video(ItemABS):
    url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='videos', blank=True, null=True,storage=OverwriteStorage())
    duration = models.DurationField(blank=True, null=True)

    def clean(self):
        if not self.url and not self.file:
            raise ValidationError('Either URL or file must be provided.')
        if self.file and not self.file.name.endswith('.mp4'):
            raise ValidationError('Uploaded video must be a .mp4 file.')

    def save(self, *args, **kwargs):
        if self.url:
            self.file = None
            video_id = get_video_id_from_url(self.url)
            if video_id is not None:
                duration_in_seconds = get_youtube_video_duration(video_id, settings.GOOGLE_YOUTUBE_API_KEY)
                self.duration = timedelta(seconds=duration_in_seconds)
        if self.file:
            video_path = default_storage.path(self.file.name)
            duration_in_seconds = get_video_duration(video_path)
            self.duration = timedelta(seconds=duration_in_seconds)

        super().save(*args, **kwargs)


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    order = OrderField(blank=True, for_fields=['module'])
    passage_time = models.DurationField(blank=True, null=True)
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'({self.order}:{self.pk}) {self.title}'

    def calculate_passage_time(self):
        total_time = timedelta()
        for content in self.contents.all():
            item = content.item
            if isinstance(item, Video) and item.duration:
                total_time += item.duration
            elif isinstance(item, Text):
                word_count = len(item.content.split())
                reading_time = word_count / 200
                total_time += timedelta(minutes=reading_time)
        self.passage_time = total_time
        self.save()

class Content(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='contents',on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('text', 'video', 'image', 'file')}, related_name='course_contents')
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    order = OrderField(blank=True, for_fields=['lesson'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'({self.order}:{self.pk}) {self.content_type.model}'

class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'user')

    def __str__(self):
        return f'{self.user} - {self.course} - {self.rating}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.course.update_rating()