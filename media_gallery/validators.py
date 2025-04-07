from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os
import mimetypes


def validate_image_quality(image):
    """
    Validate that the uploaded image meets minimum quality requirements.

    Args:
        image: The uploaded image file

    Raises:
        ValidationError: If image quality is insufficient
    """
    min_width, min_height = 800, 600  # Minimum dimensions

    try:
        img = Image.open(image)
        width, height = img.size

        if width < min_width or height < min_height:
            raise ValidationError(
                _(f'Image dimensions must be at least {min_width}x{min_height} pixels. '
                  f'Uploaded image is {width}x{height} pixels.')
            )

        # Check file size (max 10MB)
        if image.size > 10 * 1024 * 1024:
            raise ValidationError(_('Image file too large. Maximum size is 10MB.'))

    except Exception as e:
        raise ValidationError(_('Invalid image file. Please upload a valid image.'))


def validate_video_quality(video):
    """
    Validate that the uploaded video meets minimum quality requirements.

    Args:
        video: The uploaded video file

    Raises:
        ValidationError: If video quality is insufficient
    """
    # Check file size (max 100MB)
    if video.size > 100 * 1024 * 1024:
        raise ValidationError(_('Video file too large. Maximum size is 100MB.'))

    # Check file type
    file_name = video.name.lower()
    mime_type, _ = mimetypes.guess_type(file_name)

    if not mime_type or not mime_type.startswith('video/'):
        raise ValidationError(_('Invalid video format. Supported formats: MP4, WebM.'))

    valid_types = ['video/mp4', 'video/webm']
    if mime_type not in valid_types:
        raise ValidationError(_(f'Unsupported video format: {mime_type}. Supported formats: MP4, WebM.'))


def validate_media_url(url):
    """
    Validate that the provided URL points to a valid media resource.

    Args:
        url: The media URL

    Raises:
        ValidationError: If URL is invalid or inaccessible
    """
    import requests
    from urllib.parse import urlparse

    # Basic URL validation
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValidationError(_('Please provide a valid URL.'))

    # Check if the URL is accessible
    try:
        response = requests.head(url, timeout=5)
        if response.status_code != 200:
            raise ValidationError(_(f'The URL returned error code: {response.status_code}'))

        # Check content type
        content_type = response.headers.get('content-type', '')
        if not (content_type.startswith('image/') or content_type.startswith('video/')):
            raise ValidationError(_(f'URL does not point to valid media: {content_type}'))

    except requests.RequestException:
        raise ValidationError(_('Could not access the provided URL. Please check the URL and try again.'))
