from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile

class Command(BaseCommand):
    help = 'Profile\'ı olmayan kullanıcılar için Profile oluşturur'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        
        for user in users_without_profile:
            Profile.objects.create(
                user=user,
                nickname=user.username,
                username=user.username,
                preferred_language='tr'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Profile created for user: {user.username}')
            )
        
        if not users_without_profile:
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles')
            )