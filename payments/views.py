from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
import stripe
import json
import requests
import uuid

from .models import (
    FeaturedMovie, Purchase, MovieCategory,
    MovieTrailer, MPesaPayment
)
from workshops.models import WorkshopRegistration


def featured_movies(request):
    """
    Display all available featured movies.
    """
    movies = FeaturedMovie.objects.filter(is_active=True)

    context = {
        'movies': movies,
    }

    return render(request, 'payments/featured_movies.html', context)


def movie_detail(request, pk):
    """
    Display details about a featured movie.
    """
    movie = get_object_or_404(FeaturedMovie, pk=pk, is_active=True)

    # Check if user has already purchased this movie
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = Purchase.objects.filter(
            user=request.user,
            movie=movie,
            payment_status='completed'
        ).exists()

    # Get related movies
    related_movies = FeaturedMovie.objects.filter(
        is_active=True
    ).exclude(pk=pk)[:3]

    context = {
        'movie': movie,
        'has_purchased': has_purchased,
        'related_movies': related_movies,
    }

    return render(request, 'payments/movie_detail.html', context)


@login_required
def watch_movie(request, pk):
    """
    Allow users who have purchased the movie to watch it.
    """
    movie = get_object_or_404(FeaturedMovie, pk=pk, is_active=True)

    # Check if the user has purchased the movie
    has_purchased = Purchase.objects.filter(
        user=request.user,
        movie=movie,
        payment_status='completed'
    ).exists()

    if not has_purchased:
        messages.error(request, 'You need to purchase this movie before you can watch it.')
        return redirect('payments:movie_detail', pk=movie.pk)

    context = {
        'movie': movie,
    }

    return render(request, 'payments/movie_player.html', context)


@login_required
def purchase_movie(request, pk):
    """
    Handle movie purchase process.
    """
    movie = get_object_or_404(FeaturedMovie, pk=pk, is_active=True)

    # Check if user has already purchased this movie
    has_purchased = Purchase.objects.filter(
        user=request.user,
        movie=movie,
        payment_status='completed'
    ).exists()

    if has_purchased:
        messages.info(request, 'You have already purchased this movie.')
        return redirect('payments:watch_movie', pk=movie.pk)

    if request.method == 'POST':
        # Get payment method from request data if provided
        try:
            data = json.loads(request.body)
            payment_method = data.get('payment_method', 'card')
        except:
            payment_method = 'card'

        # If payment method is M-Pesa, create a pending purchase and return the ID
        if payment_method == 'mpesa':
            purchase = Purchase.objects.create(
                user=request.user,
                movie=movie,
                amount=movie.price,
                payment_status='pending',
                payment_method='mpesa'
            )
            return JsonResponse({'purchase_id': purchase.id})

        # Otherwise, default to Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        success_url = request.build_absolute_uri(reverse('payments:payment_success'))
        cancel_url = request.build_absolute_uri(reverse('payments:payment_cancel'))

        # Create a Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': movie.title,
                                'description': movie.description[:255],  # Stripe limits description length
                            },
                            'unit_amount': int(movie.price * 100),  # Convert to cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url + f'?session_id={{CHECKOUT_SESSION_ID}}&type=movie&id={movie.pk}',
                cancel_url=cancel_url,
                client_reference_id=str(request.user.id),
                metadata={
                    'type': 'movie',
                    'movie_id': str(movie.pk),
                    'user_id': str(request.user.id),
                }
            )

            # Create a pending purchase record
            purchase = Purchase.objects.create(
                user=request.user,
                movie=movie,
                amount=movie.price,
                payment_status='pending',
                payment_method='card',
                payment_id=checkout_session.id
            )

            # Redirect to Stripe Checkout
            return JsonResponse({'id': checkout_session.id})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    context = {
        'movie': movie,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, 'payments/purchase_prompt.html', context)


