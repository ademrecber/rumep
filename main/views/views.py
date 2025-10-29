from .topic_views import home
from .popular_views import popular, load_more_popular, agenda, load_more_agenda
from .profile_views import login_page, complete_profile, profile, update_profile, search
from .sozluk_views import sozluk_ana_sayfa, sozluk_harf, sozluk_harf_yukle, sozluk_kelime, sozluk_kelime_sil, sozluk_kelime_duzenle, sozluk_kelime_veri, sozluk_detay_ekle, sozluk_detay_sil, sozluk_detay_duzenle, sozluk_detay_veri, sozluk_ara, sozluk_tum_kelimeler
from .kisi_views import kisi_detay, kisi_ekle, kisi_liste, kisi_liste_yukle, kisi_sil, kisi_duzenle, kisi_detay_ekle, kisi_detay_sil, kisi_detay_duzenle, kisi_detay_veri
from .sarki_views import sarki_kisi_ara, sarki_album_liste, sarki_liste, sarki_detay, sarki_sil, sarki_sozleri, sarki_ekle, sarki_album_sil, sarki_album_ekle, sarki_detay_veri, sarki_album_degistir, sarki_detay_ekle, sarki_detay_duzenle, sarki_detay_sil, sarki_album_degistir_veri,sarki_album_degistir, sarki_ara, sarki_detay_duzenle, sarki_duzenle,sarki_duzenle_kaydet, sarki_detay_seo
from .atasozu_deyim_views import atasozu_deyim, atasozu_deyim_detay, atasozu_deyim_sil, atasozu_deyim_ekle, atasozu_deyim_duzenle, atasozu_deyim_detay_veri, atasozu_deyim_ara,atasozu_deyim_detay_duzenle,atasozu_deyim_detay_ekle,atasozu_deyim_detay_sil
from .katki_views import load_more_liderler, load_more_katkilar
from .base import profile_required
from .notification_views import notifications, mark_as_read, mark_all_as_read
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'main/404.html', status=404)

def offline_page(request):
    return render(request, 'main/offline.html')

def csrf_failure(request, reason=""):
    from django.http import JsonResponse
    if request.content_type == 'application/json':
        return JsonResponse({'error': 'CSRF token missing or incorrect'}, status=403)
    return render(request, 'main/csrf_failure.html', {'reason': reason}, status=403)

def privacy_policy(request):
    return render(request, 'main/privacy.html')

def terms_of_service(request):
    return render(request, 'main/terms.html')

# SEO uyumlu slug view'ları
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from ..models import Kisi, Sozluk, Atasozu, Deyim

@login_required
@csrf_protect
def kisi_detay_slug(request, slug):
    kisi = get_object_or_404(Kisi, slug=slug)
    detaylar = kisi.detaylar.all()
    return render(request, 'main/kisi/kisi_detay.html', {
        'kisi': kisi,
        'detaylar': detaylar
    })

@login_required
@csrf_protect
def sozluk_kelime_slug(request, slug):
    kelime = get_object_or_404(Sozluk, slug=slug)
    detaylar = kelime.detaylar.all()
    return render(request, 'main/sozluk/sozluk_kelime.html', {
        'kelime': kelime,
        'detaylar': detaylar
    })

@login_required
@csrf_protect
def atasozu_detay_slug(request, slug):
    atasozu = get_object_or_404(Atasozu, slug=slug)
    detaylar = atasozu.detaylar.all()
    return render(request, 'main/atasozu_deyim/atasozu_deyim_detay.html', {
        'item': atasozu,
        'detaylar': detaylar,
        'tur': 'atasozu'
    })

@login_required
@csrf_protect
def kisi_detay_seo(request, kisi_adi):
    from urllib.parse import unquote
    kisi_adi = unquote(kisi_adi)
    kisi_adi = kisi_adi.replace('-', ' ')
    kisi = get_object_or_404(Kisi, ad__iexact=kisi_adi)
    detaylar = kisi.detaylar.all()
    return render(request, 'main/kisi/kisi_detay.html', {
        'kisi': kisi,
        'detaylar': detaylar
    })

@login_required
@csrf_protect
def sozluk_kelime_seo(request, kelime_adi):
    from urllib.parse import unquote
    kelime_adi = unquote(kelime_adi)
    kelime_adi = kelime_adi.replace('-', ' ')
    kelime = get_object_or_404(Sozluk, kelime__iexact=kelime_adi)
    detaylar = kelime.detaylar.all()
    return render(request, 'main/sozluk/sozluk_kelime.html', {
        'kelime': kelime,
        'detaylar': detaylar
    })

@login_required
@csrf_protect
def atasozu_detay_seo(request, atasozu_metni):
    from urllib.parse import unquote
    atasozu_metni = unquote(atasozu_metni)
    atasozu_metni = atasozu_metni.replace('-', ' ')
    atasozu = get_object_or_404(Atasozu, kelime__iexact=atasozu_metni)
    detaylar = atasozu.detaylar.all()
    return render(request, 'main/atasozu_deyim/atasozu_deyim_detay.html', {
        'item': atasozu,
        'detaylar': detaylar,
        'tur': 'atasozu'
    })

@login_required
@csrf_protect
def deyim_detay_seo(request, deyim_metni):
    from urllib.parse import unquote
    deyim_metni = unquote(deyim_metni)
    deyim_metni = deyim_metni.replace('-', ' ')
    deyim = get_object_or_404(Deyim, kelime__iexact=deyim_metni)
    detaylar = deyim.detaylar.all()
    return render(request, 'main/atasozu_deyim/atasozu_deyim_detay.html', {
        'item': deyim,
        'detaylar': detaylar,
        'tur': 'deyim'
    })