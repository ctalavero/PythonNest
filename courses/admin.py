from django.contrib import admin
from .models import Course, Module, Lesson, Content, Text, File, Image, Video



class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    show_change_link = True

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    show_change_link = True

class ContentInline(admin.StackedInline):
    model = Content
    extra = 1
    show_change_link = True

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'rating')
    list_filter = ('created_at', 'tags')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('user',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('created_by', 'title', 'slug', 'description', 'tags', 'user', 'passage_time', 'rating')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    inlines = [LessonInline]



@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'passage_time')
    list_filter = ('module',)
    search_fields = ('title',)
    inlines = [ContentInline]


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'content_type', 'object_id', 'order')
    list_filter = ('lesson', 'content_type')
    search_fields = ('lesson__title',)

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
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