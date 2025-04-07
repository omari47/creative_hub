from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os


def validate_avatar_dimensions(image):
    """
    Validate that the uploaded avatar meets minimum dimensions.

    Args:
        image: The uploaded image file

    Raises:
        ValidationError: If image dimensions are too small
    """
    min_width, min_height = 200, 200

    try:
        img = Image.open(image)
        width, height = img.size

        if width < min_width or height < min_height:
            raise ValidationError(
                _(f'Image dimensions must be at least {min_width}x{min_height} pixels. '
                  f'Uploaded image is {width}x{height} pixels.')
            )
    except Exception as e:
        raise ValidationError(_('Invalid image file. Please upload a valid image.'))


def validate_avatar_size(image):
    """
    Validate that the uploaded avatar meets size limits.

    Args:
        image: The uploaded image file

    Raises:
        ValidationError: If image size exceeds 2MB
    """
    max_size = 2 * 1024 * 1024  # 2MB

    if image.size > max_size:
        raise ValidationError(
            _('Image file too large. Maximum size is 2MB.')
        )
