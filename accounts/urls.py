from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/purchases/', views.purchase_history, name='purchase_history'),
    path('profile/workshops/', views.workshop_history, name='workshop_history'),
    path('switch-theme/<int:theme_id>/', views.switch_theme, name='switch_theme'),
]
