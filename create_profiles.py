#!/usr/bin/env python
import os
import sys
import django

# Django ayarlarını yükle
sys.path.append('c:\\Users\\ademr\\OneDrive\\Masaüstü\\projelerim\\rumep')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rumep.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Profile

# Profili olmayan kullanıcıları bul ve profil oluştur
users_without_profile = []
for user in User.objects.all():
    try:
        profile = user.profile
    except:
        users_without_profile.append(user)
        Profile.objects.create(
            user=user,
            nickname=user.username,
            username=user.username
        )
        print(f"Profil oluşturuldu: {user.username}")

print(f"Toplam {len(users_without_profile)} kullanıcı için profil oluşturuldu.")