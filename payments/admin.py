from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FeaturedMovie, Purchase, MovieCategory, MovieTrailer, MPesaPayment


@admin.register(MovieCategory)
class MovieCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for movie categories."""
    list_display = ('name', 'slug', 'movie_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def movie_count(self, obj):
        """Count the number of movies in this category."""
        return obj.movies.count()

    movie_count.short_description = 'Movies'


@admin.register(MovieTrailer)
class MovieTrailerAdmin(admin.ModelAdmin):
    """Admin configuration for movie trailers."""
    list_display = ('title', 'is_upcoming', 'release_date', 'created_at')
    list_filter = ('is_upcoming', 'release_date', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Trailer Information', {
            'fields': ('title', 'description', 'trailer_url')
        }),
        ('Media', {
            'fields': ('thumbnail',)
        }),
        ('Release Details', {
            'fields': ('is_upcoming', 'release_date', 'created_at')
        }),
    )


@admin.register(FeaturedMovie)
class FeaturedMovieAdmin(admin.ModelAdmin):
    """Admin configuration for featured movies."""
    list_display = ('title', 'price', 'release_year', 'is_featured', 'is_active', 'purchase_count', 'created_at')
    list_filter = ('is_active', 'is_featured', 'categories', 'release_year', 'created_at')
    search_fields = ('title', 'description', 'director', 'cast')
    readonly_fields = ('created_at', 'view_count')
    filter_horizontal = ('categories',)

    fieldsets = (
        ('Movie Information', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Detailed Information', {
            'fields': ('director', 'cast', 'duration_minutes', 'release_year', 'rating', 'language')
        }),
        ('Categorization', {
            'fields': ('categories', 'trailer')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Media', {
            'fields': ('video_file', 'video_url', 'thumbnail', 'banner_image')
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_active', 'view_count', 'created_at')
        }),
    )

    def purchase_count(self, obj):
        """Count the number of purchases for this movie."""
        return obj.purchases.count()

    purchase_count.short_description = 'Purchases'


@admin.register(MPesaPayment)
class MPesaPaymentAdmin(admin.ModelAdmin):
    """Admin configuration for M-Pesa payments."""
    list_display = ('phone_number', 'amount', 'transaction_status', 'mpesa_receipt_number', 'transaction_date')
    list_filter = ('transaction_status', 'transaction_date')
    search_fields = ('phone_number', 'transaction_id', 'mpesa_receipt_number')
    readonly_fields = ('transaction_date',)

    fieldsets = (
        ('Payment Information', {
            'fields': ('phone_number', 'amount', 'transaction_status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'mpesa_receipt_number', 'transaction_date')
        }),
        ('API Response', {
            'fields': ('result_code', 'result_description')
        }),
    )


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin configuration for purchases."""
    list_display = ('user', 'content_title', 'amount', 'payment_method', 'payment_status', 'purchased_at')
    list_filter = ('payment_status', 'payment_method', 'purchased_at')
    search_fields = ('user__username', 'user__email', 'movie__title')
    readonly_fields = ('purchased_at', 'payment_id')

    fieldsets = (
        ('Purchase Information', {
            'fields': ('user', 'movie', 'workshop_registration', 'amount')
        }),
        ('Payment Details', {
            'fields': ('payment_status', 'payment_method', 'payment_id', 'mpesa_payment', 'purchased_at')
        }),
    )

    def content_title(self, obj):
        """Return the title of the purchased content."""
        if obj.movie:
            return obj.movie.title
        elif obj.workshop_registration:
            return obj.workshop_registration.workshop.title
        return 'Unknown'

    content_title.short_description = 'Content'
