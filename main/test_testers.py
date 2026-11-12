from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import SporTestApplication


@override_settings(SECURE_SSL_REDIRECT=False)
class PublicReleaseTests(TestCase):
    def test_retired_signup_does_not_accept_applications(self):
        for method in ('get', 'post'):
            response = getattr(self.client, method)(
                '/rumep-spor/test-katilim/', {'email': 'user@gmail.com', 'consent': 'on'}
            )
            self.assertEqual(response.status_code, 404)
        self.assertEqual(SporTestApplication.objects.count(), 0)

    def test_landing_page_links_directly_to_google_play(self):
        response = self.client.get(reverse('rumep_spor'))
        self.assertContains(response, 'https://play.google.com/store/apps/details?id=net.rumep.spor', count=3)
        self.assertContains(response, 'class="play-button"', count=2)
        self.assertNotContains(response, 'test-katilim')
        self.assertNotContains(response, 'Kapalı test başvuruları açık')
        for name in ('rumep_spor_privacy', 'rumep_spor_terms', 'rumep_spor_data'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_existing_applications_remain_private_and_manageable(self):
        url = reverse('admin:main_sportestapplication_changelist')
        self.assertEqual(self.client.get(url).status_code, 302)
        admin = get_user_model().objects.create_superuser('testeradmin', 'admin@example.com', 'test-only-password')
        self.client.force_login(admin)
        self.assertEqual(self.client.get(url).status_code, 200)
