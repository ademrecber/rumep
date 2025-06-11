from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
         help = 'Reset password for admin user'

         def handle(self, *args, **kwargs):
             try:
                 user = User.objects.get(username='ademr')
                 user.password = make_password('Adre86312')
                 user.save()
                 self.stdout.write(self.style.SUCCESS('Password reset successfully for ademr'))
             except User.DoesNotExist:
                 user = User.objects.create_superuser(
                     username='ademr',
                     email='email@example.com',
                     password='Adre86312'
                 )
                 self.stdout.write(self.style.SUCCESS('Created new admin user: ademr'))