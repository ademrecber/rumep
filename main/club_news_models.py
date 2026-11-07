from django.db import models


class ClubNews(models.Model):
    source_url = models.URLField(max_length=600, unique=True)
    source = models.CharField(max_length=40)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=350)
    kind = models.CharField(max_length=12, default='news')
    published_at = models.DateTimeField()
    is_official = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    imported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at', '-pk']
        verbose_name = 'Kulüp haber bağlantısı'
        verbose_name_plural = 'Kulüp haber bağlantıları'


class ClubNewsSync(models.Model):
    # A shared lease prevents replica/restart bursts. Fetches never run in views.
    key = models.CharField(max_length=20, primary_key=True)
    next_attempt_at = models.DateTimeField()
    last_success_at = models.DateTimeField(null=True)
    last_error = models.CharField(max_length=100, blank=True)
