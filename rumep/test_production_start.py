import subprocess
from unittest import TestCase
from unittest.mock import patch

from scripts.start_production import main


class ProductionStartTests(TestCase):
    def test_prepares_runtime_before_starting_gunicorn(self):
        with patch('scripts.start_production.subprocess.run') as run, \
                patch('scripts.start_production.os.execvp') as start, \
                patch.dict('os.environ', {'PORT': '9000'}):
            main()
        self.assertEqual([c.args[0][2] for c in run.call_args_list], ['migrate', 'collectstatic'])
        self.assertTrue(all(c.kwargs['check'] for c in run.call_args_list))
        self.assertIn('0.0.0.0:9000', start.call_args.args[1])

    def test_failed_migration_prevents_server_start(self):
        with patch('scripts.start_production.subprocess.run',
                   side_effect=subprocess.CalledProcessError(1, 'migrate')), \
                patch('scripts.start_production.os.execvp') as start:
            with self.assertRaises(subprocess.CalledProcessError):
                main()
        start.assert_not_called()
