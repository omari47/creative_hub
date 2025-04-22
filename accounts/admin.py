from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, ThemePreference


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for user profiles."""
    list_display = ('user', 'get_theme_name', 'date_joined')
    search_fields = ('user__username', 'user__email')
    list_filter = ('theme__name',)

    def get_theme_name(self, obj):
        return obj.theme.name if obj.theme else 'Default'

    get_theme_name.short_description = 'Theme'

    def date_joined(self, obj):
        return obj.user.date_joined

    date_joined.short_description = 'Date Joined'


@admin.register(ThemePreference)
class ThemePreferenceAdmin(admin.ModelAdmin):
    """Admin configuration for theme preferences."""
    list_display = ('name', 'css_file', 'is_default')
    search_fields = ('name',)
    list_filter = ('is_default',)
