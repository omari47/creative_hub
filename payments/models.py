from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.urls import reverse
from workshops.models import WorkshopRegistration
from media_gallery.validators import validate_video_quality, validate_image_quality


class MovieCategory(models.Model):
    """
    Categories for organizing featured movies.

    Allows for grouping movies into genres and categories.
    """
    name = models.CharField(_('Category Name'), max_length=100, unique=True)
    slug = models.SlugField(_('URL Slug'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Movie Category')
        verbose_name_plural = _('Movie Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the URL for this category."""
        return reverse('payments:category_movies', kwargs={'slug': self.slug})


class MovieTrailer(models.Model):
    """
    Trailers for featured movies.

    Stores trailer information including title, URL and thumbnail.
    """
    title = models.CharField(_('Trailer Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    trailer_url = models.URLField(_('Trailer URL'), max_length=500)
    thumbnail = models.ImageField(
        _('Thumbnail'),
        upload_to='trailer_thumbnails/',
        validators=[validate_image_quality]
    )
    is_upcoming = models.BooleanField(_('Upcoming Release'), default=False)
    release_date = models.DateField(_('Release Date'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Movie Trailer')
        verbose_name_plural = _('Movie Trailers')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FeaturedMovie(models.Model):
    """
    Featured premium movies that require payment to access.

    This model stores information about premium movies including title,
    description, price, and the actual video file.
    """
    RATING_CHOICES = (
        ('G', _('G - General Audiences')),
        ('PG', _('PG - Parental Guidance Suggested')),
        ('PG-13', _('PG-13 - Parents Strongly Cautioned')),
        ('R', _('R - Restricted')),
        ('NC-17', _('NC-17 - Adults Only')),
    )

    title = models.CharField(_('Movie Title'), max_length=200)
    subtitle = models.CharField(_('Subtitle/Tagline'), max_length=255, blank=True)
    description = models.TextField(_('Description'))

    # Detailed information
    director = models.CharField(_('Director'), max_length=200, blank=True)
    cast = models.TextField(_('Cast'), blank=True, help_text=_('Enter actor names separated by commas'))
    duration_minutes = models.PositiveIntegerField(_('Duration (minutes)'), null=True, blank=True)
    release_year = models.PositiveIntegerField(_('Release Year'), null=True, blank=True)
    rating = models.CharField(_('Rating'), max_length=10, choices=RATING_CHOICES, blank=True)
    language = models.CharField(_('Language'), max_length=100, blank=True)

    # Categorization
    categories = models.ManyToManyField(
        MovieCategory,
        related_name='movies',
        verbose_name=_('Categories')
    )

    # Trailer
    trailer = models.ForeignKey(
        MovieTrailer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_movie',
        verbose_name=_('Trailer')
    )

    # Pricing
    price = models.DecimalField(
        _('Price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  # Ensure price is positive
    )
    discount_price = models.DecimalField(
        _('Discount Price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)]
    )

    # Media can be provided as a file or a URL
    video_file = models.FileField(
        _('Video File'),
        upload_to='movies/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'webm']),
            validate_video_quality
        ]
    )
    video_url = models.URLField(_('Video URL'), max_length=500, blank=True)

    # Thumbnail image
    thumbnail = models.ImageField(
        _('Thumbnail'),
        upload_to='movie_thumbnails/',
        null=True,
        blank=True,
        validators=[validate_image_quality]
    )

    # Featured banner image - for hero sections
    banner_image = models.ImageField(
        _('Banner Image'),
        upload_to='movie_banners/',
        null=True,
        blank=True,
        validators=[validate_image_quality],
        help_text=_('Large widescreen image for featured content sections')
    )

    # Metadata
    is_featured = models.BooleanField(_('Featured'), default=True, help_text=_('Show in featured section on homepage'))
    is_active = models.BooleanField(_('Active'), default=True)
    view_count = models.PositiveIntegerField(_('View Count'), default=0)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Featured Movie')
        verbose_name_plural = _('Featured Movies')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return the URL for this movie."""
        return reverse('payments:movie_detail', kwargs={'pk': self.pk})

    def clean(self):
        """Validate that either file or URL is provided."""
        from django.core.exceptions import ValidationError

        if not self.video_file and not self.video_url:
            raise ValidationError(_('Either a video file or URL must be provided.'))

        if not self.thumbnail:
            raise ValidationError(_('A thumbnail image is required.'))


class MPesaPayment(models.Model):
    """
    M-Pesa specific payment details

    This model stores the specific details related to M-Pesa payments.
    """
    TRANSACTION_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    )

    phone_number = models.CharField(_('Phone Number'), max_length=20)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    transaction_id = models.CharField(_('Transaction ID'), max_length=100, blank=True)
    transaction_status = models.CharField(
        _('Transaction Status'),
        max_length=20,
        choices=TRANSACTION_STATUS_CHOICES,
        default='pending'
    )
    mpesa_receipt_number = models.CharField(_('M-Pesa Receipt Number'), max_length=50, blank=True)
    transaction_date = models.DateTimeField(_('Transaction Date'), auto_now_add=True)

    # Response from M-Pesa API
    result_code = models.CharField(_('Result Code'), max_length=10, blank=True)
    result_description = models.CharField(_('Result Description'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('M-Pesa Payment')
        verbose_name_plural = _('M-Pesa Payments')
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.phone_number} - {self.amount} - {self.transaction_status}"


class Purchase(models.Model):
    """
    Record of purchases made by users for premium content.

    This model tracks all payments including both movie purchases
    and workshop registrations.
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )

    PAYMENT_METHOD_CHOICES = (
        ('mpesa', _('M-Pesa')),
        ('card', _('Credit Card')),
        ('bank', _('Bank Transfer')),
        ('other', _('Other')),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name=_('User')
    )

    # A purchase can be for a movie or a workshop registration (but not both)
    movie = models.ForeignKey(
        FeaturedMovie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases',
        verbose_name=_('Movie')
    )
    workshop_registration = models.ForeignKey(
        WorkshopRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase',
        verbose_name=_('Workshop Registration')
    )

    # Payment details
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        _('Payment Status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_id = models.CharField(_('Payment ID'), max_length=100, blank=True)
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='mpesa'
    )

    # Link to M-Pesa transaction if applicable
    mpesa_payment = models.ForeignKey(
        MPesaPayment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases',
        verbose_name=_('M-Pesa Payment')
    )

    purchased_at = models.DateTimeField(_('Purchased At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Purchase')
        verbose_name_plural = _('Purchases')
        ordering = ['-purchased_at']

    def __str__(self):
        if self.movie:
            return f"{self.user.username} - {self.movie.title}"
        elif self.workshop_registration:
            return f"{self.user.username} - {self.workshop_registration.workshop.title} Workshop"
        return f"{self.user.username} - {self.amount}"

    def clean(self):
        """Validate that either movie or workshop_registration is provided, but not both."""
        from django.core.exceptions import ValidationError

        if self.movie and self.workshop_registration:
            raise ValidationError(_('A purchase can be for either a movie or a workshop, not both.'))

        if not self.movie and not self.workshop_registration:
            raise ValidationError(_('A purchase must be associated with either a movie or a workshop.'))

    def save(self, *args, **kwargs):
        """Update related workshop registration status when purchase status changes."""
        # If this purchase is for a workshop registration
        if self.workshop_registration:
            # Update registration payment status based on purchase status
            if self.payment_status == 'completed':
                self.workshop_registration.payment_status = 'paid'
                self.workshop_registration.status = 'confirmed'
            elif self.payment_status == 'pending':
                self.workshop_registration.payment_status = 'pending'
            elif self.payment_status == 'failed':
                self.workshop_registration.payment_status = 'unpaid'
            elif self.payment_status == 'refunded':
                self.workshop_registration.payment_status = 'refunded'
                self.workshop_registration.status = 'cancelled'

            self.workshop_registration.save()

        super().save(*args, **kwargs)
