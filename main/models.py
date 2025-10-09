from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from .mixins import KurdishTextValidationMixin, ContributionMixin, SafeDeleteMixin
import uuid
import re

def validate_title_text_only(value):
    """Başlıkta sadece harf, rakam, boşluk ve temel noktalama işaretlerine izin ver"""
    import unicodedata
    for char in value:
        category = unicodedata.category(char)
        # Harf (L*), rakam (N*), boşluk (Z*) ve temel noktalama (P*) kategorilerine izin ver
        # Emoji ve semboller (S*) engellenecek
        if not (category.startswith('L') or category.startswith('N') or 
                category.startswith('Z') or category.startswith('P') or
                char in '.,!?;:()\\-\'"'):
            raise ValidationError(_('Başlık sadece harf, rakam, boşluk ve temel noktalama işaretleri içerebilir. Emoji ve özel karakterler kullanılamaz.'))
    return value

def generate_short_id():
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Kategori')
        verbose_name_plural = _('Kategoriler')
        ordering = ['name']
    
    def __str__(self):
        return str(self.get_display_name())
    
    def get_display_name(self):
        """Kategori adını çeviri ile döndür"""
        category_translations = {
            'bilim': _('Bilim'),
            'egitim': _('Eğitim'),
            'sanat': _('Sanat'),
            'siyaset': _('Siyaset'),
            'spor': _('Spor'),
            'teknoloji': _('Teknoloji'),
        }
        return str(category_translations.get(self.name.lower(), self.name))
    
    def topic_count(self):
        return self.topics.count()

class TopicManager(models.Manager):
    def with_related(self):
        return self.select_related('user').prefetch_related(
            'entries__user', 'categories', 'upvotes', 'downvotes'
        )
    
    def popular(self):
        return self.with_related().annotate(
            entry_count=models.Count('entries'),
            vote_score=models.Count('upvotes') - models.Count('downvotes')
        ).order_by('-vote_score', '-updated_at')

class Topic(models.Model):
    title = models.CharField(max_length=200, unique=True, validators=[validate_title_text_only])
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, blank=True, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='upvoted_topics', blank=True)
    downvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='downvoted_topics', blank=True)
    
    objects = TopicManager()
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Başlık')
        verbose_name_plural = _('Başlıklar')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Topic.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.code:
            import random
            max_attempts = 10
            for _ in range(max_attempts):
                code = str(random.randint(100000000, 999999999))
                if not Topic.objects.filter(code=code).exists():
                    self.code = code
                    break
            else:
                # Fallback: timestamp + random
                import time
                self.code = str(int(time.time()))[-9:] + str(random.randint(10, 99))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def entry_count(self):
        return self.entries.count()
    
    def last_entry(self):
        return self.entries.order_by('-created_at').first()
    
    def can_be_edited_by(self, user):
        # Kendi başlığını ve başka kimse entry yazmamışsa düzenleyebilir veya moderatör+
        if hasattr(user, 'profile') and user.profile.is_moderator():
            return True
        return self.user == user and self.entries.exclude(user=user).count() == 0
    
    def can_be_deleted_by(self, user):
        # Kendi başlığını ve başka kimse entry yazmamışsa silebilir veya moderatör+
        if hasattr(user, 'profile') and user.profile.is_moderator():
            return True
        return self.user == user and self.entries.exclude(user=user).count() == 0
    
    def upvote_count(self):
        return self.upvotes.count()
    
    def downvote_count(self):
        return self.downvotes.count()
    
    def vote_score(self):
        return self.upvote_count() - self.downvote_count()

class EntryManager(models.Manager):
    def with_related(self):
        return self.select_related('user', 'topic').prefetch_related(
            'likes', 'upvotes', 'downvotes'
        )

