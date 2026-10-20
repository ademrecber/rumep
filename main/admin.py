from django.contrib import admin
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
from .models import Wallpaper
from .models import SporTestApplication
from .models import SportPost, SportPostImage


class SportPostImageForm(forms.ModelForm):
    class Meta:
        model = SportPostImage
        fields = ('image', 'position')

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and 'image' in self.changed_data:
            if not settings.WALLPAPER_UPLOADS_ENABLED:
                raise ValidationError('Kalıcı depolama bağlı değil; yükleme kapalı.')
            from .feed_images import prepare_post
            prepare_post(image)
            image.seek(0)
        return image


class SportPostImageInline(admin.TabularInline):
    model = SportPostImage
    form = SportPostImageForm
    extra = 1
    max_num = 9
    validate_max = True


class SportPostForm(forms.ModelForm):
    class Meta:
        model = SportPost
        fields = '__all__'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if 'image' in self.changed_data and image:
            if not settings.WALLPAPER_UPLOADS_ENABLED:
                raise ValidationError('Kalıcı görsel depolaması bağlı değil; yükleme kapalı.')
            from .feed_images import prepare_post
            prepare_post(image)
            image.seek(0)
        return image


@admin.register(SportPost)
class SportPostAdmin(admin.ModelAdmin):
    inlines = [SportPostImageInline]
    form = SportPostForm
    list_display = ('id', 'preview', 'is_published', 'file_size', 'published_at')
    list_filter = ('is_published',)
    search_fields = ('description',)
    readonly_fields = ('preview', 'width', 'height', 'file_size', 'published_at', 'created_at', 'updated_at')
    fields = ('image', 'preview', 'description', 'is_published', 'notify_users', 'width', 'height', 'file_size', 'published_at', 'created_at', 'updated_at')

    @admin.display(description='Önizleme')
    def preview(self, obj):
        if not obj.thumbnail:
            return 'Kaydedince önizleme oluşur.'
        return format_html('<img src="{}" width="96" style="border-radius:12px" alt="Paylaşım">', obj.thumbnail.url)


@admin.register(SporTestApplication)
class SporTestApplicationAdmin(admin.ModelAdmin):
    change_list_template = 'admin/main/sportestapplication/change_list.html'
    list_display = ('email', 'status_badge', 'added_to_test', 'created_at')
    list_editable = ('added_to_test',)
    list_filter = ('added_to_test', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
    actions = ('mark_added', 'mark_waiting')
    list_per_page = 50

    @admin.display(description='Durum', ordering='added_to_test')
    def status_badge(self, obj):
        return format_html('<span style="display:inline-block;padding:6px 12px;border-radius:20px;background:{};color:{};font-weight:600">{}</span>',
                           '#d9fbe8' if obj.added_to_test else '#fff0cf',
                           '#12623d' if obj.added_to_test else '#765318',
                           '✓ Teste eklendi' if obj.added_to_test else '● Eklenmeyi bekliyor')

    @admin.action(description='Seçilenleri teste eklendi olarak işaretle')
    def mark_added(self, request, queryset):
        queryset.update(added_to_test=True)

    @admin.action(description='Seçilenleri bekliyor olarak işaretle')
    def mark_waiting(self, request, queryset):
        queryset.update(added_to_test=False)

    def has_add_permission(self, request):
        return False

admin.site.site_header = 'Rumep Stüdyo'
admin.site.site_title = 'Rumep Stüdyo'
admin.site.index_title = 'İçerik yönetimi'


class WallpaperForm(forms.ModelForm):
    class Meta:
        model = Wallpaper
        fields = '__all__'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if 'image' in self.changed_data and image:
            if not settings.WALLPAPER_UPLOADS_ENABLED:
                raise ValidationError('Kalıcı görsel depolaması henüz bağlanmadı. Veri kaybını önlemek için canlı yükleme kapalı.')
            from .wallpaper_images import prepare_wallpaper
            prepare_wallpaper(image)
            image.seek(0)
        return image


@admin.register(Wallpaper)
class WallpaperAdmin(admin.ModelAdmin):
    form = WallpaperForm
    list_display = ('preview', 'title', 'is_published', 'resolution', 'published_at', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    readonly_fields = ('preview', 'resolution', 'file_size', 'published_at', 'created_at', 'updated_at')
    fields = ('title', 'description', 'image', 'preview', 'is_published', 'notify_users', 'resolution', 'file_size', 'published_at', 'created_at', 'updated_at')

    @admin.display(description='Önizleme')
    def preview(self, obj):
        if not obj.thumbnail:
            return 'Görsel seçip kaydettiğinde önizleme oluşur.'
        return format_html('<img src="{}" width="80" height="120" style="object-fit:contain;border-radius:10px" alt="Duvar kağıdı önizlemesi">', reverse('wallpaper_admin_preview', args=[obj.pk]))

    @admin.display(description='Çözünürlük')
    def resolution(self, obj):
        return f'{obj.width} × {obj.height}' if obj.width else '—'
