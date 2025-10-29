from django.core.management.base import BaseCommand
from django.utils.text import slugify
from main.models import Sarki, Kisi, Sozluk, YerAdi, Atasozu, Deyim

class Command(BaseCommand):
    help = 'Generate slugs for existing records'

    def handle(self, *args, **options):
        # Şarkılar için slug oluştur
        for sarki in Sarki.objects.filter(slug__isnull=True):
            if sarki.sarki_grubu:
                base_slug = slugify(f"{sarki.sarki_grubu.ad}-{sarki.get_dil_display()}")
                slug = base_slug
                counter = 1
                while Sarki.objects.filter(slug=slug).exclude(pk=sarki.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                sarki.slug = slug
                sarki.save()
        
        # Kişiler için slug oluştur
        for kisi in Kisi.objects.filter(slug__isnull=True):
            base_slug = slugify(kisi.ad)
            slug = base_slug
            counter = 1
            while Kisi.objects.filter(slug=slug).exclude(pk=kisi.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            kisi.slug = slug
            kisi.save()
        
        # Sözlük için slug oluştur
        for sozluk in Sozluk.objects.filter(slug__isnull=True):
            base_slug = slugify(sozluk.kelime)
            slug = base_slug
            counter = 1
            while Sozluk.objects.filter(slug=slug).exclude(pk=sozluk.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            sozluk.slug = slug
            sozluk.save()
        
        # Yer adları için slug oluştur
        for yer in YerAdi.objects.filter(slug__isnull=True):
            base_slug = slugify(yer.ad)
            slug = base_slug
            counter = 1
            while YerAdi.objects.filter(slug=slug).exclude(pk=yer.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            yer.slug = slug
            yer.save()
        
        # Atasözleri için slug oluştur
        for atasozu in Atasozu.objects.filter(slug__isnull=True):
            base_slug = slugify(atasozu.kelime)
            slug = base_slug
            counter = 1
            while Atasozu.objects.filter(slug=slug).exclude(pk=atasozu.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            atasozu.slug = slug
            atasozu.save()
        
        # Deyimler için slug oluştur
        for deyim in Deyim.objects.filter(slug__isnull=True):
            base_slug = slugify(deyim.kelime)
            slug = base_slug
            counter = 1
            while Deyim.objects.filter(slug=slug).exclude(pk=deyim.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            deyim.slug = slug
            deyim.save()
        
        self.stdout.write(self.style.SUCCESS('Slugs generated successfully'))