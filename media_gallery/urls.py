from django.urls import path
from . import views

app_name = 'media_gallery'

urlpatterns = [
    path('', views.gallery_view, name='gallery'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('detail/<int:pk>/', views.media_detail, name='detail'),
    path('type/<str:media_type>/', views.media_type_view, name='media_type'),
    path('featured/', views.featured_gallery, name='featured'),
    path('search/', views.search_media, name='search'),
]
