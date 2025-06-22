from django.contrib import admin
from main.models import (
    Post, Profile, Comment, PostVote, CommentVote, 
    Category, Critique, CritiqueVote, Kategori, Kisi,
    Album, Sarki, Sozluk, Atasozu, Deyim, Katki,
    AIProviderConfig
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

admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(PostVote)
admin.site.register(CommentVote)
admin.site.register(Category)
admin.site.register(Critique)
admin.site.register(CritiqueVote)
admin.site.register(Kategori)
admin.site.register(Kisi)
admin.site.register(Album)
admin.site.register(Sarki)
admin.site.register(Sozluk)
admin.site.register(Atasozu)
admin.site.register(Deyim)
admin.site.register(Katki)
