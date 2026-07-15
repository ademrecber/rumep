from django.contrib import admin
from .models import RuxPdfComment

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