@login_required
def workshop_payment(request, registration_id):
    """
    Handle payment for workshop registration.
    """
    registration = get_object_or_404(
        WorkshopRegistration,
        pk=registration_id,
        user=request.user
    )

    # Ensure the workshop has a price and payment is needed
    if registration.workshop.price <= 0:
        messages.info(request, 'This workshop is free, no payment required.')
        return redirect('workshops:detail', pk=registration.workshop.pk)

    # Check if already paid
    if registration.payment_status == 'paid':
        messages.info(request, 'You have already paid for this workshop.')
        return redirect('workshops:detail', pk=registration.workshop.pk)

    if request.method == 'POST':
        # Get payment method from request data if provided
        try:
            data = json.loads(request.body)
            payment_method = data.get('payment_method', 'card')
        except:
            payment_method = 'card'

        # If payment method is M-Pesa, create a pending purchase and return the ID
        if payment_method == 'mpesa':
            purchase = Purchase.objects.create(
                user=request.user,
                workshop_registration=registration,
                amount=registration.workshop.price,
                payment_status='pending',
                payment_method='mpesa'
            )

            # Update registration status
            registration.payment_status = 'pending'
            registration.save()

            return JsonResponse({'purchase_id': purchase.id})

        # Initialize Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        success_url = request.build_absolute_uri(reverse('payments:payment_success'))
        cancel_url = request.build_absolute_uri(reverse('payments:payment_cancel'))

        # Create a Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f"Workshop: {registration.workshop.title}",
                                'description': registration.workshop.description[:255],
                            },
                            'unit_amount': int(registration.workshop.price * 100),  # Convert to cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url + f'?session_id={{CHECKOUT_SESSION_ID}}&type=workshop&id={registration.pk}',
                cancel_url=cancel_url,
                client_reference_id=str(request.user.id),
                metadata={
                    'type': 'workshop',
                    'registration_id': str(registration.pk),
                    'user_id': str(request.user.id),
                }
            )

            # Create a pending purchase record
            purchase = Purchase.objects.create(
                user=request.user,
                workshop_registration=registration,
                amount=registration.workshop.price,
                payment_status='pending',
                payment_method='card',
                payment_id=checkout_session.id
            )

            # Update registration status
            registration.payment_status = 'pending'
            registration.save()

            # Redirect to Stripe Checkout
            return JsonResponse({'id': checkout_session.id})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    context = {
        'registration': registration,
        'workshop': registration.workshop,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, 'payments/workshop_payment.html', context)


def payment_success(request):
    """
    Handle successful payment callback.
    """
    session_id = request.GET.get('session_id')
    payment_type = request.GET.get('type')
    item_id = request.GET.get('id')

    if not session_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('landing:home')

    # Find the purchase by session ID
    try:
        purchase = Purchase.objects.get(payment_id=session_id)

        # If payment was already processed, just redirect
        if purchase.payment_status == 'completed':
            messages.success(request, 'Payment was successful!')

            if purchase.movie:
                return redirect('payments:watch_movie', pk=purchase.movie.pk)
            elif purchase.workshop_registration:
                return redirect('workshops:detail', pk=purchase.workshop_registration.workshop.pk)
            return redirect('accounts:profile')

        # Otherwise, verify with Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == 'paid':
            # Update purchase record
            purchase.payment_status = 'completed'
            purchase.payment_method = 'card'  # From Stripe Checkout
            purchase.save()

            messages.success(request, 'Your payment was successful!')

            if purchase.movie:
                return redirect('payments:watch_movie', pk=purchase.movie.pk)
            elif purchase.workshop_registration:
                return redirect('workshops:detail', pk=purchase.workshop_registration.workshop.pk)
        else:
            messages.warning(request, 'Payment is still being processed. Please check back later.')

    except Purchase.DoesNotExist:
        messages.error(request, 'Could not find your purchase record.')
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')

    return redirect('accounts:profile')


def payment_cancel(request):
    """
    Handle cancelled payment.
    """
    messages.warning(request, 'Your payment was cancelled.')
    return redirect('landing:home')


