from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import MediaItem, MediaCategory


class MediaItemAdmin(admin.ModelAdmin):
    """Admin configuration for media items."""
    list_display = ('title', 'media_type', 'category', 'created_at', 'is_featured')
    list_filter = ('media_type', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Content Information', {
            'fields': ('title', 'description', 'category', 'is_featured')
        }),
        ('Media', {
            'fields': ('media_type', 'file', 'thumbnail', 'media_url')
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('created_at',),
        }),
    )

    readonly_fields = ('created_at',)


admin.site.register(MediaItem, MediaItemAdmin)


class MediaCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for media categories."""
    list_display = ('name', 'slug', 'item_count')
    prepopulated_fields = {'slug': ('name',)}

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = 'Number of Items'


admin.site.register(MediaCategory, MediaCategoryAdmin)
