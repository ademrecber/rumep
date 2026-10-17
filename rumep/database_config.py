"""Database configuration without connecting or exposing connection secrets."""
from pathlib import Path
from urllib.parse import urlsplit

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


def database_config(base_dir: Path, database_url: str = '') -> dict:
    if not database_url.strip():
        return {'ENGINE': 'django.db.backends.sqlite3', 'NAME': base_dir / 'db.sqlite3'}
    try:
        if urlsplit(database_url).scheme not in {'postgres', 'postgresql'}:
            raise ValueError('unsupported database scheme')
        config = dj_database_url.parse(database_url, conn_max_age=0, conn_health_checks=True)
        if not all(config.get(key) for key in ('HOST', 'NAME', 'USER', 'PASSWORD')):
            raise ValueError('incomplete remote connection')
    except (ValueError, TypeError, KeyError):
        raise ImproperlyConfigured(
            'DATABASE_URL must be a complete PostgreSQL connection URL. Its value is not logged.'
        ) from None
    config.setdefault('OPTIONS', {})['sslmode'] = 'require'
    config['DISABLE_SERVER_SIDE_CURSORS'] = True
    return config
