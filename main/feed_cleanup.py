"""Remove superseded post objects only after the database commit succeeds."""
import logging
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import SportPost


def cleanup(files):
    def remove():
        for storage, name in files:
            if name and not SportPost.objects.filter(image=name).exists() and not SportPost.objects.filter(thumbnail=name).exists():
                try:
                    storage.delete(name)
                except Exception:
                    logging.getLogger(__name__).warning('Post object cleanup failed; retry required')
    transaction.on_commit(remove)


@receiver(pre_save, sender=SportPost)
def remember_files(sender, instance, **kwargs):
    old = sender.objects.filter(pk=instance.pk).first() if instance.pk else None
    instance._old_files = [(f.storage, f.name) for f in (old.image, old.thumbnail)] if old else []


@receiver(post_save, sender=SportPost)
def remove_replaced(sender, instance, **kwargs):
    current = {instance.image.name, instance.thumbnail.name}
    cleanup([(s, n) for s, n in getattr(instance, '_old_files', []) if n not in current])


@receiver(post_delete, sender=SportPost)
def remove_deleted(sender, instance, **kwargs):
    cleanup([(f.storage, f.name) for f in (instance.image, instance.thumbnail)])
