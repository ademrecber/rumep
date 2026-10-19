"""Validate publisher images; retain the original file without recompression."""
from io import BytesIO
from uuid import uuid4
from django.core.files.base import ContentFile
from PIL import Image
from .wallpaper_images import prepare_wallpaper


def prepare_post(upload):
    # Reuse file type, animation, byte and decoded-pixel safety validation.
    _, preview, width, height = prepare_wallpaper(upload)
    upload.seek(0)
    raw = upload.read()
    with Image.open(BytesIO(raw)) as image:
        extension = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}[image.format]
    return ContentFile(raw, name=f'{uuid4().hex}.{extension}'), preview, width, height
