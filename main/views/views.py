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
from django.views.decorators.http import require_POST
from ..models import Kisi, Sozluk, Atasozu, Deyim
from ..forms import KisiForm

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

@login_required
@csrf_protect
def kisi_duzenle_seo(request, kisi_adi):
    from urllib.parse import unquote
    kisi_adi = unquote(kisi_adi)
    kisi_adi = kisi_adi.replace('-', ' ')
    kisi = get_object_or_404(Kisi, ad__iexact=kisi_adi)
    if kisi.kullanici != request.user:
        return redirect('kisi_detay_seo', kisi_adi=kisi.ad.replace(' ', '-'))
    
    if request.method == 'POST':
        form = KisiForm(request.POST, instance=kisi)
        if form.is_valid():
            form.save()
            return redirect('kisi_detay_seo', kisi_adi=kisi.ad.replace(' ', '-'))
    else:
        form = KisiForm(instance=kisi)
    
    return render(request, 'main/kisi/kisi_duzenle.html', {
        'form': form,
        'kisi': kisi
    })

@login_required
@require_POST
def kisi_sil_seo(request, kisi_adi):
    from urllib.parse import unquote
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    
    kisi_adi = unquote(kisi_adi)
    kisi_adi = kisi_adi.replace('-', ' ')
    kisi = get_object_or_404(Kisi, ad__iexact=kisi_adi)
    
    if kisi.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Yetkiniz yok'}, status=403)
    
    kisi.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def atasozu_sil_seo(request, atasozu_metni):
    from urllib.parse import unquote
    atasozu_metni = unquote(atasozu_metni).replace('-', ' ')
    atasozu = get_object_or_404(Atasozu, kelime__iexact=atasozu_metni)
    if atasozu.kullanici == request.user:
        atasozu.delete()
    return redirect('atasozu_deyim')

@login_required
@require_POST
def deyim_sil_seo(request, deyim_metni):
    from urllib.parse import unquote
    deyim_metni = unquote(deyim_metni).replace('-', ' ')
    deyim = get_object_or_404(Deyim, kelime__iexact=deyim_metni)
    if deyim.kullanici == request.user:
        deyim.delete()
    return redirect('atasozu_deyim')

# Kişi detay işlemleri için SEO URL'ler
@login_required
@csrf_protect
def kisi_detay_ekle_seo(request, kisi_adi):
    from urllib.parse import unquote
    from django.http import JsonResponse
    from ..forms import KisiDetayForm
    
    kisi_adi = unquote(kisi_adi).replace('-', ' ')
    kisi = get_object_or_404(Kisi, ad__iexact=kisi_adi)
    
    if request.method == 'POST':
        form = KisiDetayForm(request.POST)
        if form.is_valid():
            detay = form.save(commit=False)
            detay.kisi = kisi
            detay.kullanici = request.user
            detay.save()
            return redirect('kisi_detay_seo', kisi_adi=kisi.ad.replace(' ', '-'))
    
    return redirect('kisi_detay_seo', kisi_adi=kisi.ad.replace(' ', '-'))

@login_required
def kisi_detay_veri_seo(request, kisi_adi, detay_id):
    from urllib.parse import unquote
    from django.http import JsonResponse
    from ..models import KisiDetay
    
    kisi_adi = unquote(kisi_adi).replace('-', ' ')
    kisi = get_object_or_404(Kisi, ad__iexact=kisi_adi)
    detay = get_object_or_404(KisiDetay, id=detay_id, kisi=kisi)
    
    if detay.kullanici != request.user:
        return JsonResponse({'error': 'Yetkiniz yok'}, status=403)
    
    return JsonResponse({
        'detay': detay.detay
    })

@login_required
@require_POST
def kisi_detay_sil_seo(request, kisi_adi, detay_id):
    from urllib.parse import unquote
    from django.http import JsonResponse
    from ..models import KisiDetay
    
    kisi_adi = unquote(kisi_adi).replace('-', ' ')
    kisi = get_object_or_404(Kisi, ad__iexact=kisi_adi)
    detay = get_object_or_404(KisiDetay, id=detay_id, kisi=kisi)
    
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Yetkiniz yok'}, status=403)
    
    detay.delete()
    return JsonResponse({'success': True})

# Yer adları için SEO URL'ler
from ..models import YerAdi

@login_required
def yer_adi_detay_seo(request, yer_adi):
    from urllib.parse import unquote
    yer_adi = unquote(yer_adi).replace('-', ' ')
    yer = get_object_or_404(YerAdi, ad__iexact=yer_adi)
    detaylar = yer.detaylar.all()
    return render(request, 'main/yer_adlari/yer_adi_detay.html', {
        'yer_adi': yer,
        'detaylar': detaylar,
        'is_owner': yer.kullanici == request.user
    })

@login_required
def yer_adi_duzenle_seo(request, yer_adi):
    from urllib.parse import unquote
    from ..forms import YerAdiForm
    
    yer_adi = unquote(yer_adi).replace('-', ' ')
    yer = get_object_or_404(YerAdi, ad__iexact=yer_adi)
    
    if yer.kullanici != request.user:
        return redirect('yer_adi_detay_seo', yer_adi=yer.ad.replace(' ', '-'))
    
    if request.method == 'POST':
        form = YerAdiForm(request.POST, instance=yer)
        if form.is_valid():
            form.save()
            return redirect('yer_adi_detay_seo', yer_adi=yer.ad.replace(' ', '-'))
    else:
        form = YerAdiForm(instance=yer)
    
    return render(request, 'main/yer_adlari/yer_adi_duzenle.html', {
        'form': form,
        'yer_adi': yer
    })

