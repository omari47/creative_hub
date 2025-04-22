from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

from .models import FeaturedMovie, Purchase
from workshops.models import Workshop, Registration


class FeaturedMovieModelTest(TestCase):
    """Tests for the FeaturedMovie model."""

    def test_featured_movie_creation(self):
        """Test creating a featured movie."""
        movie = FeaturedMovie.objects.create(
            title='Test Movie',
            description='Test Description',
            price=9.99,
            video_url='https://example.com/movie.mp4',
            is_active=True
        )

        self.assertEqual(str(movie), 'Test Movie')
        self.assertEqual(movie.price, 9.99)
        self.assertTrue(movie.is_active)


class PurchaseModelTest(TestCase):
    """Tests for the Purchase model."""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test movie
        self.movie = FeaturedMovie.objects.create(
            title='Test Movie',
            description='Test Description',
            price=9.99,
            video_url='https://example.com/movie.mp4',
            is_active=True
        )

        # Create test workshop
        self.workshop = Workshop.objects.create(
            title='Test Workshop',
            description='Test Description',
            instructor='Test Instructor',
            date=timezone.now() + timedelta(days=30),
            location='Test Location',
            price=49.99,
            max_participants=10
        )

        # Create test registration
        self.registration = Registration.objects.create(
            user=self.user,
            workshop=self.workshop,
            status='pending',
            payment_status='unpaid'
        )

    def test_movie_purchase_creation(self):
        """Test creating a movie purchase."""
        purchase = Purchase.objects.create(
            user=self.user,
            movie=self.movie,
            amount=self.movie.price,
            payment_status='completed',
            payment_id='test_payment_id',
            payment_method='card'
        )

        self.assertEqual(str(purchase), f'testuser - Test Movie')
        self.assertEqual(purchase.amount, 9.99)
        self.assertEqual(purchase.payment_status, 'completed')

    def test_workshop_purchase_creation(self):
        """Test creating a workshop purchase."""
        purchase = Purchase.objects.create(
            user=self.user,
            workshop_registration=self.registration,
            amount=self.workshop.price,
            payment_status='completed',
            payment_id='test_payment_id',
            payment_method='card'
        )

        self.assertEqual(str(purchase), f'testuser - Test Workshop Workshop')
        self.assertEqual(purchase.amount, 49.99)
        self.assertEqual(purchase.payment_status, 'completed')

        # Check that registration status was updated
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.payment_status, 'paid')
        self.assertEqual(self.registration.status, 'confirmed')


class FeaturedMovieViewTest(TestCase):
    """Tests for featured movie views."""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test movies
        self.movie1 = FeaturedMovie.objects.create(
            title='Movie 1',
            description='First movie',
            price=9.99,
            video_url='https://example.com/movie1.mp4',
            is_active=True
        )

        self.movie2 = FeaturedMovie.objects.create(
            title='Movie 2',
            description='Second movie',
            price=14.99,
            video_url='https://example.com/movie2.mp4',
            is_active=True
        )

        # Create a purchase for movie1
        self.purchase = Purchase.objects.create(
            user=self.user,
            movie=self.movie1,
            amount=self.movie1.price,
            payment_status='completed',
            payment_id='test_payment_id',
            payment_method='card'
        )

    def test_featured_movies_view(self):
        """Test the featured movies list view."""
        response = self.client.get(reverse('payments:featured_movies'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Movie 1')
        self.assertContains(response, 'Movie 2')
        self.assertEqual(len(response.context['movies']), 2)

    def test_movie_detail_view(self):
        """Test the movie detail view."""
        response = self.client.get(reverse(
            'payments:movie_detail',
            kwargs={'pk': self.movie1.pk}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Movie 1')
        self.assertContains(response, 'First movie')

        # Login to check purchased status
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse(
            'payments:movie_detail',
            kwargs={'pk': self.movie1.pk}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_purchased'])

    def test_watch_movie_requires_purchase(self):
        """Test that watching a movie requires purchase."""
        # Login first
        self.client.login(username='testuser', password='testpass123')

        # Try to watch movie1 (purchased)
        response = self.client.get(reverse(
            'payments:watch_movie',
            kwargs={'pk': self.movie1.pk}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Movie 1')

        # Try to watch movie2 (not purchased)
        response = self.client.get(reverse(
            'payments:watch_movie',
            kwargs={'pk': self.movie2.pk}
        ))
        self.assertEqual(response.status_code, 302)  # Redirects to purchase page
