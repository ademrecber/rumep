from django.test import TestCase, override_settings
from django.utils import timezone
from .models import SportPost, Wallpaper


@override_settings(SECURE_SSL_REDIRECT=False)
class ContentNotificationTests(TestCase):
    def test_explicit_published_content_only_and_edit_does_not_resend(self):
        p = SportPost.objects.create(image='cover.jpg', width=800, height=1000, is_published=True)
        self.assertEqual(self.client.get('/api/content-notifications/').json()['items'], [])
        p.notify_users = True
        p.description = 'Yeni paylaşım açıklaması'
        p.save()
        stamp = p.notification_requested_at
        data = self.client.get('/api/content-notifications/').json()['items']
        self.assertEqual(data[0]['body'], p.description)
        self.assertEqual(data[0]['id'], f'content:post:{p.pk}')
        p.description = 'Düzenlendi'
        p.save()
        self.assertEqual(p.notification_requested_at, stamp)
        p.is_published = False
        p.save()
        self.assertEqual(self.client.get('/api/content-notifications/').json()['items'], [])
        self.assertEqual(self.client.get(f'/api/spor-feed/?post={p.pk}').json()['items'], [])

    def test_wallpaper_text_and_stable_preview(self):
        p = Wallpaper.objects.create(title='Sur', image='sur.jpg', is_published=True, notify_users=True)
        data = self.client.get('/api/content-notifications/').json()['items'][0]
        self.assertEqual(data['contentType'], 'wallpaper')
        self.assertIn('Yeni duvar', data['title'])
        self.assertEqual(self.client.get(data['imageUrl']).status_code, 302)
        self.assertEqual(self.client.get(f'/api/wallpapers/{p.pk}/').json()['title'], 'Sur')
