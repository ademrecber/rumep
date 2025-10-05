# Notification kategorileri için model güncellemesi

NOTIFICATION_CATEGORIES = [
    ('important', '🔥 Önemli'),
    ('interaction', '💬 Etkileşim'), 
    ('social', '👥 Sosyal'),
    ('content', '📝 İçerik'),
    ('achievement', '⭐ Başarımlar'),
    ('suggestion', '🎯 Öneriler'),
]

# Notification modelinde eklenecek field:
# category = models.CharField(max_length=20, choices=NOTIFICATION_CATEGORIES, default='interaction')

# NotificationSettings modeli:
class NotificationSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    important_enabled = models.BooleanField(default=True)
    interaction_enabled = models.BooleanField(default=True)
    social_enabled = models.BooleanField(default=True)
    content_enabled = models.BooleanField(default=True)
    achievement_enabled = models.BooleanField(default=True)
    suggestion_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} bildirim ayarları"