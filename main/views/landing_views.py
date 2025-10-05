from django.shortcuts import render
from django.db.models import Count
from ..models import Sozluk, Kisi, Sarki, Topic, Entry

def landing_page(request):
    """Yeni kullanıcılar için optimize edilmiş landing page"""
    
    # Hızlı istatistikler
    context = {
        'sozluk_count': Sozluk.objects.count(),
        'kisi_count': Kisi.objects.count(), 
        'sarki_count': Sarki.objects.count(),
        'topic_count': Topic.objects.count(),
        
        # Son eklenen içerikler (cache'lenebilir)
        'recent_sozluk': Sozluk.objects.select_related('kullanici').order_by('-eklenme_tarihi')[:5],
        
        # Popüler başlıklar
        'popular_topics': Topic.objects.annotate(
            entry_count=Count('entries')
        ).filter(entry_count__gt=0).order_by('-entry_count')[:5]
    }
    
    return render(request, 'main/landing.html', context)