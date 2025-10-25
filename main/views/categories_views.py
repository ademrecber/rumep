from django.shortcuts import render
from django.db.models import Count
from main.models import Sozluk, Kisi, Sarki, Atasozu, Deyim, YerAdi, SarkiGrubu
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string

def categories_view(request):
    """Kategoriler sayfası - modern infinite scroll tasarım"""
    
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

def get_recent_content(request):
    """AJAX ile son içerikleri getir"""
    page = int(request.GET.get('page', 1))
    category = request.GET.get('category', 'all')
    
    # Tüm içerikleri birleştir
    all_items = []
    
    # Sozluk
    for item in Sozluk.objects.order_by('-eklenme_tarihi'):
        description = item.detay[:60] + '...' if len(item.detay) > 60 else item.detay
        all_items.append({
            'type': 'sozluk',
            'title': item.kelime,
            'description': description,
            'user': item.kullanici.profile.nickname,
            'date': item.eklenme_tarihi,
            'category_name': 'Ferheng',
            'category_url': 'sozluk_ana_sayfa',
            'icon': 'bi-book',
            'color': '#667eea',
            'url': f'/sozluk/kelime/{item.id}/'
        })
    
    # Kisi
    for item in Kisi.objects.order_by('-eklenme_tarihi'):
        # Biyografiden kesit al
        bio_text = item.biyografi.replace('<p>', '').replace('</p>', '').replace('<br>', ' ')
        description = bio_text[:80] + '...' if len(bio_text) > 80 else bio_text
        all_items.append({
            'type': 'kisi',
            'title': item.ad,
            'description': description,
            'user': item.kullanici.profile.nickname,
            'date': item.eklenme_tarihi,
            'category_name': 'Kes',
            'category_url': 'kisi_liste',
            'icon': 'bi-people',
            'color': '#764ba2',
            'url': f'/kisi/detay/{item.id}/'
        })
    
    # Sarki
    for item in Sarki.objects.select_related('sarki_grubu__album__kisi').order_by('-sarki_grubu__eklenme_tarihi'):
        # Sanatçı bilgisi
        artist_name = item.sarki_grubu.album.kisi.ad if item.sarki_grubu.album else 'Bilinmeyen Sanatçı'
        description = f'{artist_name} - {item.get_dil_display()}'
        all_items.append({
            'type': 'sarki',
            'title': item.sarki_grubu.ad,
            'description': description,
            'user': item.sarki_grubu.kullanici.profile.nickname,
            'date': item.sarki_grubu.eklenme_tarihi,
            'category_name': 'Gotinên Stranan',
            'category_url': 'sarki_sozleri',
            'icon': 'bi-music-note-list',
            'color': '#f093fb',
            'url': f'/sarki/detay/{item.id}/'
        })
    
    # Atasozu
    for item in Atasozu.objects.order_by('-eklenme_tarihi'):
        # Anlamından kesit
        meaning = item.anlami[:60] + '...' if len(item.anlami) > 60 else item.anlami
        all_items.append({
            'type': 'atasozu',
            'title': item.kelime[:40] + '...' if len(item.kelime) > 40 else item.kelime,
            'description': meaning,
            'user': item.kullanici.profile.nickname,
            'date': item.eklenme_tarihi,
            'category_name': 'Gotinên Pêşiyan',
            'category_url': 'atasozu_deyim',
            'icon': 'bi-quote',
            'color': '#f5576c',
            'url': f'/atasozu-deyim/atasozu/{item.id}/'
        })
    
    # Yer Adi
    for item in YerAdi.objects.order_by('-eklenme_tarihi'):
        # Bölge ve kategori bilgisi
        region_info = f'{item.get_bolge_display()} - {item.get_kategori_display()}'
        all_items.append({
            'type': 'yer_adi',
            'title': item.ad,
            'description': region_info,
            'user': item.kullanici.profile.nickname,
            'date': item.eklenme_tarihi,
            'category_name': 'Navên Cîhan',
            'category_url': 'yer_adlari_anasayfa',
            'icon': 'bi-geo-alt',
            'color': '#4facfe',
            'url': f'/yer-adi/{item.id}/'
        })
    
    # Tarihe göre sırala
    all_items.sort(key=lambda x: x['date'], reverse=True)
    
    # Kategori filtresi
    if category != 'all':
        all_items = [item for item in all_items if item['category_url'] == category]
    
    # Pagination
    paginator = Paginator(all_items, 10)
    page_obj = paginator.get_page(page)
    
    return JsonResponse({
        'items': list(page_obj),
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None
    })