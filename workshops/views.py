from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import Workshop, WorkshopRegistration, WorkshopCategory


def workshop_list(request):
    """Display a list of available workshops."""
    # Get filters from query params
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search')
    filter_option = request.GET.get('filter', 'upcoming')

    # Start with all published workshops
    workshops = Workshop.objects.filter(is_published=True)

    # Apply category filter if specified
    if category_slug:
        workshops = workshops.filter(category__slug=category_slug)

    # Apply search if specified
    if search_query:
        workshops = workshops.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(instructor__username__icontains=search_query)
        )

    # Apply time-based filters
    today = timezone.now().date()
    if filter_option == 'upcoming':
        workshops = workshops.filter(start_date__gte=today)
    elif filter_option == 'past':
        workshops = workshops.filter(start_date__lt=today)
    elif filter_option == 'free':
        workshops = workshops.filter(price=0)

    # Get featured workshop
    featured_workshop = Workshop.objects.filter(
        is_published=True,
        is_featured=True,
        start_date__gte=today
    ).first()

    # Get categories for filter
    categories = WorkshopCategory.objects.all()

    context = {
        'workshops': workshops,
        'featured_workshop': featured_workshop,
        'categories': categories,
        'current_category': category_slug,
        'current_filter': filter_option,
        'search_query': search_query,
    }

    return render(request, 'workshops/list.html', context)


@login_required
def my_workshops(request):
    """Display workshops the user has registered for."""
    today = timezone.now().date()

    # Get user registrations
    registrations = WorkshopRegistration.objects.filter(user=request.user)

    # Split into upcoming and past
    upcoming_registrations = registrations.filter(
        workshop__start_date__gte=today
    ).order_by('workshop__start_date')

    past_registrations = registrations.filter(
        workshop__start_date__lt=today
    ).order_by('-workshop__start_date')

    context = {
        'registrations': registrations,
        'upcoming_registrations': upcoming_registrations,
        'past_registrations': past_registrations,
    }

    return render(request, 'workshops/my_workshops.html', context)


def workshop_detail(request, pk):
    """Display details of a specific workshop."""
    workshop = get_object_or_404(Workshop, pk=pk, is_published=True)

    # Check if user is already registered
    registration = None
    is_registered = False

    if request.user.is_authenticated:
        try:
            registration = WorkshopRegistration.objects.get(
                workshop=workshop,
                user=request.user
            )
            is_registered = True
        except WorkshopRegistration.DoesNotExist:
            pass

    # Get related workshops in same category
    related_workshops = []
    if workshop.category:
        related_workshops = Workshop.objects.filter(
            category=workshop.category,
            is_published=True
        ).exclude(id=workshop.id).order_by('-is_featured', '-start_date')[:3]

    # If no related workshops by category, get some other workshops
    if not related_workshops:
        related_workshops = Workshop.objects.filter(
            is_published=True
        ).exclude(id=workshop.id).order_by('-is_featured', '-start_date')[:3]

    context = {
        'workshop': workshop,
        'is_registered': is_registered,
        'registration': registration,
        'related_workshops': related_workshops,
    }

    return render(request, 'workshops/detail.html', context)


@login_required
def workshop_register(request, pk):
    """Register a user for a workshop."""
    workshop = get_object_or_404(Workshop, pk=pk, is_published=True)

    # Check if user is already registered
    if WorkshopRegistration.objects.filter(workshop=workshop, user=request.user).exists():
        messages.info(request, 'You are already registered for this workshop.')
        return redirect('workshops:detail', pk=workshop.pk)

    # Check if workshop is full
    if workshop.is_full:
        messages.error(request, 'This workshop is already at full capacity.')
        return redirect('workshops:detail', pk=workshop.pk)

    # Check if workshop date has passed
    if workshop.is_completed:
        messages.error(request, 'This workshop has already taken place.')
        return redirect('workshops:detail', pk=workshop.pk)

    # Create registration
    registration = WorkshopRegistration.objects.create(
        workshop=workshop,
        user=request.user,
        status='pending'
    )

    # If workshop is free, confirm the registration immediately
    if workshop.price <= 0:
        registration.payment_status = 'paid'
        registration.status = 'confirmed'
        registration.payment_complete = True
        registration.save()
        messages.success(request, 'You have successfully registered for this workshop!')
        return redirect('workshops:my_workshops')

    # If paid workshop, redirect to payment
    return redirect('payments:workshop_payment', registration_id=registration.pk)


@login_required
def workshop_cancel_registration(request, pk):
    """Cancel a workshop registration."""
    registration = get_object_or_404(WorkshopRegistration, pk=pk, user=request.user)

    # Don't allow cancellation of past workshops
    if registration.workshop.is_completed:
        messages.error(request, 'Cannot cancel a registration for a workshop that has already occurred.')
        return redirect('workshops:my_workshops')

    if request.method == 'POST':
        registration.is_cancelled = True
        registration.status = 'cancelled'
        registration.save()
        messages.success(request, 'Your registration has been cancelled.')
        return redirect('workshops:my_workshops')

    return render(request, 'workshops/cancel_confirmation.html', {'registration': registration})


def category_workshops(request, slug):
    """Show workshops for a specific category."""
    category = get_object_or_404(WorkshopCategory, slug=slug)

    # Get workshops in this category
    workshops = Workshop.objects.filter(
        category=category,
        is_published=True
    ).order_by('-is_featured', 'start_date')

    # Filter to upcoming workshops
    today = timezone.now().date()
    upcoming_workshops = workshops.filter(start_date__gte=today)

    context = {
        'category': category,
        'workshops': upcoming_workshops,
        'workshop_count': upcoming_workshops.count(),
    }

    return render(request, 'workshops/category.html', context)