"""Remove superseded post objects only after the database commit succeeds."""
import logging
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import SportPost, SportPostImage, Wallpaper


def cleanup(files, using=None):
    def remove():
        for storage, name in files:
            if name:
                try:
                    if any(model.objects.using(using).filter(**{field: name}).exists()
                           for model in (SportPost, SportPostImage, Wallpaper)
                           for field in ('image', 'thumbnail')):
                        continue
                    storage.delete(name)
                except Exception:
                    logging.getLogger(__name__).warning('Post object cleanup failed; retry required')
    transaction.on_commit(remove, using=using)


@receiver(pre_save, sender=SportPost)
@receiver(pre_save, sender=SportPostImage)
@receiver(pre_save, sender=Wallpaper)
def remember_files(sender, instance, **kwargs):
    old = sender.objects.using(kwargs.get('using')).filter(pk=instance.pk).first() if instance.pk else None
    instance._old_files = [(f.storage, f.name) for f in (old.image, old.thumbnail)] if old else []
    if sender in (SportPost, Wallpaper):
        instance._newly_published = instance.is_published and not (old and old.is_published)


@receiver(post_save, sender=SportPost)
@receiver(post_save, sender=SportPostImage)
@receiver(post_save, sender=Wallpaper)
def remove_replaced(sender, instance, **kwargs):
    current = {instance.image.name, instance.thumbnail.name}
    cleanup([(s, n) for s, n in getattr(instance, '_old_files', []) if n not in current], kwargs.get('using'))
    if getattr(instance, '_newly_published', False) and not kwargs.get('raw'):
        from .content_retention import schedule_retention
        schedule_retention(sender, using=kwargs.get('using'))


@receiver(post_delete, sender=SportPost)
@receiver(post_delete, sender=SportPostImage)
@receiver(post_delete, sender=Wallpaper)
def remove_deleted(sender, instance, **kwargs):
    if sender is SportPostImage:
        from django.utils import timezone
        SportPost.objects.using(kwargs.get('using')).filter(pk=instance.post_id).update(updated_at=timezone.now())
    cleanup([(f.storage, f.name) for f in (instance.image, instance.thumbnail)], kwargs.get('using'))
