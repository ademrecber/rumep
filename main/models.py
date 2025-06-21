from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils import timezone
import uuid
import re

def generate_short_id():
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_id = models.CharField(max_length=8, unique=True, default=generate_short_id, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True, blank=True)
    text = models.TextField(max_length=10000)
    link = models.CharField(max_length=100, blank=True, null=True, unique=True)
    original_link = models.URLField(blank=True, null=True)
    embed_code = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    bookmarks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bookmarked_posts', blank=True)
    views = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.title[:20] if self.title else self.text[:20]}"

    def like_count(self):
        return self.likes.count()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    username = models.CharField(max_length=30, unique=True)
    instagram_username = models.CharField(max_length=30, blank=True, null=True)
    twitter_username = models.CharField(max_length=30, blank=True, null=True)
    posts_visible = models.BooleanField(default=True)
    critiques_visible = models.BooleanField(default=True)
    comments_visible = models.BooleanField(default=True)
    katki_puani = models.PositiveIntegerField(default=0)
    account_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Aktif'),
            ('frozen', 'Dondurulmuş'),
            ('deletion_scheduled', 'Silinme Planlandı')
        ],
        default='active'
    )
    scheduled_deletion_date = models.DateTimeField(blank=True, null=True)
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('tr', 'Türkçe'),
            ('ku', 'Kürtçe'),
            ('en', 'English'),
        ],
        default='tr',
        blank=True
    )

    def __str__(self):
        return self.nickname

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"

class Critique(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_id = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='critiques')
    text = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = '?' + generate_short_id()
        super().save(*args, **kwargs)

class CritiqueVote(models.Model):
    critique = models.ForeignKey(Critique, related_name='votes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('critique', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.critique.short_id} - {self.rating}"

class PostVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=[('up', 'Upvote'), ('down', 'Downvote')])
    class Meta:
        unique_together = ('user', 'post')

class CommentVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=[('up', 'Upvote'), ('down', 'Downvote')])
    class Meta:
        unique_together = ('user', 'comment')

