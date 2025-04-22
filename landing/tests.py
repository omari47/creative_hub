from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import ContactMessage
from media_gallery.models import MediaItem, MediaCategory
from workshops.models import Workshop
from payments.models import FeaturedMovie


class LandingPageViewTest(TestCase):
    """Tests for landing page views."""

    def setUp(self):
        # Create test data for landing page
        # Media category
        self.category = MediaCategory.objects.create(
            name='Test Category'
        )

        # Featured photos
        for i in range(3):
            MediaItem.objects.create(
                title=f'Photo {i}',
                description=f'Photo description {i}',
                media_type='photo',
                category=self.category,
                media_url=f'https://example.com/photo{i}.jpg',
                is_featured=True
            )

        # Featured videos
        for i in range(2):
            MediaItem.objects.create(
                title=f'Video {i}',
                description=f'Video description {i}',
                media_type='video',
                category=self.category,
                media_url=f'https://example.com/video{i}.mp4',
                is_featured=True
            )

        # Upcoming workshops
        for i in range(3):
            Workshop.objects.create(
                title=f'Workshop {i}',
                description=f'Workshop description {i}',
                instructor=f'Instructor {i}',
                date=timezone.now() + timedelta(days=i + 1),
                location=f'Location {i}',
                price=49.99 + i * 10,
                is_active=True
            )

        # Featured movies
        for i in range(2):
            FeaturedMovie.objects.create(
                title=f'Movie {i}',
                description=f'Movie description {i}',
                price=9.99 + i * 5,
                video_url=f'https://example.com/movie{i}.mp4',
                is_active=True
            )

    def test_home_view(self):
        """Test the home page view."""
        response = self.client.get(reverse('landing:home'))
        self.assertEqual(response.status_code, 200)

        # Check that featured content is displayed
        self.assertEqual(len(response.context['featured_photos']), 3)
        self.assertEqual(len(response.context['featured_videos']), 2)
        self.assertEqual(len(response.context['upcoming_workshops']), 3)
        self.assertEqual(len(response.context['featured_movies']), 2)

    def test_contact_form(self):
        """Test contact form submission."""
        # Before submission, no contact messages
        self.assertEqual(ContactMessage.objects.count(), 0)

        # Submit the form
        response = self.client.post(reverse('landing:contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test Message Content'
        })

        # Check redirect after successful submission
        self.assertEqual(response.status_code, 302)

        # Check that a message was created
        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, 'Test User')
        self.assertEqual(message.email, 'test@example.com')
        self.assertEqual(message.subject, 'Test Subject')
        self.assertEqual(message.message, 'Test Message Content')
        self.assertFalse(message.is_read)

    def test_about_page(self):
        """Test the about page."""
        response = self.client.get(reverse('landing:about'))
        self.assertEqual(response.status_code, 200)
