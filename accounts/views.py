from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Profile, ThemePreference
from .forms import ProfileUpdateForm
from payments.models import Purchase
from workshops.models import WorkshopRegistration


@login_required
def profile_view(request):
    """Display user profile with personalized information."""
    purchases = Purchase.objects.filter(user=request.user).order_by('-purchased_at')[:5]
    workshops = WorkshopRegistration.objects.filter(user=request.user).order_by('-registered_at')[:5]

    context = {
        'profile': request.user.profile,
        'recent_purchases': purchases,
        'recent_workshops': workshops,
        'available_themes': ThemePreference.objects.all(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile information."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def purchase_history(request):
    """View all user purchases."""
    purchases = Purchase.objects.filter(user=request.user).order_by('-purchased_at')
    return render(request, 'accounts/purchase_history.html', {'purchases': purchases})


@login_required
def workshop_history(request):
    """View all user workshop registrations."""
    workshops = WorkshopRegistration.objects.filter(user=request.user).order_by('-registered_at')
    return render(request, 'accounts/workshop_history.html', {'workshops': workshops})


@login_required
def switch_theme(request, theme_id):
    """Switch user theme preference."""
    if request.method == 'POST':
        theme = get_object_or_404(ThemePreference, id=theme_id)
        profile = request.user.profile
        profile.theme = theme
        profile.save()
        messages.success(request, f'Theme switched to {theme.name}')

    # Redirect back to the referring page, or profile page if not available
    next_url = request.POST.get('next', reverse('accounts:profile'))
    return HttpResponseRedirect(next_url)
