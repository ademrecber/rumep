"""Run from repo root: python scripts/test_public_site.py. No external DB/email."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ['DJANGO_SETTINGS_MODULE'] = 'rumep.public_settings'
os.environ['SECRET_KEY'] = 'isolated-public-site-test-key'
os.environ['DATABASE_URL'] = 'postgresql://invalid:invalid@127.0.0.1:1/disabled'
import django
django.setup()
from django.test import Client, override_settings
from django.urls import reverse
from django.db.backends.dummy.base import DatabaseWrapper


class PublicSiteTest(unittest.TestCase):
    def test_pages_never_open_database(self):
        with patch.object(DatabaseWrapper, 'cursor', side_effect=AssertionError('Database access forbidden')):
            for url in ['/', '/rumep-spor/', '/rumep-spor/privacy-policy/',
                        '/rumep-spor/terms-of-use/', '/rumep-spor/data-deletion/',
                        '/privacy-policy/', '/terms-of-service/', '/about/', '/contact/',
                        '/cookie-policy/', '/usage-guide/', '/healthz/', '/app-ads.txt']:
                with self.subTest(url=url):
                    self.assertEqual(Client().get(url).status_code, 200)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_HOST_USER='test@example.invalid')
    def test_contact_without_database_or_session(self):
        from django.core import mail
        with patch.object(DatabaseWrapper, 'cursor', side_effect=AssertionError('Database access forbidden')):
            client = Client()
            response = client.post('/contact/', {'name': 'Local test', 'email': 'test@example.invalid', 'message': 'Local test only'})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(client.get(response.url).status_code, 200)

    def test_csrf_and_legacy_admin_separation(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post('/contact/', {'message': 'no csrf'}).status_code, 403)
        self.assertEqual(Client().get('/rumep-studyo/').url, '/rumep-studyo/content/')
        self.assertEqual(Client().get('/admin/').status_code, 404)


if __name__ == '__main__':
    unittest.main()