def movie_list(request):
    """
    Display all movies with filtering options.
    """
    movies = FeaturedMovie.objects.filter(is_active=True)
    categories = MovieCategory.objects.all()

    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        try:
            category = MovieCategory.objects.get(id=category_id)
            movies = movies.filter(categories=category)
        except MovieCategory.DoesNotExist:
            pass

    # Filter by search term if specified
    search_query = request.GET.get('search')
    if search_query:
        movies = movies.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(director__icontains=search_query) |
            Q(cast__icontains=search_query)
        )

    # Sort options
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        movies = movies.order_by('price')
    elif sort_by == 'price_high':
        movies = movies.order_by('-price')
    elif sort_by == 'title':
        movies = movies.order_by('title')
    else:  # default to newest
        movies = movies.order_by('-created_at')

    context = {
        'movies': movies,
        'categories': categories,
        'active_category': category_id,
        'search_query': search_query,
        'sort_by': sort_by,
    }

    return render(request, 'payments/movie_list.html', context)


def category_movies(request, slug):
    """
    Display movies for a specific category.
    """
    category = get_object_or_404(MovieCategory, slug=slug)
    movies = FeaturedMovie.objects.filter(
        categories=category,
        is_active=True
    ).order_by('-created_at')

    context = {
        'category': category,
        'movies': movies,
    }

    return render(request, 'payments/category_movies.html', context)


def trailers_list(request):
    """
    Display all movie trailers with separate sections for current and upcoming.
    """
    current_trailers = MovieTrailer.objects.filter(
        is_upcoming=False
    ).order_by('-created_at')

    upcoming_trailers = MovieTrailer.objects.filter(
        is_upcoming=True
    ).order_by('release_date')

    context = {
        'current_trailers': current_trailers,
        'upcoming_trailers': upcoming_trailers,
    }

    return render(request, 'payments/trailers_list.html', context)


@login_required
def mpesa_payment_initiate(request, purchase_id):
    """
    Initiate an M-Pesa payment for a purchase.
    """
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
        user=request.user,
        payment_status='pending'
    )

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        if not phone_number:
            messages.error(request, 'Please provide a valid phone number.')
            if purchase.movie:
                return redirect('payments:movie_detail', pk=purchase.movie.pk)
            else:
                return redirect('workshops:detail', pk=purchase.workshop_registration.workshop.pk)

        # Strip any non-numeric characters and ensure it starts with country code
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if not phone_number.startswith('254'):
            if phone_number.startswith('0'):
                # Convert Kenyan format (07xx) to international format (254xxx)
                phone_number = '254' + phone_number[1:]
            else:
                # Add country code if not present
                phone_number = '254' + phone_number

        # Create M-Pesa payment record
        mpesa_payment = MPesaPayment.objects.create(
            phone_number=phone_number,
            amount=purchase.amount,
            transaction_status='pending'
        )

        # Link to purchase
        purchase.mpesa_payment = mpesa_payment
        purchase.payment_method = 'mpesa'
        purchase.save()

        # In a real implementation, this would make an API call to the M-Pesa API
        # For demonstration, we're simulating a successful payment

        # Simulate M-Pesa API response
        mpesa_payment.transaction_id = f"MPE{uuid.uuid4().hex[:8].upper()}"
        mpesa_payment.mpesa_receipt_number = f"LKP{uuid.uuid4().hex[:8].upper()}"
        mpesa_payment.transaction_status = 'completed'
        mpesa_payment.result_code = '0'
        mpesa_payment.result_description = 'Success'
        mpesa_payment.save()

        # Update purchase status
        purchase.payment_status = 'completed'
        purchase.save()

        # Update workshop registration status if applicable
        if purchase.workshop_registration:
            purchase.workshop_registration.payment_status = 'paid'
            purchase.workshop_registration.status = 'confirmed'
            purchase.workshop_registration.save()

        messages.success(request, 'Your M-Pesa payment was successful!')

        # Redirect based on what was purchased
        if purchase.movie:
            return redirect('payments:watch_movie', pk=purchase.movie.pk)
        else:
            return redirect('workshops:detail', pk=purchase.workshop_registration.workshop.pk)

    # GET request - show payment form
    context = {
        'purchase': purchase,
    }

    # Different templates based on what's being purchased
    if purchase.movie:
        context['movie'] = purchase.movie
        return render(request, 'payments/mpesa_movie_payment.html', context)
    else:
        context['workshop'] = purchase.workshop_registration.workshop
        return render(request, 'payments/mpesa_workshop_payment.html', context)


