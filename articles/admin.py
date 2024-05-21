from django.contrib import admin
from .models import Article, Content
from courses.admin import TextAdmin, VideoAdmin, ImageAdmin, FileAdmin

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

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