class Entry(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='entries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=10000)
    code = models.CharField(max_length=10, unique=True, blank=True)
    link = models.URLField(blank=True, null=True)
    font_family = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_entries', blank=True)
    upvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='upvoted_entries', blank=True)
    downvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='downvoted_entries', blank=True)
    
    objects = EntryManager()
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Entry')
        verbose_name_plural = _('Entry\'ler')
    
    def save(self, *args, **kwargs):
        if not self.code:
            import random
            max_attempts = 10
            for _ in range(max_attempts):
                code = str(random.randint(100000000, 999999999))
                if not Entry.objects.filter(code=code).exists():
                    self.code = code
                    break
            else:
                # Fallback: timestamp + random
                import time
                self.code = str(int(time.time()))[-9:] + str(random.randint(10, 99))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.topic.title} - {self.user.username}"
    
    def like_count(self):
        return self.likes.count()
    
    def can_be_edited_by(self, user):
        # Kendi entry'sini düzenleyebilir veya moderatör+
        if hasattr(user, 'profile') and user.profile.is_moderator():
            return True
        return self.user == user
    
    def can_be_deleted_by(self, user):
        # Kendi entry'sini silebilir veya moderatör+
        if hasattr(user, 'profile') and user.profile.is_moderator():
            return True
        return self.user == user
    
    def upvote_count(self):
        return self.upvotes.count()
    
    def downvote_count(self):
        return self.downvotes.count()
    
    def vote_score(self):
        return self.upvote_count() - self.downvote_count()
    
    def get_content_with_font(self):
        from django.utils.safestring import mark_safe
        from .templatetags.post_tags import render_emojis
        content = render_emojis(self.content)
        if self.font_family:
            return mark_safe(f'<span style="font-family: {self.font_family};">{content}</span>')
        return mark_safe(content)



class Profile(models.Model):
    USER_ROLES = [
        ('user', _('Kullanıcı')),
        ('writer', _('Yazar')),
        ('moderator', _('Moderatör')),
        ('admin', _('Admin')),
        ('super_admin', _('Süper Admin')),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    username = models.CharField(max_length=30, unique=True)
    biography = models.TextField(max_length=500, blank=True, null=True)
    instagram_username = models.CharField(max_length=30, blank=True, null=True)
    twitter_username = models.CharField(max_length=30, blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True, verbose_name=_('YouTube Kanalı'))
    tiktok_username = models.CharField(max_length=30, blank=True, null=True, verbose_name=_('TikTok Kullanıcı Adı'))
    linkedin_url = models.URLField(blank=True, null=True, verbose_name=_('LinkedIn Profili'))
    github_username = models.CharField(max_length=30, blank=True, null=True, verbose_name=_('GitHub Kullanıcı Adı'))
    website_url = models.URLField(blank=True, null=True, verbose_name=_('Kişisel Website'))
    facebook_username = models.CharField(max_length=30, blank=True, null=True, verbose_name=_('Facebook Kullanıcı Adı'))
    user_role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default='user',
        verbose_name=_('Kullanıcı Rolü')
    )
    katki_puani = models.PositiveIntegerField(default=0)
    account_status = models.CharField(
        max_length=20,
        choices=[
            ('active', _('Aktif')),
            ('frozen', _('Dondurulmuş')),
            ('deletion_scheduled', _('Silinme Planlandı'))
        ],
        default='active'
    )
    scheduled_deletion_date = models.DateTimeField(blank=True, null=True)
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('tr', _('Türkçe')),
            ('ku', _('Kürtçe')),
            ('en', _('İngilizce')),
        ],
        default='tr',
        blank=True
    )


    def clean(self):
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            raise ValidationError({'username': _('Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir.')})
        if not re.match(r'^[a-zA-Z0-9_\s]+$', self.nickname):
            raise ValidationError({'nickname': _('İsim sadece harf, rakam, alt çizgi ve boşluk içerebilir.')})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nickname
    
    def is_writer(self):
        return self.user_role in ['writer', 'moderator', 'admin', 'super_admin']
    
    def is_moderator(self):
        return self.user_role in ['moderator', 'admin', 'super_admin']
    
    def is_admin(self):
        return self.user_role in ['admin', 'super_admin']
    
    def is_super_admin(self):
        return self.user_role == 'super_admin'
    
    def is_staff_or_admin(self):
        return self.user.is_staff or self.is_admin()
    
    def can_edit_content(self, content_user):
        """İçeriği düzenleyebilir mi?"""
        return (self.user == content_user or 
                self.is_moderator())
    
    def can_delete_content(self, content_user):
        """İçeriği silebilir mi?"""
        return (self.user == content_user or 
                self.is_moderator())
    
    def can_moderate_users(self):
        """Kullanıcıları yönetebilir mi?"""
        return self.is_moderator()
    
    def can_manage_categories(self):
        """Kategorileri yönetebilir mi?"""
        return self.is_admin()
    
    def get_role_display_with_badge(self):
        """Rol adını badge ile döndür"""
        role_badges = {
            'user': '',
            'writer': '✍️',
            'moderator': '🛡️',
            'admin': '👑',
            'super_admin': '⭐'
        }
        badge = role_badges.get(self.user_role, '')
        role_name = self.get_user_role_display()
        return f"{badge} {role_name}" if badge else role_name



