from django.test import TestCase, override_settings


@override_settings(SECURE_SSL_REDIRECT=False)
class RemovedClubNewsTests(TestCase):
    def test_removed_endpoint_is_not_available(self):
        self.assertEqual(self.client.get('/api/club-news/').status_code, 404)
