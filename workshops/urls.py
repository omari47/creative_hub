from django.urls import path
from . import views

app_name = 'workshops'

urlpatterns = [
    path('', views.workshop_list, name='list'),
    path('my-workshops/', views.my_workshops, name='my_workshops'),
    path('<int:pk>/', views.workshop_detail, name='detail'),
    path('<int:pk>/register/', views.workshop_register, name='register'),
    path('registration/<int:pk>/cancel/', views.workshop_cancel_registration, name='cancel_registration'),
    path('category/<slug:slug>/', views.category_workshops, name='category'),
]