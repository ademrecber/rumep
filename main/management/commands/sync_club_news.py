import time
from django.core.management.base import BaseCommand
from django.db import close_old_connections
from main.club_news import sync_news


class Command(BaseCommand):
    help = 'Import bounded public news links; never calls the football provider.'

    def add_arguments(self, parser):
        parser.add_argument('--loop', action='store_true')

    def handle(self, *args, **options):
        while True:
            try:
                close_old_connections()
                count = sync_news()
                self.stdout.write(f'club_news records processed: {count}')
            except Exception as exc:
                self.stderr.write(f'club_news sync failed: {type(exc).__name__}')
            if not options['loop']:
                break
            time.sleep(1800)
