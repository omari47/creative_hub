from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import MediaItem, MediaCategory


def gallery_view(request):
    """
    Main gallery view showing all media items with filtering options.
    """
    all_media = MediaItem.objects.all()
    featured = MediaItem.objects.filter(is_featured=True)[:6]
    categories = MediaCategory.objects.all()

    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        all_media = all_media.filter(category_id=category_id)

    # Filter by media type if specified
    media_type = request.GET.get('type')
    if media_type in ['photo', 'video', 'event']:
        all_media = all_media.filter(media_type=media_type)

    # Pagination
    paginator = Paginator(all_media, 12)  # Show 12 items per page
    page = request.GET.get('page')

    try:
        media_items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        media_items = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        media_items = paginator.page(paginator.num_pages)

    context = {
        'media_items': media_items,
        'featured': featured,
        'categories': categories,
        'current_category': category_id,
        'current_type': media_type,
    }

    return render(request, 'media_gallery/gallery.html', context)


def category_view(request, slug):
    """
    Display media items from a specific category.
    """
    category = get_object_or_404(MediaCategory, slug=slug)
    media_items = category.items.all()

    # Pagination
    paginator = Paginator(media_items, 12)
    page = request.GET.get('page')

    try:
        media_items = paginator.page(page)
    except PageNotAnInteger:
        media_items = paginator.page(1)
    except EmptyPage:
        media_items = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'media_items': media_items,
    }

    return render(request, 'media_gallery/category.html', context)


def media_detail(request, pk):
    """
    Display detailed view of a single media item.
    """
    media_item = get_object_or_404(MediaItem, pk=pk)

    # Get related items from the same category
    if media_item.category:
        related_items = MediaItem.objects.filter(
            category=media_item.category
        ).exclude(pk=pk)[:4]
    else:
        related_items = MediaItem.objects.filter(
            media_type=media_item.media_type
        ).exclude(pk=pk)[:4]

    context = {
        'media_item': media_item,
        'related_items': related_items,
    }

    return render(request, 'media_gallery/detail.html', context)


def media_type_view(request, media_type):
    """
    Display media items of a specific type (photo, video, event).
    """
    if media_type not in ['photo', 'video', 'event']:
        media_type = 'photo'  # Default to photos if invalid type

    media_items = MediaItem.objects.filter(media_type=media_type)

    # Pagination
    paginator = Paginator(media_items, 12)
    page = request.GET.get('page')

    try:
        media_items = paginator.page(page)
    except PageNotAnInteger:
        media_items = paginator.page(1)
    except EmptyPage:
        media_items = paginator.page(paginator.num_pages)

    context = {
        'media_type': media_type,
        'media_items': media_items,
    }

    return render(request, 'media_gallery/media_type.html', context)


def featured_gallery(request):
    """
    Display only featured media items.
    """
    featured_items = MediaItem.objects.filter(is_featured=True)

    # Pagination
    paginator = Paginator(featured_items, 12)
    page = request.GET.get('page')

    try:
        media_items = paginator.page(page)
    except PageNotAnInteger:
        media_items = paginator.page(1)
    except EmptyPage:
        media_items = paginator.page(paginator.num_pages)

    context = {
        'media_items': media_items,
        'is_featured': True,
    }

    return render(request, 'media_gallery/featured.html', context)


def search_media(request):
    """
    Search for media items based on user query.
    """
    query = request.GET.get('q', '')

    if query:
        results = MediaItem.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    else:
        results = MediaItem.objects.none()

    # Pagination
    paginator = Paginator(results, 12)
    page = request.GET.get('page')

    try:
        media_items = paginator.page(page)
    except PageNotAnInteger:
        media_items = paginator.page(1)
    except EmptyPage:
        media_items = paginator.page(paginator.num_pages)

    context = {
        'query': query,
        'media_items': media_items,
        'total_results': results.count(),
    }

    return render(request, 'media_gallery/search.html', context)
