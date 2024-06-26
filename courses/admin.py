from django.contrib import admin
from django.utils.html import format_html

from .models import Course, Module, Lesson, Content, Text, File, Image, Video, Review


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    show_change_link = True

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title','display_logo','published', 'created_by', 'created_at', 'rating')
    list_filter = ('created_at', 'tags')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('user',)
    readonly_fields = ('created_at','display_logo')
    list_editable = ('published',)
    fieldsets = (
        (None, {
            'fields': ('created_by', 'title', 'slug','logo','display_logo', 'description', 'tags', 'user', 'passage_time', 'rating','published')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )
    inlines = [ModuleInline]

    def display_logo(self, obj):
        return format_html('<img src="{}" height="50" />', obj.logo.url)
    display_logo.short_description = 'Logo'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    list_editable = ('order',)
    ordering = ('lessons', 'order')
    inlines = [LessonInline]



@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'passage_time')
    list_filter = ('module',)
    search_fields = ('title',)
    list_editable = ('order',)
    ordering = ('module', 'order')


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('item_title','lesson', 'content_type', 'object_id', 'order')
    list_filter = ('lesson', 'content_type')
    search_fields = ('lesson__title',)
    list_editable = ('order',)
    ordering = ('lesson', 'order')

    def item_title(self, obj):
        return obj.item.title
    item_title.short_description = 'Item Title'

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at',)
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'file')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'file')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'url', 'file')
    search_fields = ('title', 'url')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'rating', 'comment', 'created_at')
    list_filter = ('course', 'rating')
    search_fields = ('course', 'rating')
    readonly_fields = ('created_at', 'updated_at')