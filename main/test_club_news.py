from datetime import timedelta
from unittest.mock import Mock
from django.test import TestCase, override_settings
from django.utils import timezone
from .club_news import parse_official, sync_news, OFFICIAL
from .models import ClubNews, ClubNewsSync


@override_settings(SECURE_SSL_REDIRECT=False)
class ClubNewsTests(TestCase):
    def source(self, url):
        if url == OFFICIAL:
            return b'<a href="/news/announcement">Official</a>'
        date = (timezone.now() - timedelta(days=1)).isoformat()
        return f'<h1>Official announcement</h1><meta property="article:published_time" content="{date}">'.encode()

    def test_official_requires_date_and_explicit_category(self):
        url = 'https://www.amedspor.com.tr/news/announcement'
        date = (timezone.now() - timedelta(days=1)).isoformat()
        html = f'<meta property="og:title" content="Duyuru"><meta property="article:published_time" content="{date}"><meta property="article:section" content="transfer">'
        row = parse_official(url, html, timezone.now())
        self.assertEqual(row['kind'], 'transfer')
        self.assertTrue(row['is_official'])
        self.assertIsNone(parse_official(url, '<h1>Undated</h1>', timezone.now()))

    def test_visible_official_date_and_category(self):
        html = '<meta property="og:title" content="Amedspor"><span>Resmî duyuru</span><span>transfer</span><h1>Resmî duyuru</h1><div>17 Ağustos 2026, 18:54</div>'
        from datetime import datetime, timezone as tz
        row = parse_official('https://www.amedspor.com.tr/news/example', html, datetime(2026, 11, 8, tzinfo=tz.utc))
        self.assertEqual(row['kind'], 'transfer')
        self.assertEqual(row['title'], 'Resmî duyuru')
        self.assertEqual(row['published_at'].year, 2026)

    def test_sync_is_bounded_idempotent_and_failure_keeps_rows(self):
        fetch = Mock(side_effect=self.source)
        self.assertEqual(sync_news(fetch), 1)
        self.assertEqual(sync_news(fetch), 0)
        self.assertEqual(fetch.call_count, 2)
        ClubNewsSync.objects.update(next_attempt_at=timezone.now()-timedelta(seconds=1))
        sync_news(fetch)
        self.assertEqual(ClubNews.objects.count(), 1)
        ClubNewsSync.objects.update(next_attempt_at=timezone.now()-timedelta(seconds=1))
        sync_news(Mock(side_effect=TimeoutError()))
        self.assertEqual(ClubNews.objects.count(), 1)

    def test_api_is_read_only_excludes_hidden_and_future_without_fetch(self):
        sync_news(self.source)
        row = ClubNews.objects.get()
        ClubNews.objects.create(source_url='https://www.aspor.com.tr/old', source='A Spor', title='Old press', summary='Old', kind='news', published_at=timezone.now(), is_official=False)
        self.assertEqual(len(self.client.get('/api/club-news/').json()['items']), 1)
        self.assertEqual(self.client.post('/api/club-news/').status_code, 405)
        row.is_hidden = True
        row.save()
        self.assertEqual(self.client.get('/api/club-news/').json()['items'], [])