@csrf_exempt
def mpesa_payment_callback(request, purchase_id):
    """
    Callback endpoint for M-Pesa payment confirmation.

    This would be called by the M-Pesa API to confirm payment status.
    """
    if request.method != 'POST':
        return HttpResponseForbidden()

    try:
        # Parse the callback data
        callback_data = json.loads(request.body)

        # In a real implementation, validate the callback data
        # and update the payment status accordingly

        # For demonstration, we're assuming the callback indicates success
        purchase = Purchase.objects.get(pk=purchase_id)

        if purchase.mpesa_payment:
            # Update the M-Pesa payment record
            mpesa_payment = purchase.mpesa_payment
            mpesa_payment.transaction_status = 'completed'
            mpesa_payment.mpesa_receipt_number = callback_data.get('receipt_number', '')
            mpesa_payment.result_code = '0'
            mpesa_payment.result_description = 'Success'
            mpesa_payment.save()

        # Update the purchase status
        purchase.payment_status = 'completed'
        purchase.save()

        # Update workshop registration if applicable
        if purchase.workshop_registration:
            purchase.workshop_registration.payment_status = 'paid'
            purchase.workshop_registration.status = 'confirmed'
            purchase.workshop_registration.save()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def mpesa_payment_status(request, purchase_id):
    """
    Check the status of an M-Pesa payment.
    """
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
        user=request.user
    )

    if not purchase.mpesa_payment:
        messages.error(request, 'No M-Pesa payment found for this purchase.')
        return redirect('accounts:profile')

    # In a real implementation, this would make an API call to check the payment status
    # For demonstration, we're just returning the current status

    context = {
        'purchase': purchase,
        'mpesa_payment': purchase.mpesa_payment,
    }

    return render(request, 'payments/mpesa_status.html', context)


@csrf_exempt
@require_POST
def payment_webhook(request):
    """
    Handle Stripe webhook events for payment status updates.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'checkout.session.completed':
        session = event.data.object

        # Find the purchase by payment ID
        try:
            purchase = Purchase.objects.get(payment_id=session.id)

            # Update purchase status
            purchase.payment_status = 'completed'
            purchase.save()

        except Purchase.DoesNotExist:
            # If purchase record doesn't exist, we need to create one
            if session.metadata and 'type' in session.metadata:
                user_id = int(session.metadata.get('user_id'))

                if session.metadata['type'] == 'movie':
                    movie_id = int(session.metadata.get('movie_id'))
                    movie = FeaturedMovie.objects.get(pk=movie_id)
                    user = User.objects.get(pk=user_id)

                    Purchase.objects.create(
                        user=user,
                        movie=movie,
                        amount=session.amount_total / 100,  # Convert cents to dollars
                        payment_status='completed',
                        payment_id=session.id,
                        payment_method='card'
                    )

                elif session.metadata['type'] == 'workshop':
                    registration_id = int(session.metadata.get('registration_id'))
                    registration = WorkshopRegistration.objects.get(pk=registration_id)
                    user = User.objects.get(pk=user_id)

                    Purchase.objects.create(
                        user=user,
                        workshop_registration=registration,
                        amount=session.amount_total / 100,  # Convert cents to dollars
                        payment_status='completed',
                        payment_id=session.id,
                        payment_method='card'
                    )

    return HttpResponse(status=200)
