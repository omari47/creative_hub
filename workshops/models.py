from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, time, date


class WorkshopCategory(models.Model):
    """Categories for organizing workshops."""
    name = models.CharField(_('Category Name'), max_length=100, unique=True)
    slug = models.SlugField(_('URL Slug'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Workshop Category')
        verbose_name_plural = _('Workshop Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Return the URL for this category."""
        return reverse('workshops:category', kwargs={'slug': self.slug})


class Workshop(models.Model):
    """Workshop model for storing workshops information."""
    LOCATION_CHOICES = (
        ('online', _('Online')),
        ('in_person', _('In Person')),
        ('hybrid', _('Hybrid (Online & In Person)')),
    )

    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    category = models.ForeignKey(
        WorkshopCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workshops',
        verbose_name=_('Category')
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='instructed_workshops',
        verbose_name=_('Instructor')
    )

    start_date = models.DateField(_('Start Date'), default=timezone.now)
    start_time = models.TimeField(_('Start Time'), default=time(9, 0, 0))  # Default 9:00 AM
    duration = models.DecimalField(
        _('Duration (hours)'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.5)],
        default=2.0
    )

    price = models.DecimalField(
        _('Price'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    capacity = models.PositiveIntegerField(_('Capacity'), default=15)

    location_type = models.CharField(
        _('Location Type'),
        max_length=20,
        choices=LOCATION_CHOICES,
        default='online'
    )
    location_address = models.CharField(_('Location Address'), max_length=255, blank=True)
    location_url = models.URLField(_('Location URL'), blank=True, help_text=_('Zoom/Meet link for online workshops'))

    image = models.ImageField(
        _('Cover Image'),
        upload_to='workshops/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )

    requirements = models.TextField(_('Requirements'), blank=True, help_text=_('Equipment, prerequisites, etc.'))
    agenda = models.TextField(_('Workshop Agenda'), blank=True)
    provides_certificate = models.BooleanField(_('Provides Certificate'), default=False)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    is_published = models.BooleanField(_('Published'), default=True)
    is_featured = models.BooleanField(_('Featured'), default=False)

    class Meta:
        verbose_name = _('Workshop')
        verbose_name_plural = _('Workshops')
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return the URL for this workshop."""
        return reverse('workshops:detail', kwargs={'pk': self.pk})

    @property
    def end_time(self):
        """Calculate the end time based on duration."""
        hours = int(self.duration)
        minutes = int((self.duration - hours) * 60)
        start_datetime = timezone.datetime.combine(
            timezone.datetime.today(),
            self.start_time
        )
        end_datetime = start_datetime + timedelta(hours=hours, minutes=minutes)
        return end_datetime.time()

    @property
    def is_completed(self):
        """Check if the workshop has already been completed."""
        workshop_date = timezone.datetime.combine(
            self.start_date,
            self.end_time
        )
        return timezone.now() > workshop_date

    @property
    def is_ongoing(self):
        """Check if the workshop is currently ongoing."""
        now = timezone.now()
        workshop_start = timezone.datetime.combine(
            self.start_date,
            self.start_time
        )
        workshop_end = timezone.datetime.combine(
            self.start_date,
            self.end_time
        )
        return workshop_start <= now <= workshop_end

    @property
    def available_spots(self):
        """Calculate remaining available spots."""
        return self.capacity - self.registrations.count()

    @property
    def is_full(self):
        """Check if the workshop is at full capacity."""
        return self.available_spots <= 0


class WorkshopRegistration(models.Model):
    """Model for workshop registrations."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
    )

    PAYMENT_STATUS_CHOICES = (
        ('unpaid', _('Unpaid')),
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('refunded', _('Refunded')),
    )

    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name=_('Workshop')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workshop_registrations',
        verbose_name=_('User')
    )
    registered_at = models.DateTimeField(_('Registered At'), auto_now_add=True)

    # Status fields
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        _('Payment Status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )
    payment_complete = models.BooleanField(_('Payment Complete'), default=False)
    is_cancelled = models.BooleanField(_('Cancelled'), default=False)
    attendance_confirmed = models.BooleanField(_('Attendance Confirmed'), default=False)

    class Meta:
        verbose_name = _('Workshop Registration')
        verbose_name_plural = _('Workshop Registrations')
        unique_together = ('workshop', 'user')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.user.username} - {self.workshop.title}"

    def save(self, *args, **kwargs):
        """Update payment_complete based on payment_status."""
        if self.payment_status == 'paid':
            self.payment_complete = True
        else:
            self.payment_complete = False

        if self.is_cancelled and self.status != 'cancelled':
            self.status = 'cancelled'

        super().save(*args, **kwargs)