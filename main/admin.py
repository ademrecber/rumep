from django.contrib import admin
from .models import RuxPdfComment
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
from .models import Wallpaper

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
    fields = ('title', 'description', 'image', 'preview', 'is_published', 'resolution', 'file_size', 'published_at', 'created_at', 'updated_at')

    @admin.display(description='Önizleme')
    def preview(self, obj):
        if not obj.thumbnail:
            return 'Görsel seçip kaydettiğinde önizleme oluşur.'
        return format_html('<img src="{}" width="80" height="120" style="object-fit:contain;border-radius:10px" alt="Duvar kağıdı önizlemesi">', reverse('wallpaper_admin_preview', args=[obj.pk]))

    @admin.display(description='Çözünürlük')
    def resolution(self, obj):
        return f'{obj.width} × {obj.height}' if obj.width else '—'

@admin.register(RuxPdfComment)
class RuxPdfCommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'message')
    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Seçili yorumları onayla"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = "Seçili yorumların onayını kaldır"