class Sozluk(models.Model):
    kelime = models.CharField(max_length=50, db_index=True, unique=True)
    detay = models.TextField(max_length=500)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)
    tur = models.CharField(
        max_length=20,
        choices=[
            ('isim', 'İsim'),
            ('fiil', 'Fiil'),
            ('sifat', 'Sıfat'),
            ('zarf', 'Zarf')
        ],
        blank=True
    )

    class Meta:
        ordering = ['kelime']
        verbose_name = 'Sözlük'
        verbose_name_plural = 'Sözlük'

    def clean(self):
        if not re.match(r'^[a-zçêîşû\s]+$', self.kelime.lower()):
            raise ValidationError({'kelime': 'Kelime sadece Kürtçe harfler içerebilir (a-z, ç, ê, î, ş, û ve boşluk).'})
        if not self.detay.strip():
            raise ValidationError({'detay': 'Detay alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.kelime = self.kelime.upper()
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='sozluk',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['sozluk']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['sozluk']
        self.kullanici.profile.save()

    def __str__(self):
        return self.kelime

class SozlukDetay(models.Model):
    kelime = models.ForeignKey(Sozluk, on_delete=models.CASCADE, related_name='detaylar')
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    detay = models.TextField(max_length=1000, validators=[MinLengthValidator(10)])
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-eklenme_tarihi']

    def __str__(self):
        return f"{self.kelime.kelime} - {self.detay[:50]}"

class Kategori(models.Model):
    ad = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.ad

class Kisi(models.Model):
    ad = models.CharField(max_length=100, db_index=True)
    biyografi = models.TextField(max_length=20000)
    kategoriler = models.ManyToManyField(Kategori)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['ad']
        verbose_name = 'Kişi'
        verbose_name_plural = 'Kişiler'

    def clean(self):
        if not re.match(r'^[a-zçêîşû\s]+$', self.ad.lower()):
            raise ValidationError({'ad': 'Ad sadece Kürtçe harfler içerebilir (a-z, ç, ê, î, ş, û ve boşluk).'})
        if not self.biyografi.strip():
            raise ValidationError({'biyografi': 'Biyografi alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='kisi',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['kisi']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['kisi']
        self.kullanici.profile.save()

    def __str__(self):
        return self.ad

class Album(models.Model):
    kisi = models.ForeignKey(Kisi, on_delete=models.CASCADE, related_name='albumler')
    ad = models.CharField(max_length=100)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)
    yil = models.PositiveIntegerField(null=True, blank=True, verbose_name="Albüm Yılı")

    class Meta:
        ordering = ['ad']
        verbose_name = 'Albüm'
        verbose_name_plural = 'Albümler'
        unique_together = ('kisi', 'ad')

    def clean(self):
        if not self.ad.strip():
            raise ValidationError({'ad': 'Albüm adı zorunludur.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.kisi.ad} - {self.ad}"

    def sarki_sayisi(self):
        return self.sarkilar.count()

    def diger_kullanicilarin_sarkilari_var_mi(self):
        return self.sarkilar.exclude(kullanici=self.kullanici).exists()

class Sarki(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='sarkilar')
    ad = models.CharField(max_length=100)
    sozler = models.TextField(max_length=10000)
    link = models.URLField(blank=True, null=True)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)
    tur = models.CharField(
        max_length=50,
        choices=[
            ('pop', 'Pop'),
            ('klasik', 'Klasik'),
            ('arabesk', 'Arabesk'),
            ('dengbej', 'Dengbêj'),
            ('halk', 'Halk Müziği'),
            ('serbest', 'Serbest')
        ],
        blank=True,
        verbose_name="Tür"
    )

    class Meta:
        ordering = ['ad']
        verbose_name = 'Şarkı'
        verbose_name_plural = 'Şarkılar'

    def clean(self):
        if not self.ad.strip():
            raise ValidationError({'ad': 'Şarkı adı zorunludur.'})
        if not self.sozler.strip():
            raise ValidationError({'sozler': 'Şarkı sözleri zorunludur.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='sarki',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['sarki']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['sarki']
        self.kullanici.profile.save()

    def __str__(self):
        return f"{self.album.ad} - {self.ad}"

class SarkiDetay(models.Model):
    sarki = models.ForeignKey(Sarki, on_delete=models.CASCADE, related_name='detaylar')
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    detay = models.TextField(max_length=1000, validators=[MinLengthValidator(10)])
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-eklenme_tarihi']
        verbose_name = 'Şarkı Detayı'
        verbose_name_plural = 'Şarkı Detayları'

    def __str__(self):
        return f"{self.sarki.ad} - {self.detay[:50]}"

class Atasozu(models.Model):
    kelime = models.CharField(max_length=500, db_index=True, unique=True)
    anlami = models.TextField(max_length=500)
    ornek = models.TextField(max_length=500, blank=True)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['kelime']
        verbose_name = 'Atasözü'
        verbose_name_plural = 'Atasözleri'

    def clean(self):
        if not self.kelime.strip():
            raise ValidationError({'kelime': 'Atasözü alanı zorunludur.'})
        if not self.anlami.strip():
            raise ValidationError({'anlami': 'Anlam alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.kelime = self.kelime.upper()
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='atasozu',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['atasozu']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['atasozu']
        self.kullanici.profile.save()

    def __str__(self):
        return self.kelime

class Deyim(models.Model):
    kelime = models.CharField(max_length=500, db_index=True, unique=True)
    anlami = models.TextField(max_length=500)
    ornek = models.TextField(max_length=500, blank=True)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['kelime']
        verbose_name = 'Deyim'
        verbose_name_plural = 'Deyimler'

    def clean(self):
        if not self.kelime.strip():
            raise ValidationError({'kelime': 'Deyim alanı zorunludur.'})
        if not self.anlami.strip():
            raise ValidationError({'anlami': 'Anlam alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.kelime = self.kelime.upper()
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='deyim',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['deyim']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['deyim']
        self.kullanici.profile.save()

    def __str__(self):
        return self.kelime

class AtasozuDeyimDetay(models.Model):
    atasozu = models.ForeignKey(Atasozu, on_delete=models.CASCADE, related_name='detaylar', null=True, blank=True)
    deyim = models.ForeignKey(Deyim, on_delete=models.CASCADE, related_name='detaylar', null=True, blank=True)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    detay = models.TextField(max_length=1000, validators=[MinLengthValidator(10)])
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-eklenme_tarihi']
        verbose_name = 'Atasözü/Deyim Detayı'
        verbose_name_plural = 'Atasözü/Deyim Detayları'

    def clean(self):
        if self.atasozu and self.deyim:
            raise ValidationError('Atasözü ve deyim aynı anda tanımlanamaz.')
        if not (self.atasozu or self.deyim):
            raise ValidationError('Atasözü veya deyimden biri tanımlanmalıdır.')
        if not self.detay.strip():
            raise ValidationError({'detay': 'Detay alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.atasozu:
            return f"Atasözü: {self.atasozu.kelime} - {self.detay[:50]}"
        return f"Deyim: {self.deyim.kelime} - {self.detay[:50]}"

class Katki(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='katkilar')
    tur = models.CharField(
        max_length=20,
        choices=[
            ('sarki', 'Şarkı Sözü'),
            ('kisi', 'Kişi'),
            ('sozluk', 'Sözlük'),
            ('atasozu', 'Atasözü'),
            ('deyim', 'Deyim')
        ]
    )
    icerik_id = models.PositiveIntegerField()
    puan = models.PositiveIntegerField()
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-eklenme_tarihi']
        verbose_name = 'Katkı'
        verbose_name_plural = 'Katkılar'

    def __str__(self):
        return f"{self.user.username} - {self.tur} - {self.eklenme_tarihi}"
    
class AIProviderConfig(models.Model):
    PROVIDER_CHOICES = [
        ('deepseek', 'DeepSeek'),
        ('huggingface', 'Hugging Face'),
        ('grok', 'Grok'),
    ]

    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='deepseek',
        unique=True,
        verbose_name='AI Sağlayıcısı'
    )
    is_active = models.BooleanField(default=False, verbose_name='Aktif')
    api_key = models.CharField(max_length=256, blank=True, null=True, verbose_name='API Anahtarı')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'AI Sağlayıcı Konfigürasyonu'
        verbose_name_plural = 'AI Sağlayıcı Konfigürasyonları'

    def __str__(self):
        return f"{self.get_provider_display()} - {'Aktif' if self.is_active else 'Pasif'}"

    def clean(self):
        if self.is_active:
            # Sadece bir sağlayıcı aktif olabilir
            other_active = AIProviderConfig.objects.filter(is_active=True).exclude(pk=self.pk)
            if other_active.exists():
                raise ValidationError('Sadece bir AI sağlayıcısı aktif olabilir.')
        if self.provider in ['deepseek', 'grok'] and not self.api_key:
            raise ValidationError(f'{self.get_provider_display()} için API anahtarı zorunludur.')

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_active:
            # Diğer sağlayıcıları pasif yap
            AIProviderConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)