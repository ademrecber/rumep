from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Wallpaper
from .wallpaper_images import MAX_BYTES, prepare_wallpaper


def upload():
    output = BytesIO()
    Image.new('RGB', (720, 1280), '#223344').save(output, 'JPEG')
    return SimpleUploadedFile('wallpaper.jpg', output.getvalue() + b'<script>unsafe trailer</script>', content_type='image/jpeg')


@override_settings(SECURE_SSL_REDIRECT=False, WALLPAPER_UPLOADS_ENABLED=True)
class WallpaperAdminTests(TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.storage_override = override_settings(MEDIA_ROOT=self.folder.name)
        self.storage_override.enable()
        self.addCleanup(self.storage_override.disable)
        self.admin = get_user_model().objects.create_superuser(username='offline-admin', password='test-only-password')
        self.add_url = reverse('admin:main_wallpaper_add')

    def test_old_admin_route_is_gone_and_new_route_requires_login(self):
        self.assertEqual(self.client.get('/admin/').status_code, 404)
        self.assertEqual(reverse('admin:index'), '/rumep-studyo/')
        self.assertEqual(self.client.get(self.add_url).status_code, 302)
        self.assertEqual(self.client.get(reverse('admin:login')).status_code, 200)

    def test_upload_normalizes_image_and_builds_permission_protected_preview(self):
        self.client.force_login(self.admin)
        result = self.client.post(self.add_url, {'title': 'Amedspor', 'description': 'Tribün duvar kağıdı', 'image': upload(), '_save': 'Kaydet'})
        self.assertEqual(result.status_code, 302)
        item = Wallpaper.objects.get()
        self.assertFalse(item.is_published)
        self.assertEqual((item.width, item.height), (720, 1280))
        with item.image.open('rb') as image:
            data = image.read()
        self.assertNotIn(b'<script>', data)
        self.assertEqual(item.file_size, len(data))
        self.assertTrue(Path(item.thumbnail.path).exists())
        url = reverse('wallpaper_admin_preview', args=[item.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response['Cache-Control'])
        response.close()
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)
        staff = get_user_model().objects.create_user(username='no-permission', is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_invalid_and_unconfigured_uploads_do_not_create_records(self):
        self.client.force_login(self.admin)
        result = self.client.post(self.add_url, {'title': 'Invalid', 'image': SimpleUploadedFile('fake.png', b'not an image', content_type='image/png')})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(Wallpaper.objects.count(), 0)
        with self.settings(WALLPAPER_UPLOADS_ENABLED=False):
            result = self.client.post(self.add_url, {'title': 'Disabled', 'image': upload()})
            self.assertEqual(result.status_code, 200)
            self.assertContains(result, 'Kalıcı görsel depolaması henüz bağlanmadı')
        self.assertEqual(Wallpaper.objects.count(), 0)

    def test_publish_and_metadata_edit_preserve_original(self):
        item = Wallpaper.objects.create(title='Original', image=upload(), is_published=True)
        name, published = item.image.name, item.published_at
        self.assertIsNotNone(published)
        item.title = 'Updated'
        item.save()
        item.refresh_from_db()
        self.assertEqual(item.image.name, name)
        self.assertEqual(item.published_at, published)

    def test_oversize_rejected_before_reading(self):
        with self.assertRaises(ValidationError):
            prepare_wallpaper(SimpleNamespace(size=MAX_BYTES + 1))
