from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile
import re

class Command(BaseCommand):
    help = 'Profile\'ı olmayan kullanıcılar için Profile oluşturur'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        
        for user in users_without_profile:
            # Kullanıcı adını temizle - sadece harf, rakam ve alt çizgi
            clean_username = re.sub(r'[^a-zA-Z0-9_]', '', user.username)
            if not clean_username:
                clean_username = f'user_{user.id}'
            
            # Benzersiz username oluştur
            base_username = clean_username
            counter = 1
            while Profile.objects.filter(username=clean_username).exists():
                clean_username = f'{base_username}_{counter}'
                counter += 1
            
            try:
                Profile.objects.create(
                    user=user,
                    nickname=user.username,
                    username=clean_username,
                    preferred_language='tr'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Profile created for user: {user.username} -> {clean_username}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating profile for {user.username}: {e}')
                )
        
        if not users_without_profile:
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles')
            )