class Sozluk(models.Model):
    kelime = models.CharField(max_length=50, db_index=True, unique=True)
    detay = models.TextField(max_length=500)
    turkce_karsiligi = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Türkçe Karşılığı'))
    ingilizce_karsiligi = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('İngilizce Karşılığı'))
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)
    tur = models.CharField(
        max_length=20,
        choices=[
            ('isim', _('İsim')),
            ('fiil', _('Fiil')),
            ('sifat', _('Sıfat')),
            ('zarf', _('Zarf')),
            ('beyanvan', _('Beyanvan')),
            ('pevek', _('Bağlaç')),
            ('giredek', _('Bağlaç')),
            ('bang', _('Ünlem')),     
        ],
        blank=True
    )

    class Meta:
        ordering = ['kelime']
        verbose_name = _('Sözlük')
        verbose_name_plural = _('Sözlük')

    def clean(self):
        if not re.match(r'^[a-zçêîşû\s]+$', self.kelime.lower()):
            raise ValidationError({'kelime': _('Kelime sadece Kürtçe harfleri içerebilir (a-z, ç, ê, î, ş, û ve boşluk).')})
        if not self.detay.strip():
            raise ValidationError({'detay': _('Detay alanı zorunludur.')})

    def save(self, *args, **kwargs):
        self.kelime = self.kelime.upper()
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        try:
            Katki.objects.create(
                user=self.kullanici,
                tur='sozluk',
                icerik_id=self.id,
                puan=settings.KATKI_PUANLARI['sozluk']
            )
            profile, created = Profile.objects.get_or_create(
                user=self.kullanici,
                defaults={'katki_puani': 0, 'nickname': self.kullanici.username, 'username': self.kullanici.username}
            )
            profile.katki_puani += settings.KATKI_PUANLARI['sozluk']
            profile.save()
        except Exception:
            pass

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
        verbose_name = _('Kişi')
        verbose_name_plural = _('Kişiler')

    def clean(self):
        if not re.match(r'^[a-zçêîşû\s]+$', self.ad.lower()):
            raise ValidationError({'ad': _('Ad sadece Kürtçe harfleri içerebilir (a-z, ç, ê, î, ş, û ve boşluk).')})
        if not self.biyografi.strip():
            raise ValidationError({'biyografi': _('Biyografi alanı zorunludur.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        try:
            Katki.objects.create(
                user=self.kullanici,
                tur='kisi',
                icerik_id=self.id,
                puan=settings.KATKI_PUANLARI['kisi']
            )
            profile, created = Profile.objects.get_or_create(
                user=self.kullanici,
                defaults={'katki_puani': 0, 'nickname': self.kullanici.username, 'username': self.kullanici.username}
            )
            profile.katki_puani += settings.KATKI_PUANLARI['kisi']
            profile.save()
        except Exception:
            pass

    def __str__(self):
        return self.ad
    
class KisiDetay(models.Model):
    kisi = models.ForeignKey(Kisi, on_delete=models.CASCADE, related_name='detaylar')
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    detay = models.TextField(max_length=20000, validators=[MinLengthValidator(10)])
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-eklenme_tarihi']
        verbose_name = _('Kişi Detayı')
        verbose_name_plural = _('Kişi Detayları')

    def clean(self):
        if not self.detay.strip():
            raise ValidationError({'detay': _('Detay alanı zorunludur.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        Katki.objects.create(
            user=self.kullanici,
            tur='kisi_detay',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI.get('kisi_detay', 5)
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI.get('kisi_detay', 5)
        self.kullanici.profile.save()

    def __str__(self):
        return f"{self.kisi.ad} - {self.detay[:50]}"

class Album(models.Model):
    kisi = models.ForeignKey(Kisi, on_delete=models.CASCADE, related_name='albumler')
    ad = models.CharField(max_length=100)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)
    yil = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Albüm Yılı'))

    class Meta:
        ordering = ['ad']
        verbose_name = _('Albüm')
        verbose_name_plural = _('Albümler')
        unique_together = ('kisi', 'ad')

    def clean(self):
        if not self.ad.strip():
            raise ValidationError({'ad': _('Albüm adı zorunludur.')})

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
            ('klasik', _('Klasik')),
            ('arabesk', _('Arabesk')),
            ('dengbej', _('Dengbej')),
            ('halk', _('Halk Müziği')),
            ('serbest', 'Serbest'),
            ('rock', 'Rock'),
            ('rap', 'Rap'),
            ('hiphop', 'Hip Hop'),
            ('caz', 'Caz'),
            ('blues', 'Blues'),
            ('metal', 'Metal'),
            ('elektronik', _('Elektronik')),
            ('tekno', 'Tekno'),
            ('rnb', 'R&B'),
            ('reggae', 'Reggae'),
            ('tasavvuf', _('Dini Müzik')),
            ('film', _('Film Müziği')),
            ('çocuk', _('Çocuk Müziği')),
            ('enstrümantal', _('Enstrümantal')),
            ('deneysel', _('Deneysel')),
        ],
        blank=True,
        verbose_name="Tür"
    )

    class Meta:
        ordering = ['ad']
        verbose_name = _('Şarkı')
        verbose_name_plural = _('Şarkılar')

    def clean(self):
        if not self.ad.strip():
            raise ValidationError({'ad': _('Şarkı adı zorunludur.')})
        if not self.sozler.strip():
            raise ValidationError({'sozler': _('Şarkı sözleri zorunludur.')})

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
        verbose_name = _('Şarkı Detayı')
        verbose_name_plural = _('Şarkı Detayları')

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
        verbose_name = _('Atasözü')
        verbose_name_plural = _('Atasözleri')

    def clean(self):
        if not self.kelime.strip():
            raise ValidationError({'kelime': _('Atasözü alanı zorunludur.')})
        if not self.anlami.strip():
            raise ValidationError({'anlami': _('Anlam alanı zorunludur.')})

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
        verbose_name = _('Deyim')
        verbose_name_plural = _('Deyimler')

    def clean(self):
        if not self.kelime.strip():
            raise ValidationError({'kelime': _('Deyim alanı zorunludur.')})
        if not self.anlami.strip():
            raise ValidationError({'anlami': _('Anlam alanı zorunludur.')})

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
        verbose_name = _('Atasözü/Deyim Detayı')
        verbose_name_plural = _('Atasözü/Deyim Detayları')

    def clean(self):
        if self.atasozu and self.deyim:
            raise ValidationError(_('Atasözü ve deyim birlikte belirtilemez.'))
        if not (self.atasozu or self.deyim):
            raise ValidationError(_('Atasözü veya deyimden biri belirtilmelidir.'))
        if not self.detay.strip():
            raise ValidationError({'detay': 'Qada berfireh mecbûrî ye.'})

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
            ('sarki', _('Şarkı Sözleri')),
            ('kisi', _('Kişi')),
            ('sozluk', _('Sözlük')),
            ('atasozu', _('Atasözü')),
            ('deyim', _('Deyim')),
            ('yer_adi', _('Yer Adı')),
        ]
    )
    icerik_id = models.PositiveIntegerField()
    puan = models.PositiveIntegerField()
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-eklenme_tarihi']
        verbose_name = _('Katkı')
        verbose_name_plural = _('Katkılar')

    def __str__(self):
        return f"{self.user.username} - {self.tur} - {self.eklenme_tarihi}"

class AIProviderConfig(models.Model):
      PROVIDER_CHOICES = [
          ('deepseek', 'DeepSeek'),
          ('huggingface', 'Hugging Face'),
          ('grok', 'Grok'),
          ('gemini', 'Gemini'),
      ]

      provider = models.CharField(
          max_length=20,
          choices=PROVIDER_CHOICES,
          default='gemini',
          unique=True,
          verbose_name=_('AI Sağlayıcısı')
      )
      is_active = models.BooleanField(default=False, verbose_name=_('Aktif'))
      api_key = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('API Anahtarı'))
      created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
      updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncelleme Tarihi'))

      class Meta:
          verbose_name = _('AI Sağlayıcı Yapılandırması')
          verbose_name_plural = _('AI Sağlayıcı Yapılandırmaları')

      def __str__(self):
          return f"{self.get_provider_display()} - {str(_('Aktif')) if self.is_active else str(_('Pasif'))}"

      def clean(self):
          if self.is_active:
              other_active = AIProviderConfig.objects.filter(is_active=True).exclude(pk=self.pk)
              if other_active.exists():
                  raise ValidationError('Tenê yek pêşkêşkara AI dikare çalak be.')
          if self.provider in ['deepseek', 'grok', 'gemini'] and not self.api_key:
              raise ValidationError(f'Ji bo {self.get_provider_display()} miftê API mecbûrî ye.')

      def save(self, *args, **kwargs):
          self.full_clean()
          if self.is_active:
              AIProviderConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
          super().save(*args, **kwargs)
  
