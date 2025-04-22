from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Profile, ThemePreference


class ThemePreferenceModelTest(TestCase):
    """Tests for the ThemePreference model."""

    def test_default_theme_uniqueness(self):
        """Test that only one theme can be the default."""
        theme1 = ThemePreference.objects.create(name='Dark', css_file='dark.css', is_default=True)
        theme2 = ThemePreference.objects.create(name='Light', css_file='light.css', is_default=True)

        # Refresh theme1 from database
        theme1.refresh_from_db()

        # Now theme1 should no longer be default
        self.assertFalse(theme1.is_default)
        self.assertTrue(theme2.is_default)


class ProfileModelTest(TestCase):
    """Tests for the Profile model."""

    def setUp(self):
        self.default_theme = ThemePreference.objects.create(
            name='Default',
            css_file='default.css',
            is_default=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_creation(self):
        """Test that a profile is created for a new user."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.theme, self.default_theme)


class ProfileViewTest(TestCase):
    """Tests for profile views."""

    def setUp(self):
        self.default_theme = ThemePreference.objects.create(
            name='Default',
            css_file='default.css',
            is_default=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_view_requires_login(self):
        """Test that the profile view requires login."""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirects to login

        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
