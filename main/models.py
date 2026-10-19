from django.db import models
from django.utils import timezone


class SporTestApplication(models.Model):
    email = models.EmailField('Google Play Gmail adresi', unique=True)
    added_to_test = models.BooleanField('Teste eklendi', default=False)
    created_at = models.DateTimeField('Başvuru tarihi', auto_now_add=True)

    class Meta:
        ordering = ['added_to_test', '-created_at']
        verbose_name = 'Spor test başvurusu'
        verbose_name_plural = 'Spor test başvuruları'

    def __str__(self):
        return self.email

class RuxPdfComment(models.Model):
    name = models.CharField(max_length=100, verbose_name="İsim")
    message = models.TextField(verbose_name="Mesaj/Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    is_approved = models.BooleanField(default=True, verbose_name="Onaylı mı?")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Rux PDF Yorumu"
        verbose_name_plural = "Rux PDF Yorumları"

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class SportPost(models.Model):
    description = models.TextField('Açıklama', blank=True, max_length=4000)
    image = models.ImageField('Görsel', upload_to='spor-feed/originals/', max_length=200)
    thumbnail = models.ImageField('Önizleme', upload_to='spor-feed/previews/', blank=True, editable=False)
    width = models.PositiveIntegerField(default=0, editable=False)
    height = models.PositiveIntegerField(default=0, editable=False)
    file_size = models.PositiveIntegerField('Dosya boyutu', default=0, editable=False)
    is_published = models.BooleanField('Yayında', default=False)
    published_at = models.DateTimeField('Yayın tarihi', null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-pk']
        verbose_name = 'Rumep Spor paylaşımı'
        verbose_name_plural = 'Rumep Spor akışı'

    def __str__(self):
        return f'Paylaşım #{self.pk or "Yeni"}'

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            from .feed_images import prepare_post
            self.image, self.thumbnail, self.width, self.height = prepare_post(self.image)
            self.file_size = self.image.size
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Wallpaper(models.Model):
    title = models.CharField('Başlık', max_length=160)
    description = models.TextField('Açıklama', blank=True, max_length=4000)
    image = models.ImageField('Duvar kağıdı', upload_to='wallpapers/originals/', max_length=200)
    thumbnail = models.ImageField('Önizleme', upload_to='wallpapers/previews/', blank=True, editable=False)
    width = models.PositiveIntegerField('Genişlik', default=0, editable=False)
    height = models.PositiveIntegerField('Yükseklik', default=0, editable=False)
    file_size = models.PositiveIntegerField('Dosya boyutu', default=0, editable=False)
    is_published = models.BooleanField('Yayında', default=False)
    published_at = models.DateTimeField('İlk yayın tarihi', null=True, blank=True, editable=False)
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncelleme', auto_now=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        verbose_name = 'Duvar kağıdı'
        verbose_name_plural = 'Duvar kağıtları'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            from .wallpaper_images import prepare_wallpaper
            image, thumbnail, self.width, self.height = prepare_wallpaper(self.image)
            self.image = image
            self.thumbnail = thumbnail
            self.file_size = image.size
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
