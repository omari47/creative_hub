from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Movie listings and categories
    path('featured/', views.featured_movies, name='featured_movies'),
    path('movies/', views.movie_list, name='movie_list'),
    path('category/<slug:slug>/', views.category_movies, name='category_movies'),
    path('trailers/', views.trailers_list, name='trailers_list'),

    # Movie detail and watching
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('watch/<int:pk>/', views.watch_movie, name='watch_movie'),

    # Payment routes
    path('purchase/movie/<int:pk>/', views.purchase_movie, name='purchase_movie'),
    path('purchase/workshop/<int:registration_id>/', views.workshop_payment, name='workshop_payment'),

    # M-Pesa specific routes
    path('mpesa/initiate/<int:purchase_id>/', views.mpesa_payment_initiate, name='mpesa_payment_initiate'),
    path('mpesa/callback/<int:purchase_id>/', views.mpesa_payment_callback, name='mpesa_payment_callback'),
    path('mpesa/status/<int:purchase_id>/', views.mpesa_payment_status, name='mpesa_payment_status'),

    # Checkout routes
    path('checkout/success/', views.payment_success, name='payment_success'),
    path('checkout/cancel/', views.payment_cancel, name='payment_cancel'),

    # Webhooks for payment providers
    path('webhook/', views.payment_webhook, name='payment_webhook'),
]
