from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import WorkshopCategory, Workshop, WorkshopRegistration


class WorkshopCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for workshop categories."""
    list_display = ('name', 'slug', 'workshop_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def workshop_count(self, obj):
        """Get the count of workshops in this category."""
        return obj.workshops.count()

    workshop_count.short_description = 'Number of Workshops'


class WorkshopAdmin(admin.ModelAdmin):
    """Admin configuration for workshops."""
    list_display = (
        'title', 'category', 'instructor', 'start_date',
        'price', 'capacity', 'available_spots', 'is_published', 'is_featured'
    )
    list_filter = ('is_published', 'is_featured', 'category', 'location_type', 'start_date')
    search_fields = ('title', 'description', 'instructor__username', 'instructor__email')
    date_hierarchy = 'start_date'
    autocomplete_fields = ['instructor', 'category']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'instructor')
        }),
        ('Schedule', {
            'fields': ('start_date', 'start_time', 'duration')
        }),
        ('Pricing & Capacity', {
            'fields': ('price', 'capacity')
        }),
        ('Location', {
            'fields': ('location_type', 'location_address', 'location_url')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Details', {
            'fields': ('requirements', 'agenda', 'provides_certificate')
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured')
        })
    )

    def available_spots(self, obj):
        """Calculate available spots left in the workshop."""
        return obj.available_spots

    available_spots.short_description = 'Available Spots'


class WorkshopRegistrationAdmin(admin.ModelAdmin):
    """Admin configuration for workshop registrations."""
    list_display = ('user', 'workshop', 'registered_at', 'payment_complete', 'is_cancelled')
    list_filter = ('payment_complete', 'is_cancelled', 'attendance_confirmed', 'registered_at')
    search_fields = ('user__username', 'user__email', 'workshop__title')
    date_hierarchy = 'registered_at'
    autocomplete_fields = ['user', 'workshop']

    fieldsets = (
        ('Registration Information', {
            'fields': ('workshop', 'user')
        }),
        ('Status', {
            'fields': ('payment_complete', 'is_cancelled', 'attendance_confirmed')
        })
    )

    readonly_fields = ('registered_at',)


# Register models with their admin classes
admin.site.register(WorkshopCategory, WorkshopCategoryAdmin)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(WorkshopRegistration, WorkshopRegistrationAdmin)