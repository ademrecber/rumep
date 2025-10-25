#!/usr/bin/env python
import os
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rumep.settings')
django.setup()

from main.models import Sarki, SarkiGrubu

def migrate_old_songs():
    # Dil versiyonu olmayan şarkı gruplarını sil
    empty_groups = SarkiGrubu.objects.filter(dil_versiyonlari__isnull=True)
    print(f"Silinecek boş şarkı grubu sayısı: {empty_groups.count()}")
    empty_groups.delete()
    
    # sarki_grubu'su olmayan şarkıları sil
    orphan_songs = Sarki.objects.filter(sarki_grubu__isnull=True)
    print(f"Silinecek yetim şarkı sayısı: {orphan_songs.count()}")
    orphan_songs.delete()
    
    print("Temizlik tamamlandı!")

if __name__ == "__main__":
    migrate_old_songs()