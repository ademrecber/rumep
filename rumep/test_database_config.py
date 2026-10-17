from pathlib import Path
import unittest

from django.core.exceptions import ImproperlyConfigured
from rumep.database_config import database_config


class DatabaseConfigurationTests(unittest.TestCase):
    def test_local_database_preserved_without_url(self):
        result = database_config(Path('/project'))
        self.assertEqual(result['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(result['NAME'], Path('/project/db.sqlite3'))

    def test_remote_database_requires_tls_and_supports_pooler(self):
        result = database_config(Path('/project'), 'postgresql://test:offline-only@db.example/testdb?sslmode=disable')
        self.assertEqual(result['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(result['OPTIONS']['sslmode'], 'require')
        self.assertEqual(result['CONN_MAX_AGE'], 0)
        self.assertTrue(result['DISABLE_SERVER_SIDE_CURSORS'])

    def test_invalid_remote_config_is_redacted_and_never_falls_back(self):
        for value in ['sqlite:///other.sqlite3', 'postgresql://user:offline-only@/db', 'postgresql://user:offline-only@host:invalid/db']:
            with self.subTest(value=value), self.assertRaises(ImproperlyConfigured) as error:
                database_config(Path('/project'), value)
            self.assertNotIn('offline-only', str(error.exception))


if __name__ == '__main__':
    unittest.main()
