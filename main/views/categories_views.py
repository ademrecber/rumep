from django.shortcuts import render
from django.db.models import Count
from main.models import Sozluk, Kisi, Sarki, Atasozu, Deyim, YerAdi

def categories_view(request):
    """Kategoriler sayfası - tüm kategorilerin linkleri ve içerik sayıları"""
    
    # Her kategorinin içerik sayısını hesapla
    categories = [
        {
            'name': 'Ferheng',
            'description': 'Kürtçe-Türkçe Sözlük',
            'icon': 'bi-book',
            'url': 'sozluk_ana_sayfa',
            'count': Sozluk.objects.count(),
            'color': '#667eea'
        },
        {
            'name': 'Kes',
            'description': 'Ünlü Kişiler',
            'icon': 'bi-people',
            'url': 'kisi_liste',
            'count': Kisi.objects.count(),
            'color': '#764ba2'
        },
        {
            'name': 'Gotinên Stranan',
            'description': 'Şarkı Sözleri',
            'icon': 'bi-music-note-list',
            'url': 'sarki_sozleri',
            'count': Sarki.objects.count(),
            'color': '#f093fb'
        },
        {
            'name': 'Gotinên Pêşiyan û Îdîom',
            'description': 'Atasözleri ve Deyimler',
            'icon': 'bi-quote',
            'url': 'atasozu_deyim',
            'count': Atasozu.objects.count() + Deyim.objects.count(),
            'color': '#f5576c'
        },
        {
            'name': 'Navên Cîhan',
            'description': 'Yer Adları',
            'icon': 'bi-geo-alt',
            'url': 'yer_adlari_anasayfa',
            'count': YerAdi.objects.count(),
            'color': '#4facfe'
        }
    ]
    
    context = {
        'categories': categories,
        'total_content': sum(cat['count'] for cat in categories)
    }
    
    return render(request, 'main/categories.html', context)