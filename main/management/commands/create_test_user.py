from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile

class Command(BaseCommand):
    help = 'Test kullanıcısı oluşturur'

    def handle(self, *args, **options):
        # Test kullanıcısı oluştur
        if not User.objects.filter(username='test').exists():
            user = User.objects.create_user(
                username='test',
                email='test@test.com',
                password='test123'
            )
            
            # Profile oluştur
            Profile.objects.create(
                user=user,
                nickname='Test User',
                username='testuser'
            )
            
            self.stdout.write(
                self.style.SUCCESS('Test kullanıcısı oluşturuldu: test/test123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Test kullanıcısı zaten mevcut')
            )
        
        # Admin kullanıcısı oluştur
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@test.com',
                password='admin123'
            )
            
            # Profile oluştur
            Profile.objects.create(
                user=admin,
                nickname='Admin',
                username='admin'
            )
            
            self.stdout.write(
                self.style.SUCCESS('Admin kullanıcısı oluşturuldu: admin/admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin kullanıcısı zaten mevcut')
            )