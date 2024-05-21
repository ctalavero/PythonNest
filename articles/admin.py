from django.contrib import admin
from django.utils.html import format_html

from .models import Article, Content
from courses.admin import TextAdmin, VideoAdmin, ImageAdmin, FileAdmin

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_logo', 'published', 'author', 'created_at')
    list_filter = ('created_at', 'tags')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'display_logo', 'updated_at')
    list_editable = ('published',)
    fieldsets = (
        (None, {
            'fields': ('author', 'title', 'slug', 'logo', 'display_logo', 'tags', 'published')
        }),
        ('Timestamps', {
            'fields': ('created_at','updated_at'),
        }),
    )
    def display_logo(self, obj):
        return format_html('<img src="{}" height="50" />', obj.logo.url)
    display_logo.short_description = 'Logo'

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('item_title', 'content_type', 'object_id', 'order')
    list_filter = ('article', 'content_type')
    search_fields = ('article__title',)
    list_editable = ('order',)
    ordering = ('article', 'order')

    def item_title(self, obj):
        return obj.item.title
    item_title.short_description = 'Item Title'
