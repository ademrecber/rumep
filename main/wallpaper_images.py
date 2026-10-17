"""Validate and re-encode publisher uploads; never publish raw file contents."""
from io import BytesIO
from uuid import uuid4
import warnings

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 12 * 1024 * 1024
MAX_PIXELS = 25_000_000


def prepare_wallpaper(upload):
    if upload.size > MAX_BYTES:
        raise ValidationError('Görsel en fazla 12 MB olabilir.')
    upload.seek(0)
    raw = upload.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValidationError('Görsel en fazla 12 MB olabilir.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as image:
                if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                    raise ValidationError('Yalnızca JPEG, PNG veya WebP yükleyebilirsin.')
                width, height = image.size
                if min(width, height) < 320 or width * height > MAX_PIXELS:
                    raise ValidationError('Görsel en az 320×320, en fazla 25 megapiksel olmalı.')
                if getattr(image, 'is_animated', False):
                    raise ValidationError('Hareketli görsel yerine sabit bir duvar kağıdı yükle.')
                image.load()
                image = ImageOps.exif_transpose(image)
                mode = 'RGBA' if 'A' in image.getbands() else 'RGB'
                # A fresh pixel-only image drops EXIF, text chunks and file trailers.
                clean = Image.new(mode, image.size)
                clean.paste(image.convert(mode))
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValidationError('Görsel açılamadı veya güvenli boyut sınırını aşıyor.') from None
    width, height = clean.size
    output = BytesIO()
    transparent = clean.mode == 'RGBA'
    clean.save(output, format='PNG' if transparent else 'JPEG', **({} if transparent else {'quality': 94}))
    if output.tell() > MAX_BYTES:
        raise ValidationError('İşlenmiş görsel 12 MB sınırını aşıyor; görseli küçültüp tekrar yükle.')
    preview = clean.copy()
    preview.thumbnail((480, 800))
    thumb = BytesIO()
    preview.save(thumb, format='PNG' if transparent else 'JPEG', **({} if transparent else {'quality': 82}))
    stem = uuid4().hex
    ext = 'png' if transparent else 'jpg'
    return (
        ContentFile(output.getvalue(), name=f'{stem}.{ext}'),
        ContentFile(thumb.getvalue(), name=f'{stem}-preview.{ext}'),
        width, height,
    )
