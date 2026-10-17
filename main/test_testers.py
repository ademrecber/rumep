from django.core import signing
from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import SporTestApplication


class TesterSignupTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse('rumep_spor_testers')

    def preview(self, email='amed.taraftar@gmail.com'):
        return self.client.post(self.url, {'email': email, 'consent': 'on'})

    def test_preview_requires_final_confirmation_and_normalizes_duplicate_mailbox(self):
        response = self.preview()
        self.assertEqual(SporTestApplication.objects.count(), 0)
        token = response.context['confirmation']
        for _ in range(2):
            response = self.client.post(self.url, {'action': 'confirm', 'confirmation': token})
            self.assertRedirects(response, self.url + '?done=1')
        self.assertEqual(SporTestApplication.objects.get().email, 'amedtaraftar@gmail.com')
        self.assertFalse(SporTestApplication.objects.get().added_to_test)

    def test_only_gmail_and_consent_accepted(self):
        for email in ['user@yahoo.com', 'user@gmail.com.attacker.net', 'a..b@gmail.com', 'a+b@gmail.com']:
            response = self.preview(email)
            self.assertNotIn('confirmation', response.context)
        self.client.post(self.url, {'email': 'user@gmail.com'})
        self.assertEqual(SporTestApplication.objects.count(), 0)

    def test_tampered_and_expired_confirmations_do_not_create_rows(self):
        token = signing.dumps('user@gmail.com', salt='wrong-salt')
        response = self.client.post(self.url, {'action': 'confirm', 'confirmation': token})
        self.assertContains(response, 'Onay süresi')
        self.assertEqual(SporTestApplication.objects.count(), 0)

    def test_csrf_and_private_admin(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post(self.url, {'email': 'user@gmail.com'}).status_code, 403)
        url = reverse('admin:main_sportestapplication_changelist')
        self.assertEqual(self.client.get(url).status_code, 302)
        admin = get_user_model().objects.create_superuser('testeradmin', 'admin@example.com', 'test-only-password')
        self.client.force_login(admin)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_signup_page_is_not_cached_and_rate_limit_does_not_save(self):
        response = self.client.get(self.url)
        self.assertIn('no-store', response['Cache-Control'])
        for _ in range(20):
            self.preview()
        self.assertEqual(self.preview().status_code, 429)
        self.assertEqual(SporTestApplication.objects.count(), 0)
