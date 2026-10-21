from django.test import TestCase, override_settings
from django.utils import timezone
from .models import SportPost, Wallpaper
from unittest.mock import patch, MagicMock


@override_settings(SECURE_SSL_REDIRECT=False)
class ContentNotificationTests(TestCase):
    def test_hook_runs_only_after_commit_and_only_on_first_publish(self):
        with patch('main.content_push_hook.send_content_push') as send:
            with self.captureOnCommitCallbacks(execute=True):
                p = SportPost.objects.create(image='cover.jpg', is_published=False, notify_users=True)
            send.assert_not_called()
            with self.captureOnCommitCallbacks(execute=True):
                p.is_published = True
                p.save()
                send.assert_not_called()
            send.assert_called_once_with('post', p.pk, 'default')
            with self.captureOnCommitCallbacks(execute=True):
                p.description = 'Edited'
                p.save()
            self.assertEqual(send.call_count, 1)

    def test_hook_failure_preserves_publication_for_fallback_poll(self):
        with patch.dict('os.environ', {'CONTENT_PUSH_WEBHOOK_TOKEN': 'offline-secret'}):
            with patch('main.content_push_hook.urlopen', side_effect=TimeoutError), self.captureOnCommitCallbacks(execute=True):
                p = Wallpaper.objects.create(title='Test', image='test.jpg', is_published=True, notify_users=True)
            p.refresh_from_db()
            self.assertIsNotNone(p.notification_requested_at)
            self.assertEqual(len(self.client.get('/api/content-notifications/').json()['items']), 1)

    def test_hook_posts_committed_payload_to_fixed_sender(self):
        from .content_push_hook import send_content_push
        p = SportPost.objects.create(image='cover.jpg', description='Test body', is_published=True, notify_users=True)
        response = MagicMock()
        response.__enter__.return_value.status = 200
        with patch.dict('os.environ', {'CONTENT_PUSH_WEBHOOK_TOKEN': 'offline-secret'}), patch('main.content_push_hook.urlopen', return_value=response) as post:
            send_content_push('post', p.pk)
        import json
        request = post.call_args.args[0]
        self.assertEqual(json.loads(request.data)['id'], f'content:post:{p.pk}')
        self.assertEqual(request.full_url, 'https://amedspor-football-api.emrahrecber88.workers.dev/hooks/content-published')
        self.assertEqual(post.call_args.kwargs['timeout'], 8)

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
