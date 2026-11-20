"""Bound published content after publication, without background polling."""
import logging

from django.db import DEFAULT_DB_ALIAS, connections, transaction

from .models import SportPost, Wallpaper

LIMITS = {SportPost: 40, Wallpaper: 50}
logger = logging.getLogger(__name__)


def expired_ids(model, using=None):
    ordering = ('-published_at', '-pk') if model is SportPost else ('-created_at', '-pk')
    return list(model.objects.using(using).filter(is_published=True)
                .order_by(*ordering).values_list('pk', flat=True)[LIMITS[model]:])


def prune_published(model, using=None):
    alias = using or DEFAULT_DB_ALIAS
    with transaction.atomic(using=alias):
        connection = connections[alias]
        if connection.vendor == 'postgresql':
            # Serialize competing publications without a permanent connection,
            # a new table, or any lock in the read endpoints.
            with connection.cursor() as cursor:
                cursor.execute('SELECT pg_advisory_xact_lock(%s)',
                               [940040 if model is SportPost else 940050])
        ids = expired_ids(model, alias)
        if ids:
            model.objects.using(alias).filter(pk__in=ids, is_published=True).delete()
        return len(ids)


def schedule_retention(model, using=None):
    def prune():
        try:
            removed = prune_published(model, using)
            if removed:
                logger.info('Content retention removed %s old %s records', removed, model._meta.model_name)
        except Exception:
            # Publication already committed: never claim that saving failed.
            # A later publication retries the same bounded cleanup.
            logger.warning('Content retention failed for %s; retry on next publication', model._meta.model_name)
    transaction.on_commit(prune, using=using)
