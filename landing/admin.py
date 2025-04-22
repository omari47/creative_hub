from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin configuration for contact messages."""
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('created_at', 'is_read')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message', 'is_read')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