class YerAdi(models.Model):
    ad = models.CharField(max_length=100, db_index=True)
    detay = models.TextField(max_length=5000, blank=True)
    kategori = models.CharField(
        max_length=20,
        choices=[
            ('il', _('İl/Şehir')),
            ('ilce', _('İlçe')),
            ('kasaba', _('Kasaba')),
            ('belde', _('Belde')),
            ('koy', _('Köy')),
        ],
        verbose_name=_('Kategori')
    )
    bolge = models.CharField(
        max_length=20,
        choices=[
            ('bakur', 'Bakur'),
            ('basur', 'Başûr'),
            ('rojava', 'Rojava'),
            ('rojhilat', 'Rojhilat'),
        ],
        verbose_name=_('Kürdistan Bölgesi')
    )
    enlem = models.FloatField(null=True, blank=True, verbose_name=_('Enlem'))
    boylam = models.FloatField(null=True, blank=True, verbose_name=_('Boylam'))
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', verbose_name=_('İlgili Yer'))

    class Meta:
        ordering = ['ad']
        verbose_name = _('Yer Adı')
        verbose_name_plural = _('Yer Adları')

    def clean(self):
        if not self.ad.strip():
            raise ValidationError({'ad': _('Yer adı alanı zorunludur.')})
        if not re.match(r'^[a-zçêîşû\s]+$', self.ad.lower()):
            raise ValidationError({'ad': _('Yer adı sadece Kürtçe harfleri içerebilir (a-z, ç, ê, î, ş, û ve boşluk).')})
        if self.kategori != 'il' and not self.parent:
            raise ValidationError({'parent': _('Şehir dışındaki kategoriler için ilgili yer seçilmelidir.')})
        if self.kategori == 'il' and self.parent:
            raise ValidationError({'parent': _('Şehir kategorisi için ilgili yer seçilmez.')})
        if self.parent:
            if self.kategori == 'ilce' and self.parent.kategori != 'il':
                raise ValidationError({'parent': _('İlçe sadece bir şehirle bağlantılı olabilir.')})
            if self.kategori in ['kasaba', 'belde', 'koy'] and self.parent.kategori not in ['il', 'ilce']:
                raise ValidationError({'parent': _('Kasaba, belde veya köy sadece şehir veya ilçe ile bağlantılı olabilir.')})

    def save(self, *args, **kwargs):
        self.ad = self.ad.upper()
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='yer_adi',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI.get('yer_adi', 10)
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI.get('yer_adi', 10)
        self.kullanici.profile.save()

    def __str__(self):
        return self.ad

