from django.contrib import admin
from main.models import (
    Profile, Kategori, Kisi, Album, Sarki, Sozluk, Atasozu, Deyim, Katki,
    AIProviderConfig, YerAdi, YerAdiDetay, SozlukDetay, SarkiDetay, AtasozuDeyimDetay, KisiDetay,
    Topic, Entry, Category, Follow, Notification, Hashtag, HashtagUsage, Bookmark, TopicBookmark
)

@admin.register(AIProviderConfig)
class AIProviderConfigAdmin(admin.ModelAdmin):
    list_display = ('provider', 'is_active', 'api_key', 'updated_at')
    list_filter = ('provider', 'is_active')
    search_fields = ('provider', 'api_key')
    list_editable = ('is_active', 'api_key')
    ordering = ('-updated_at',)

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            # Diğer aktif sağlayıcıları pasif yap
            AIProviderConfig.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'username', 'user_role', 'katki_puani', 'account_status')
    list_filter = ('user_role', 'account_status', 'preferred_language')
    search_fields = ('nickname', 'username', 'user__username')
    list_editable = ('user_role', 'account_status')
    ordering = ('-katki_puani',)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('user', 'nickname', 'username', 'biography')
        }),
        ('Rol ve Durum', {
            'fields': ('user_role', 'account_status', 'scheduled_deletion_date')
        }),
        ('Sosyal Medya', {
            'fields': ('instagram_username', 'twitter_username')
        }),
        ('Ayarlar', {
            'fields': ('katki_puani', 'preferred_language')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'get_user_role', 'entry_count', 'created_at')
    list_filter = ('user__profile__user_role', 'created_at')
    search_fields = ('title', 'user__username')
    
    def get_user_role(self, obj):
        return obj.user.profile.get_user_role_display() if hasattr(obj.user, 'profile') else 'Bilinmiyor'
    get_user_role.short_description = 'Kullanıcı Rolü'

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('topic', 'user', 'get_user_role', 'created_at', 'vote_score')
    list_filter = ('user__profile__user_role', 'created_at')
    search_fields = ('topic__title', 'user__username', 'content')
    
    def get_user_role(self, obj):
        return obj.user.profile.get_user_role_display() if hasattr(obj.user, 'profile') else 'Bilinmiyor'
    get_user_role.short_description = 'Kullanıcı Rolü'

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'slug')
    search_fields = ('ad',)
    prepopulated_fields = {'slug': ('ad',)}

@admin.register(Kisi)
class KisiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'kullanici', 'eklenme_tarihi')
    list_filter = ('kategoriler', 'eklenme_tarihi')
    search_fields = ('ad', 'kullanici__username')
    filter_horizontal = ('kategoriler',)
    date_hierarchy = 'eklenme_tarihi'

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('ad', 'kisi', 'yil', 'kullanici', 'sarki_sayisi')
    list_filter = ('yil', 'eklenme_tarihi')
    search_fields = ('ad', 'kisi__ad', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(Sarki)
class SarkiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'album', 'tur', 'kullanici', 'eklenme_tarihi')
    list_filter = ('tur', 'eklenme_tarihi')
    search_fields = ('ad', 'album__ad', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(Sozluk)
class SozlukAdmin(admin.ModelAdmin):
    list_display = ('kelime', 'turkce_karsiligi', 'ingilizce_karsiligi', 'tur', 'kullanici', 'eklenme_tarihi')
    list_filter = ('tur', 'eklenme_tarihi')
    search_fields = ('kelime', 'detay', 'turkce_karsiligi', 'ingilizce_karsiligi', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'
    
    fieldsets = (
        ('Kelime Bilgileri', {
            'fields': ('kelime', 'detay', 'tur')
        }),
        ('Çeviriler', {
            'fields': ('turkce_karsiligi', 'ingilizce_karsiligi'),
            'classes': ('collapse',)
        }),
        ('Diğer', {
            'fields': ('kullanici', 'eklenme_tarihi'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('eklenme_tarihi',)

@admin.register(Atasozu)
class AtasozuAdmin(admin.ModelAdmin):
    list_display = ('kelime', 'kullanici', 'eklenme_tarihi')
    list_filter = ('eklenme_tarihi',)
    search_fields = ('kelime', 'anlami', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(Deyim)
class DeyimAdmin(admin.ModelAdmin):
    list_display = ('kelime', 'kullanici', 'eklenme_tarihi')
    list_filter = ('eklenme_tarihi',)
    search_fields = ('kelime', 'anlami', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(Katki)
class KatkiAdmin(admin.ModelAdmin):
    list_display = ('user', 'tur', 'puan', 'eklenme_tarihi')
    list_filter = ('tur', 'eklenme_tarihi')
    search_fields = ('user__username',)
    date_hierarchy = 'eklenme_tarihi'
    readonly_fields = ('eklenme_tarihi',)

@admin.register(YerAdi)
class YerAdiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'kategori', 'bolge', 'kullanici', 'eklenme_tarihi')
    list_filter = ('kategori', 'bolge', 'eklenme_tarihi')
    search_fields = ('ad', 'detay', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(YerAdiDetay)
class YerAdiDetayAdmin(admin.ModelAdmin):
    list_display = ('yer_adi', 'kullanici', 'eklenme_tarihi')
    list_filter = ('eklenme_tarihi',)
    search_fields = ('yer_adi__ad', 'detay', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(SozlukDetay)
class SozlukDetayAdmin(admin.ModelAdmin):
    list_display = ('kelime', 'kullanici', 'eklenme_tarihi')
    list_filter = ('eklenme_tarihi',)
    search_fields = ('kelime__kelime', 'detay', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(SarkiDetay)
class SarkiDetayAdmin(admin.ModelAdmin):
    list_display = ('sarki', 'kullanici', 'eklenme_tarihi')
    list_filter = ('eklenme_tarihi',)
    search_fields = ('sarki__ad', 'detay', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(AtasozuDeyimDetay)
class AtasozuDeyimDetayAdmin(admin.ModelAdmin):
    list_display = ('get_item_name', 'kullanici', 'eklenme_tarihi')
    list_filter = ('eklenme_tarihi',)
    search_fields = ('detay', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'
    
    def get_item_name(self, obj):
        if obj.atasozu:
            return f"Atasözü: {obj.atasozu.kelime}"
        return f"Deyim: {obj.deyim.kelime}"
    get_item_name.short_description = 'İçerik'

@admin.register(KisiDetay)
class KisiDetayAdmin(admin.ModelAdmin):
    list_display = ('kisi', 'kullanici', 'eklenme_tarihi')
    list_filter = ('eklenme_tarihi',)
    search_fields = ('kisi__ad', 'detay', 'kullanici__username')
    date_hierarchy = 'eklenme_tarihi'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'topic_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    date_hierarchy = 'created_at'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'category', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'category', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'created_at'
    list_editable = ('is_read',)

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'usage_count', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('usage_count',)
    date_hierarchy = 'created_at'

@admin.register(HashtagUsage)
class HashtagUsageAdmin(admin.ModelAdmin):
    list_display = ('hashtag', 'entry', 'topic', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('hashtag__name', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'

@admin.register(TopicBookmark)
class TopicBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'topic__title')
    date_hierarchy = 'created_at'

