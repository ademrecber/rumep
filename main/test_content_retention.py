from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from .content_retention import prune_published
from .models import SportPost, SportPostImage, Wallpaper


class ContentRetentionTests(TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.settings_override = override_settings(
            MEDIA_ROOT=self.folder.name,
            STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}},
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    def seed_posts(self, count):
        SportPost.objects.bulk_create([
            SportPost(image=f'posts/{i}.jpg', thumbnail=f'previews/{i}.jpg',
                      is_published=True, published_at=timezone.now()) for i in range(count)
        ])

    def test_publication_keeps_latest_40_with_drafts_and_shared_files_preserved(self):
        self.seed_posts(40)
        oldest = SportPost.objects.order_by('pk').first()
        default_storage.save(oldest.image.name, ContentFile(b'original'))
        default_storage.save(oldest.thumbnail.name, ContentFile(b'preview'))
        extra = SportPostImage.objects.create(post=oldest, image='extra.jpg')
        default_storage.save(extra.image.name, ContentFile(b'extra'))
        draft = Wallpaper.objects.create(title='draft', image=oldest.image.name)
        post_draft = SportPost.objects.create(image='draft.jpg')
        with self.captureOnCommitCallbacks(execute=True):
            newest = SportPost.objects.create(image='new.jpg', is_published=True)
        self.assertEqual(SportPost.objects.filter(is_published=True).count(), 40)
        self.assertTrue(SportPost.objects.filter(pk=newest.pk).exists())
        self.assertTrue(SportPost.objects.filter(pk=post_draft.pk).exists())
        self.assertFalse(SportPostImage.objects.filter(pk=extra.pk).exists())
        self.assertTrue(default_storage.exists(draft.image.name))
        self.assertFalse(default_storage.exists(oldest.thumbnail.name))
        self.assertFalse(default_storage.exists(extra.image.name))

    def test_wallpaper_publication_keeps_latest_50_and_does_not_trim_posts(self):
        self.seed_posts(42)
        Wallpaper.objects.bulk_create([
            Wallpaper(title=str(i), image=f'w/{i}.jpg', is_published=True)
            for i in range(50)
        ])
        oldest = Wallpaper.objects.order_by('created_at', 'pk').first()
        default_storage.save(oldest.image.name, ContentFile(b'wallpaper'))
        with self.captureOnCommitCallbacks(execute=True):
            newest = Wallpaper.objects.create(title='new', image='new.jpg', is_published=True)
        self.assertEqual(Wallpaper.objects.filter(is_published=True).count(), 50)
        self.assertTrue(Wallpaper.objects.filter(pk=newest.pk).exists())
        self.assertFalse(default_storage.exists(oldest.image.name))
        self.assertEqual(SportPost.objects.count(), 42)

    def test_editing_a_published_record_does_not_schedule_retention(self):
        self.seed_posts(41)
        with patch('main.content_retention.schedule_retention') as schedule:
            record = SportPost.objects.first()
            record.description = 'Edited'
            record.save()
            self.assertFalse(schedule.called)
        self.assertEqual(SportPost.objects.count(), 41)

    def test_rollback_preserves_old_records_and_files(self):
        self.seed_posts(40)
        first = SportPost.objects.order_by('pk').first()
        default_storage.save(first.image.name, ContentFile(b'original'))
        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    SportPost.objects.create(image='new.jpg', is_published=True)
                    raise ValueError('rollback')
            except ValueError:
                pass
        self.assertEqual(SportPost.objects.count(), 40)
        self.assertTrue(default_storage.exists(first.image.name))

    def test_repeated_cleanup_is_idempotent_and_uses_publication_order(self):
        self.seed_posts(42)
        newest = SportPost.objects.order_by('-pk').first()
        SportPost.objects.filter(pk=newest.pk).update(
            published_at=timezone.now() - timezone.timedelta(days=100))
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(prune_published(SportPost), 2)
            self.assertEqual(prune_published(SportPost), 0)
        self.assertFalse(SportPost.objects.filter(pk=newest.pk).exists())

    def test_cleanup_failure_does_not_turn_committed_publication_into_error(self):
        with patch('main.content_retention.prune_published', side_effect=RuntimeError('offline')):
            with self.captureOnCommitCallbacks(execute=True):
                item = SportPost.objects.create(image='new.jpg', is_published=True)
        self.assertTrue(SportPost.objects.filter(pk=item.pk).exists())
