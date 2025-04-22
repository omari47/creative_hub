from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _


class ThemePreference(models.Model):
    """
    Model to store available theme options.

    Each theme has a name and associated CSS file path.
    The is_default flag determines which theme is used for new users.
    """
    name = models.CharField(_('Theme Name'), max_length=100)
    css_file = models.CharField(_('CSS File Path'), max_length=255)
    is_default = models.BooleanField(_('Default Theme'), default=False)

    class Meta:
        verbose_name = _('Theme Preference')
        verbose_name_plural = _('Theme Preferences')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Ensure only one default theme exists."""
        if self.is_default:
            # Set all other themes as non-default
            ThemePreference.objects.filter(is_default=True).update(is_default=False)
        # If no default theme exists, make this one default
        elif not ThemePreference.objects.filter(is_default=True).exists():
            self.is_default = True

        super().save(*args, **kwargs)


class Profile(models.Model):
    """
    Extended user profile model.

    Stores additional user information and preferences beyond the Django User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('Biography'), blank=True)
    avatar = models.ImageField(
        _('Profile Picture'),
        upload_to='avatars/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    theme = models.ForeignKey(
        ThemePreference,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        verbose_name=_('Theme Preference')
    )

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        """Set default theme if none specified."""
        if not self.theme:
            self.theme = ThemePreference.objects.filter(is_default=True).first()
        super().save(*args, **kwargs)
