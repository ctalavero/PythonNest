from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','display_photo', 'date_of_birth', ]
    raw_id_fields = ['user']
    readonly_fields = ['display_photo']

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="50" />', obj.photo.url)
        return "No photo"
    display_photo.short_description = 'Photo'

    fieldsets = (
        (None, {
            'fields': ('user', 'date_of_birth', 'photo', 'display_photo', 'about')
        }),
    )

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    show_change_link = True
    extra = 1

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)