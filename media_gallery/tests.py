from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os

from .models import MediaItem, MediaCategory


class MediaCategoryModelTest(TestCase):
    """Tests for the MediaCategory model."""

    def test_category_creation(self):
        """Test creating a category generates a slug automatically."""
        category = MediaCategory.objects.create(
            name='Nature Photography',
            description='Beautiful nature photos'
        )
        self.assertEqual(category.slug, 'nature-photography')
        self.assertEqual(str(category), 'Nature Photography')


class MediaItemModelTest(TestCase):
    """Tests for the MediaItem model."""

    def setUp(self):
        self.category = MediaCategory.objects.create(
            name='Test Category',
            description='Test Description'
        )

        # Create a test image file
        test_image_path = os.path.join(settings.STATIC_ROOT, 'test_image.jpg')
        with open(test_image_path, 'wb') as f:
            f.write(b'fake image content')

        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(test_image_path, 'rb').read(),
            content_type='image/jpeg'
        )

    def test_media_item_creation(self):
        """Test creating a media item."""
        media_item = MediaItem.objects.create(
            title='Test Item',
            description='Test Description',
            media_type='photo',
            category=self.category,
            file=self.test_image,
            is_featured=True
        )

        self.assertEqual(str(media_item), 'Test Item')
        self.assertEqual(media_item.media_type, 'photo')
        self.assertTrue(media_item.is_featured)


class GalleryViewTest(TestCase):
    """Tests for gallery views."""

    def setUp(self):
        self.category = MediaCategory.objects.create(
            name='Test Category',
            description='Test Description'
        )

        # Create test media items
        for i in range(5):
            MediaItem.objects.create(
                title=f'Test Item {i}',
                description=f'Description {i}',
                media_type='photo' if i % 2 == 0 else 'video',
                category=self.category,
                media_url=f'https://example.com/media/{i}.jpg',
                is_featured=(i == 0)  # First item is featured
            )

    def test_gallery_view(self):
        """Test the main gallery view."""
        response = self.client.get(reverse('media_gallery:gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['media_items']), 5)
        self.assertEqual(len(response.context['featured']), 1)
        self.assertTrue('categories' in response.context)

    def test_category_view(self):
        """Test the category view."""
        response = self.client.get(
            reverse('media_gallery:category',
                    kwargs={'slug': self.category.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'], self.category)
        self.assertEqual(len(response.context['media_items']), 5)

    def test_media_type_view(self):
        """Test filtering by media type."""
        response = self.client.get(
            reverse('media_gallery:media_type',
                    kwargs={'media_type': 'photo'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['media_items']), 3)  # 3 photos