@login_required
@require_POST
def yer_adi_sil_seo(request, yer_adi):
    from urllib.parse import unquote
    yer_adi = unquote(yer_adi).replace('-', ' ')
    yer = get_object_or_404(YerAdi, ad__iexact=yer_adi)
    
    if yer.kullanici == request.user:
        yer.delete()
    
    return redirect('yer_adlari_anasayfa')

@login_required
def yer_adi_detay_duzenle_seo(request, yer_adi, detay_id):
    from urllib.parse import unquote
    from ..models import YerAdiDetay
    from ..forms import YerAdiDetayForm
    
    yer_adi = unquote(yer_adi).replace('-', ' ')
    yer = get_object_or_404(YerAdi, ad__iexact=yer_adi)
    detay = get_object_or_404(YerAdiDetay, id=detay_id, yer_adi=yer)
    
    if detay.kullanici != request.user:
        return redirect('yer_adi_detay_seo', yer_adi=yer.ad.replace(' ', '-'))
    
    if request.method == 'POST':
        form = YerAdiDetayForm(request.POST, instance=detay)
        if form.is_valid():
            form.save()
            return redirect('yer_adi_detay_seo', yer_adi=yer.ad.replace(' ', '-'))
    else:
        form = YerAdiDetayForm(instance=detay)
    
    return render(request, 'main/yer_adlari/yer_adi_detay_duzenle.html', {
        'form': form,
        'yer_adi': yer,
        'detay': detay
    })

@login_required
@require_POST
def yer_adi_detay_sil_seo(request, yer_adi, detay_id):
    from urllib.parse import unquote
    from ..models import YerAdiDetay
    
    yer_adi = unquote(yer_adi).replace('-', ' ')
    yer = get_object_or_404(YerAdi, ad__iexact=yer_adi)
    detay = get_object_or_404(YerAdiDetay, id=detay_id, yer_adi=yer)
    
    if detay.kullanici == request.user:
        detay.delete()
    
    return redirect('yer_adi_detay_seo', yer_adi=yer.ad.replace(' ', '-'))

# Sözlük için SEO URL'ler
@login_required
def sozluk_kelime_veri_seo(request, kelime_adi):
    from urllib.parse import unquote
    from django.http import JsonResponse
    
    kelime_adi = unquote(kelime_adi).replace('-', ' ')
    kelime = get_object_or_404(Sozluk, kelime__iexact=kelime_adi)
    
    if kelime.kullanici != request.user:
        return JsonResponse({'error': 'Yetkiniz yok'}, status=403)
    
    return JsonResponse({
        'kelime': kelime.kelime,
        'detay': kelime.detay,
        'turkce_karsiligi': kelime.turkce_karsiligi or '',
        'ingilizce_karsiligi': kelime.ingilizce_karsiligi or '',
        'tur': kelime.tur or ''
    })

@login_required
@require_POST
def sozluk_kelime_sil_seo(request, kelime_adi):
    from urllib.parse import unquote
    from django.http import JsonResponse
    
    kelime_adi = unquote(kelime_adi).replace('-', ' ')
    kelime = get_object_or_404(Sozluk, kelime__iexact=kelime_adi)
    
    if kelime.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Yetkiniz yok'}, status=403)
    
    kelime.delete()
    return JsonResponse({'success': True})

@login_required
@csrf_protect
def sozluk_kelime_duzenle_seo(request, kelime_adi):
    from urllib.parse import unquote
    from django.http import JsonResponse
    from ..forms import SozlukForm
    
    kelime_adi = unquote(kelime_adi).replace('-', ' ')
    kelime = get_object_or_404(Sozluk, kelime__iexact=kelime_adi)
    
    if kelime.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Yetkiniz yok'}, status=403)
    
    if request.method == 'POST':
        form = SozlukForm(request.POST, instance=kelime)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'})

@login_required
@csrf_protect
def sozluk_detay_ekle_seo(request, kelime_adi):
    from urllib.parse import unquote
    from ..forms import SozlukDetayForm
    
    kelime_adi = unquote(kelime_adi).replace('-', ' ')
    kelime = get_object_or_404(Sozluk, kelime__iexact=kelime_adi)
    
    if request.method == 'POST':
        form = SozlukDetayForm(request.POST)
        if form.is_valid():
            detay = form.save(commit=False)
            detay.kelime = kelime
            detay.kullanici = request.user
            detay.save()
            return redirect('sozluk_kelime_seo', kelime_adi=kelime.kelime.replace(' ', '-'))
    
    return redirect('sozluk_kelime_seo', kelime_adi=kelime.kelime.replace(' ', '-'))

@login_required
def sozluk_detay_veri_seo(request, kelime_adi, detay_id):
    from urllib.parse import unquote
    from django.http import JsonResponse
    from ..models import SozlukDetay
    
    kelime_adi = unquote(kelime_adi).replace('-', ' ')
    kelime = get_object_or_404(Sozluk, kelime__iexact=kelime_adi)
    detay = get_object_or_404(SozlukDetay, id=detay_id, kelime=kelime)
    
    if detay.kullanici != request.user:
        return JsonResponse({'error': 'Yetkiniz yok'}, status=403)
    
    return JsonResponse({
        'detay': detay.detay
    })

@login_required
@require_POST
def sozluk_detay_sil_seo(request, kelime_adi, detay_id):
    from urllib.parse import unquote
    from django.http import JsonResponse
    from ..models import SozlukDetay
    
    kelime_adi = unquote(kelime_adi).replace('-', ' ')
    kelime = get_object_or_404(Sozluk, kelime__iexact=kelime_adi)
    detay = get_object_or_404(SozlukDetay, id=detay_id, kelime=kelime)
    
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Yetkiniz yok'}, status=403)
    
    detay.delete()
    return JsonResponse({'success': True})