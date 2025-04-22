from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """
    Model to store contact form messages from visitors.

    Used for the contact form on the landing page.
    """
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('Email'))
    subject = models.CharField(_('Subject'), max_length=200)
    message = models.TextField(_('Message'))
    is_read = models.BooleanField(_('Read'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
