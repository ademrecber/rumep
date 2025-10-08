from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile

class Command(BaseCommand):
    help = 'Profili olmayan kullanıcılar için profil oluşturur'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        created_count = 0
        
        for user in users_without_profile:
            Profile.objects.create(
                user=user,
                nickname=user.username,
                username=user.username
            )
            created_count += 1
            self.stdout.write(f'Profil oluşturuldu: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Toplam {created_count} profil oluşturuldu.')
        )