class YerAdiDetay(models.Model):
    yer_adi = models.ForeignKey(YerAdi, on_delete=models.CASCADE, related_name='detaylar')
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    detay = models.TextField(max_length=5000, validators=[MinLengthValidator(10)])
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-eklenme_tarihi']
        verbose_name = _('Yer Adı Detayı')
        verbose_name_plural = _('Yer Adı Detayları')

    def clean(self):
        if not self.detay.strip():
            raise ValidationError({'detay': 'Qada berfireh mecbûrî ye.'})
        if self.yer_adi.kullanici == self.kullanici:
            raise ValidationError('Bikarhênerê ku navê cihê zêde kiriye nikare berfirehiyên zêde lê zêde bike.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='yer_adi_detay',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI.get('yer_adi_detay', 5)
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI.get('yer_adi_detay', 5)
        self.kullanici.profile.save()

    def __str__(self):
        return f"{self.yer_adi.ad} - {self.detay[:50]}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('entry_reply', 'Entry Yanıtı'),
        ('topic_entry', 'Başlığa Entry'),
        ('vote_received', 'Oy Alındı'),
        ('mention', 'Bahsedilme'),
    ]
    
    NOTIFICATION_CATEGORIES = [
        ('interaction', '💬 Etkileşim'),
        ('social', '👥 Sosyal'),
        ('content', '📝 İçerik'),
        ('important', '🔥 Önemli'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    category = models.CharField(max_length=20, choices=NOTIFICATION_CATEGORIES, default='interaction')
    message = models.CharField(max_length=255)
    related_topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    related_entry = models.ForeignKey(Entry, on_delete=models.CASCADE, null=True, blank=True)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.message}"

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-usage_count', '-created_at']
    
    def __str__(self):
        return f"#{self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def increment_usage(self):
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

class HashtagUsage(models.Model):
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='usages')
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='hashtag_usages')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='hashtag_usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('hashtag', 'entry')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"#{self.hashtag.name} in entry {self.entry.id}"

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'entry')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} bookmarked entry {self.entry.id}"

class TopicBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='topic_bookmarks')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='topic_bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} bookmarked topic {self.topic.title}"