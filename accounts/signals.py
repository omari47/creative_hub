from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, ThemePreference


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance when a new User is created."""
    if created:
        # Get default theme or first theme if no default
        default_theme = ThemePreference.objects.filter(is_default=True).first()
        if not default_theme:
            default_theme = ThemePreference.objects.first()

        # Create profile with default theme
        Profile.objects.create(user=instance, theme=default_theme)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile is saved when user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
