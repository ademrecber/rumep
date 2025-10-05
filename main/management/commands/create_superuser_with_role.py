from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile

class Command(BaseCommand):
    help = 'Rol ile birlikte süper kullanıcı oluşturur'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Kullanıcı adı')
        parser.add_argument('--email', type=str, help='E-posta')
        parser.add_argument('--password', type=str, help='Şifre')
        parser.add_argument('--nickname', type=str, help='Takma ad')
        parser.add_argument('--role', type=str, default='super_admin', 
                          choices=['user', 'writer', 'moderator', 'admin', 'super_admin'],
                          help='Kullanıcı rolü')

    def handle(self, *args, **options):
        username = options['username'] or input('Kullanıcı adı: ')
        email = options['email'] or input('E-posta: ')
        password = options['password'] or input('Şifre: ')
        nickname = options['nickname'] or input('Takma ad: ')
        role = options['role']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'"{username}" kullanıcı adı zaten mevcut!')
            )
            return

        # Kullanıcı oluştur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        if role in ['admin', 'super_admin']:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        # Profile oluştur veya güncelle
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'nickname': nickname,
                'username': username,
                'user_role': role
            }
        )
        
        if not created:
            profile.user_role = role
            profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Kullanıcı "{username}" başarıyla oluşturuldu! Rol: {role}'
            )
        )