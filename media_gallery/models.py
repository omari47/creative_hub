from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, URLValidator
from .validators import validate_image_quality, validate_video_quality


class MediaCategory(models.Model):
    """
    Categories for organizing media content.

    Allows for grouping media items into logical collections.
    """
    name = models.CharField(_('Category Name'), max_length=100, unique=True)
    slug = models.SlugField(_('URL Slug'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Media Category')
        verbose_name_plural = _('Media Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the URL for this category."""
        return reverse('media_gallery:category', kwargs={'slug': self.slug})


class MediaItem(models.Model):
    """
    Media content items (photos, videos, events).

    Stores various types of media with metadata and categorization.
    """
    MEDIA_CHOICES = (
        ('photo', _('Photo')),
        ('video', _('Video')),
        ('event', _('Event')),
    )

    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    media_type = models.CharField(_('Media Type'), max_length=50, choices=MEDIA_CHOICES)
    category = models.ForeignKey(
        MediaCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
        verbose_name=_('Category')
    )

    # Media can either be uploaded as a file or provided as a URL
    file = models.FileField(
        _('Media File'),
        upload_to='gallery/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm'])]
    )
    media_url = models.URLField(_('Media URL'), max_length=500, blank=True, validators=[URLValidator()])

    # Thumbnail for videos or events
    thumbnail = models.ImageField(
        _('Thumbnail'),
        upload_to='thumbnails/',
        null=True,
        blank=True,
        validators=[validate_image_quality]
    )

    # Additional metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_featured = models.BooleanField(_('Featured'), default=False)

    class Meta:
        verbose_name = _('Media Item')
        verbose_name_plural = _('Media Items')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return the URL for this media item."""
        return reverse('media_gallery:detail', kwargs={'pk': self.pk})

    def clean(self):
        """Validate either file or URL is provided, and run quality checks."""
        from django.core.exceptions import ValidationError

        # Ensure at least one of file or media_url is provided
        if not self.file and not self.media_url:
            raise ValidationError(_('Either a file or URL must be provided.'))

        # Validate media quality based on type
        if self.file:
            if self.media_type == 'photo':
                validate_image_quality(self.file)
            elif self.media_type == 'video':
                validate_video_quality(self.file)

        # Events should have a thumbnail
        if self.media_type == 'event' and not self.thumbnail:
            raise ValidationError(_('Events must have a thumbnail image.'))
