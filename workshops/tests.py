from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import Workshop, Registration


class WorkshopModelTest(TestCase):
    """Tests for the Workshop model."""

    def test_workshop_creation(self):
        """Test creating a workshop."""
        future_date = timezone.now() + timedelta(days=30)
        workshop = Workshop.objects.create(
            title='Test Workshop',
            description='Test Description',
            instructor='Test Instructor',
            date=future_date,
            duration=120,
            location='Test Location',
            price=99.99,
            max_participants=10
        )

        self.assertEqual(str(workshop), 'Test Workshop')
        self.assertEqual(workshop.spots_left, 10)
        self.assertFalse(workshop.is_past)
        self.assertFalse(workshop.is_full)
        self.assertEqual(workshop.end_time, future_date + timedelta(minutes=120))


class RegistrationModelTest(TestCase):
    """Tests for the Registration model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.future_workshop = Workshop.objects.create(
            title='Future Workshop',
            description='Test Description',
            instructor='Test Instructor',
            date=timezone.now() + timedelta(days=30),
            duration=120,
            location='Test Location',
            price=99.99,
            max_participants=10
        )

        self.past_workshop = Workshop.objects.create(
            title='Past Workshop',
            description='Test Description',
            instructor='Test Instructor',
            date=timezone.now() - timedelta(days=30),
            duration=120,
            location='Test Location',
            price=99.99,
            max_participants=10
        )

    def test_registration_creation(self):
        """Test creating a workshop registration."""
        registration = Registration.objects.create(
            user=self.user,
            workshop=self.future_workshop,
            status='confirmed',
            payment_status='paid'
        )

        self.assertEqual(str(registration), f'testuser - Future Workshop')
        self.assertEqual(registration.status, 'confirmed')
        self.assertEqual(registration.payment_status, 'paid')

    def test_registration_status_sync(self):
        """Test payment status synchronizes with registration status."""
        registration = Registration.objects.create(
            user=self.user,
            workshop=self.future_workshop,
            status='pending',
            payment_status='unpaid'
        )

        # Update payment status to paid
        registration.payment_status = 'paid'
        registration.save()

        # Registration status should be auto-updated to confirmed
        registration.refresh_from_db()
        self.assertEqual(registration.status, 'confirmed')

        # Set registration to cancelled
        registration.status = 'cancelled'
        registration.save()

        # Payment status should be updated to refunded
        registration.refresh_from_db()
        self.assertEqual(registration.payment_status, 'refunded')


class WorkshopViewTest(TestCase):
    """Tests for workshop views."""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test workshops
        self.workshop1 = Workshop.objects.create(
            title='Workshop 1',
            description='First workshop',
            instructor='Instructor 1',
            date=timezone.now() + timedelta(days=30),
            duration=120,
            location='Location 1',
            price=49.99,
            max_participants=5
        )

        self.workshop2 = Workshop.objects.create(
            title='Workshop 2',
            description='Second workshop',
            instructor='Instructor 2',
            date=timezone.now() + timedelta(days=60),
            duration=240,
            location='Location 2',
            price=99.99,
            max_participants=10
        )

    def test_workshop_list_view(self):
        """Test the workshop list view."""
        response = self.client.get(reverse('workshops:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workshop 1')
        self.assertContains(response, 'Workshop 2')
        self.assertEqual(len(response.context['workshops']), 2)

    def test_workshop_detail_view(self):
        """Test the workshop detail view."""
        response = self.client.get(reverse(
            'workshops:detail',
            kwargs={'pk': self.workshop1.pk}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workshop 1')
        self.assertContains(response, 'First workshop')
        self.assertContains(response, 'Instructor 1')

    def test_workshop_registration_requires_login(self):
        """Test that registration requires login."""
        response = self.client.get(reverse(
            'workshops:register',
            kwargs={'pk': self.workshop1.pk}
        ))
        self.assertEqual(response.status_code, 302)  # Redirects to login

        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse(
            'workshops:register',
            kwargs={'pk': self.workshop1.pk}
        ))
        self.assertEqual(response.status_code, 200)
