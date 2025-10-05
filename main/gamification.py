from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Achievement(models.Model):
    """Başarım sistemi"""
    ACHIEVEMENT_TYPES = [
        ('first_entry', _('İlk Entry')),
        ('popular_writer', _('Popüler Yazar')),
        ('daily_active', _('Günlük Aktif')),
        ('helpful_user', _('Yardımsever')),
        ('kurdish_expert', _('Kürtçe Uzmanı')),
        ('community_builder', _('Topluluk Kurucusu')),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=10, default='🏆')  # Emoji icon
    points = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.icon} {self.name}"

class UserAchievement(models.Model):
    """Kullanıcı başarımları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class DailyChallenge(models.Model):
    """Günlük görevler"""
    CHALLENGE_TYPES = [
        ('write_entry', _('Entry Yaz')),
        ('vote_content', _('İçerik Oyla')),
        ('add_word', _('Kelime Ekle')),
        ('help_translate', _('Çeviri Yap')),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    target_count = models.PositiveIntegerField(default=1)
    reward_points = models.PositiveIntegerField(default=5)
    date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} ({self.date})"

class UserChallenge(models.Model):
    """Kullanıcı görev takibi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    current_count = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'challenge')
    
    def progress_percentage(self):
        return min((self.current_count / self.challenge.target_count) * 100, 100)
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"

class Leaderboard(models.Model):
    """Liderlik tablosu"""
    PERIOD_CHOICES = [
        ('daily', _('Günlük')),
        ('weekly', _('Haftalık')),
        ('monthly', _('Aylık')),
        ('all_time', _('Tüm Zamanlar')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    points = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField()
    period_start = models.DateField()
    period_end = models.DateField()
    
    class Meta:
        unique_together = ('user', 'period', 'period_start')
        ordering = ['rank']
    
    def __str__(self):
        return f"#{self.rank} {self.user.username} ({self.period})"

# Gamification Helper Functions
class GamificationHelper:
    @staticmethod
    def check_achievements(user, action_type, **kwargs):
        """Kullanıcı aksiyonlarına göre başarım kontrolü"""
        achievements_to_check = {
            'first_entry': lambda u: u.entries.count() == 1,
            'popular_writer': lambda u: u.entries.count() >= 50,
            'daily_active': lambda u: True,  # Günlük giriş kontrolü
            'kurdish_expert': lambda u: u.sozluk_set.count() >= 100,
        }
        
        for achievement_type, check_func in achievements_to_check.items():
            if action_type == achievement_type and check_func(user):
                achievement = Achievement.objects.filter(
                    achievement_type=achievement_type, 
                    is_active=True
                ).first()
                
                if achievement:
                    UserAchievement.objects.get_or_create(
                        user=user,
                        achievement=achievement
                    )
    
    @staticmethod
    def update_daily_challenge(user, action_type):
        """Günlük görev ilerlemesi güncelle"""
        from django.utils import timezone
        today = timezone.now().date()
        
        challenges = DailyChallenge.objects.filter(
            date=today,
            challenge_type=action_type,
            is_active=True
        )
        
        for challenge in challenges:
            user_challenge, created = UserChallenge.objects.get_or_create(
                user=user,
                challenge=challenge
            )
            
            if not user_challenge.completed:
                user_challenge.current_count += 1
                
                if user_challenge.current_count >= challenge.target_count:
                    user_challenge.completed = True
                    user_challenge.completed_at = timezone.now()
                    
                    # Puan ver
                    if hasattr(user, 'profile'):
                        user.profile.katki_puani += challenge.reward_points
                        user.profile.save()
                
                user_challenge.save()
    
    @staticmethod
    def get_user_level(points):
        """Puana göre seviye hesapla"""
        if points < 100:
            return {'level': 1, 'title': 'Yeni Üye', 'icon': '🌱'}
        elif points < 500:
            return {'level': 2, 'title': 'Aktif Üye', 'icon': '🌿'}
        elif points < 1000:
            return {'level': 3, 'title': 'Deneyimli', 'icon': '🌳'}
        elif points < 2500:
            return {'level': 4, 'title': 'Uzman', 'icon': '⭐'}
        else:
            return {'level': 5, 'title': 'Usta', 'icon': '👑'}