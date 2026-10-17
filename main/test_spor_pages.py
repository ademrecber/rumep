from django.test import SimpleTestCase, override_settings
from django.contrib.staticfiles import finders


@override_settings(SECURE_SSL_REDIRECT=False)
class SporPagesTests(SimpleTestCase):
    def test_public_pages_have_contact_and_legal_navigation(self):
        for path in ['rumep-spor/', 'rumep-spor/privacy-policy/',
                     'rumep-spor/terms-of-use/', 'rumep-spor/data-deletion/']:
            response = self.client.get('/' + path)
            self.assertEqual(response.status_code, 200)
            text = response.content.decode('utf-8')
            self.assertIn('info@rumep.net', text)
            self.assertIn('/rumep-spor/privacy-policy/', text)
            self.assertNotIn('\ufffd', text)
            self.assertNotIn('Ger\u00e7ekli?e', text)

    def test_promotional_assets_exist(self):
        for name in ['site.css', 'logo.webp'] + [f'screen-{i}.webp' for i in range(1, 7)]:
            self.assertIsNotNone(finders.find('rumep-spor/' + name))
