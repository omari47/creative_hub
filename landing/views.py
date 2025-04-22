from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q

from .models import ContactMessage
from media_gallery.models import MediaItem
from workshops.models import Workshop
from payments.models import FeaturedMovie


def home(request):
    """
    Landing page view.

    Displays a visually appealing homepage with featured content.
    """
    # Get featured content for the carousel
    featured_photos = MediaItem.objects.filter(
        media_type='photo',
        is_featured=True
    )[:6]

    featured_videos = MediaItem.objects.filter(
        media_type='video',
        is_featured=True
    )[:3]

    # Get upcoming workshops
    from django.utils import timezone
    upcoming_workshops = Workshop.objects.filter(
        is_published=True,
        start_date__gt=timezone.now().date()
    ).order_by('start_date')[:3]

    # Get featured movies
    featured_movies = FeaturedMovie.objects.filter(
        is_active=True
    )[:3]

    context = {
        'featured_photos': featured_photos,
        'featured_videos': featured_videos,
        'upcoming_workshops': upcoming_workshops,
        'featured_movies': featured_movies,
    }

    return render(request, 'landing/home.html', context)


def about(request):
    """About page view."""
    return render(request, 'landing/about.html')


def contact(request):
    """
    Contact page with form submission handling.
    """
    if request.method == 'POST':
        # Process contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Basic validation
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all fields.')
        else:
            # Save message to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('landing:contact')

    return render(request, 'landing/contact.html')


def testimonials(request):
    """Testimonials page view."""
    return render(request, 'landing/testimonials.html')


def privacy_policy(request):
    """Privacy policy page."""
    return render(request, 'landing/privacy_policy.html')


def terms_of_service(request):
    """Terms of service page."""
    return render(request, 'landing/terms_of_service.html')
