from io import BytesIO
from tempfile import TemporaryDirectory
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from .models import SportPost, SportPostImage


@override_settings(SECURE_SSL_REDIRECT=False)
class FeedTests(TestCase):
    def test_gallery_orders_extra_images_and_checks_publication(self):
        p = SportPost.objects.create(image='cover.jpg', width=800, height=1000, is_published=True)
        second = SportPostImage.objects.create(post=p, image='second.jpg', position=2, width=800, height=1000)
        first = SportPostImage.objects.create(post=p, image='first.jpg', position=1, width=1000, height=800)
        data = self.client.get('/api/spor-feed/').json()['items'][0]
        self.assertEqual(len(data['images']), 2)
        self.assertIn(f'/images/{first.pk}/', data['images'][0]['imageUrl'])
        self.assertIn(f'/images/{second.pk}/', data['images'][1]['imageUrl'])
        self.assertEqual(self.client.get(data['images'][0]['imageUrl']).status_code, 302)
        p.is_published = False
        p.save()
        self.assertEqual(self.client.get(data['images'][0]['imageUrl']).status_code, 404)

    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        setting = override_settings(MEDIA_ROOT=self.folder.name)
        setting.enable()
        self.addCleanup(setting.disable)

    def test_original_bytes_preserved_and_preview_created(self):
        data = BytesIO()
        Image.new('RGB', (800, 1200), '#283931').save(data, 'JPEG', quality=98)
        original = data.getvalue()
        p = SportPost.objects.create(image=SimpleUploadedFile('test.jpg', original), is_published=True)
        with p.image.open('rb') as f:
            self.assertEqual(f.read(), original)
        self.assertTrue(p.thumbnail.storage.exists(p.thumbnail.name))
        self.assertEqual((p.width, p.height), (800, 1200))
        result = self.client.get('/api/spor-feed/').json()['items'][0]
        self.assertNotIn('title', result)
        self.assertNotIn('X-Amz', result['imageUrl'])
        self.assertEqual(self.client.get(result['imageUrl']).status_code, 302)
        with self.captureOnCommitCallbacks(execute=True):
            p.delete()
        self.assertFalse(p.image.storage.exists(p.image.name))

    def test_pagination_drafts_anchor_and_deleted_visibility(self):
        SportPost.objects.bulk_create([SportPost(image='test.jpg', is_published=True, published_at=timezone.now()) for _ in range(23)])
        draft = SportPost.objects.create(image='secret.jpg')
        self.assertEqual(self.client.get(f'/api/spor-feed/{draft.pk}/original/').status_code, 404)
        first = self.client.get('/api/spor-feed/').json()
        SportPost.objects.create(image='new.jpg', is_published=True)
        second = self.client.get(f'/api/spor-feed/?page=2&before={first["before"]}').json()
        self.assertEqual(len(first['items']), 10)
        self.assertEqual(len(second['items']), 10)
        self.assertFalse(set(p['id'] for p in first['items']) & set(p['id'] for p in second['items']))
        self.assertEqual(self.client.get('/api/spor-feed/?page=-1').status_code, 400)
        self.assertEqual(self.client.post('/api/spor-feed/').status_code, 405)
