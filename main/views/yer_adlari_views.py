from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from ..models import YerAdi, YerAdiDetay
from ..forms import YerAdiForm, YerAdiDetayForm
from .base import profile_required
import bleach
from django.conf import settings

def yer_adlari_anasayfa(request):
    harf = request.GET.get('harf', '').upper()
    kategori = request.GET.get('kategori', '')
    yer_adlari = YerAdi.objects.all().order_by('ad')
    
    if harf:
        yer_adlari = yer_adlari.filter(ad__istartswith=harf)
    if kategori:
        yer_adlari = yer_adlari.filter(kategori=kategori)
    
    def add_children_recursive(yer_list):
        """Her yer için alt yerlerini recursive olarak ekle"""
        for yer in yer_list:
            children = yer_adlari.filter(parent=yer).order_by('kategori', 'ad')
            yer.manual_children = list(children)
            if children:
                add_children_recursive(children)
    
    # Bölgelere göre gruplandırma ve recursive hiyerarşik yapı
    bolgeler = {}
    for bolge_key in ['bakur', 'basur', 'rojava', 'rojhilat']:
        # Sadece il kategorisindeki yerleri al (ana yerler)
        iller = yer_adlari.filter(bolge=bolge_key, kategori='il').order_by('ad')
        
        # Her il için recursive olarak tüm alt hiyerarşiyi oluştur
        add_children_recursive(iller)
        
        bolgeler[bolge_key] = iller
    
    context = {
        'yer_adlari': yer_adlari,
        'bolgeler': bolgeler,
        'kategoriler': [choice[0] for choice in YerAdi.kategori.field.choices],
        'harfler': [chr(i) for i in range(65, 91)],  # A-Z
        'secili_harf': harf,
        'secili_kategori': kategori,
    }
    return render(request, 'main/yer_adlari/yer_adlari.html', context)

@login_required
@profile_required
@csrf_protect
def yer_adi_ekle(request):
    if request.method == 'POST':
        form = YerAdiForm(request.POST)
        if form.is_valid():
            if form.errors.get('ad', {}).get('duplicate'):
                if request.POST.get('confirm_duplicate') == 'true':
                    yer_adi = form.save(commit=False)
                    yer_adi.kullanici = request.user
                    yer_adi.save()
                    return redirect('yer_adi_detay', yer_adi_id=yer_adi.id)
                else:
                    return render(request, 'main/yer_adlari/yer_adi_ekle.html', {
                        'form': form,
                        'duplicate_warning': True,
                    })
            else:
                yer_adi = form.save(commit=False)
                yer_adi.kullanici = request.user
                yer_adi.save()
                return redirect('yer_adi_detay', yer_adi_id=yer_adi.id)
        else:
            return render(request, 'main/yer_adlari/yer_adi_ekle.html', {
                'form': form,
                'duplicate_warning': form.errors.get('ad', {}).get('duplicate'),
                'errors': form.errors,
            })
    else:
        form = YerAdiForm()
    
    context = {
        'form': form,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'main/yer_adlari/yer_adi_ekle.html', context)

@csrf_protect
def yer_adi_detay(request, yer_adi_id):
    yer_adi = get_object_or_404(YerAdi, id=yer_adi_id)
    detaylar = YerAdiDetay.objects.filter(yer_adi=yer_adi).order_by('-eklenme_tarihi')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login_page')
        form = YerAdiDetayForm(request.POST)
        if form.is_valid() and request.user != yer_adi.kullanici:
            detay = form.save(commit=False)
            detay.yer_adi = yer_adi
            detay.kullanici = request.user
            detay.detay = bleach.clean(detay.detay, tags=['p', 'b', 'i'], strip=True)
            detay.save()
            return redirect('yer_adi_detay', yer_adi_id=yer_adi.id)
    else:
        form = YerAdiDetayForm()
    
    context = {
        'yer_adi': yer_adi,
        'detaylar': detaylar,
        'form': form,
        'is_owner': yer_adi.kullanici == request.user,
        'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY',  # Google Maps API anahtarını buraya ekle
    }
    return render(request, 'main/yer_adlari/yer_adi_detay.html', context)

@login_required
@profile_required
@csrf_protect
def yer_adi_duzenle(request, yer_adi_id):
    yer_adi = get_object_or_404(YerAdi, id=yer_adi_id)
    if yer_adi.kullanici != request.user:
        return redirect('yer_adi_detay', yer_adi_id=yer_adi.id)
    
    if request.method == 'POST':
        form = YerAdiForm(request.POST, instance=yer_adi)
        if form.is_valid():
            if form.errors.get('ad', {}).get('duplicate'):
                if request.POST.get('confirm_duplicate') == 'true':
                    yer_adi = form.save()
                    return redirect('yer_adi_detay', yer_adi_id=yer_adi.id)
                else:
                    return render(request, 'main/yer_adlari/yer_adi_ekle.html', {
                        'form': form,
                        'duplicate_warning': True,
                        'is_edit': True,
                    })
            else:
                yer_adi = form.save()
                return redirect('yer_adi_detay', yer_adi_id=yer_adi.id)
        else:
            return render(request, 'main/yer_adlari/yer_adi_ekle.html', {
                'form': form,
                'duplicate_warning': form.errors.get('ad', {}).get('duplicate'),
                'errors': form.errors,
                'is_edit': True,
            })
    else:
        form = YerAdiForm(instance=yer_adi)
    
    context = {
        'form': form,
        'yer_adi': yer_adi,
        'is_edit': True,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'main/yer_adlari/yer_adi_ekle.html', context)

@login_required
@profile_required
@csrf_protect
def yer_adi_sil(request, yer_adi_id):
    yer_adi = get_object_or_404(YerAdi, id=yer_adi_id)
    if yer_adi.kullanici == request.user:
        yer_adi.delete()
    return redirect('yer_adlari_anasayfa')

@login_required
@profile_required
@csrf_protect
def yer_adi_detay_duzenle(request, detay_id):
    detay = get_object_or_404(YerAdiDetay, id=detay_id)
    if detay.kullanici != request.user:
        return redirect('yer_adi_detay', yer_adi_id=detay.yer_adi.id)
    
    if request.method == 'POST':
        form = YerAdiDetayForm(request.POST, instance=detay)
        if form.is_valid():
            detay = form.save(commit=False)
            detay.detay = bleach.clean(detay.detay, tags=['p', 'b', 'i'], strip=True)
            detay.save()
            return redirect('yer_adi_detay', yer_adi_id=detay.yer_adi.id)
    else:
        form = YerAdiDetayForm(instance=detay)
    
    context = {
        'form': form,
        'yer_adi': detay.yer_adi,
        'is_edit': True,
    }
    return render(request, 'main/yer_adlari/yer_adi_detay.html', context)

@login_required
@profile_required
@csrf_protect
def yer_adi_detay_sil(request, detay_id):
    detay = get_object_or_404(YerAdiDetay, id=detay_id)
    if detay.kullanici == request.user:
        yer_adi_id = detay.yer_adi.id
        detay.delete()
        return redirect('yer_adi_detay', yer_adi_id=yer_adi_id)
    return redirect('yer_adi_detay', yer_adi_id=detay.yer_adi.id)

@csrf_protect
def yer_adi_detay_slug(request, slug):
    yer_adi = get_object_or_404(YerAdi, slug=slug)
    detaylar = YerAdiDetay.objects.filter(yer_adi=yer_adi).order_by('-eklenme_tarihi')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login_page')
        form = YerAdiDetayForm(request.POST)
        if form.is_valid() and request.user != yer_adi.kullanici:
            detay = form.save(commit=False)
            detay.yer_adi = yer_adi
            detay.kullanici = request.user
            detay.detay = bleach.clean(detay.detay, tags=['p', 'b', 'i'], strip=True)
            detay.save()
            return redirect('yer_adi_detay_slug', slug=yer_adi.slug)
    else:
        form = YerAdiDetayForm()
    
    context = {
        'yer_adi': yer_adi,
        'detaylar': detaylar,
        'form': form,
        'is_owner': yer_adi.kullanici == request.user,
        'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY',
    }
    return render(request, 'main/yer_adlari/yer_adi_detay.html', context)

@csrf_protect
def yer_adi_detay_seo(request, yer_adi):
    yer_adi_obj = get_object_or_404(YerAdi, ad__iexact=yer_adi.replace('-', ' '))
    detaylar = YerAdiDetay.objects.filter(yer_adi=yer_adi_obj).order_by('-eklenme_tarihi')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login_page')
        form = YerAdiDetayForm(request.POST)
        if form.is_valid() and request.user != yer_adi_obj.kullanici:
            detay = form.save(commit=False)
            detay.yer_adi = yer_adi_obj
            detay.kullanici = request.user
            detay.detay = bleach.clean(detay.detay, tags=['p', 'b', 'i'], strip=True)
            detay.save()
            return redirect('yer_adi_detay_seo', yer_adi=yer_adi)
    else:
        form = YerAdiDetayForm()
    
    context = {
        'yer_adi': yer_adi_obj,
        'detaylar': detaylar,
        'form': form,
        'is_owner': yer_adi_obj.kullanici == request.user,
        'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY',
    }
    return render(request, 'main/yer_adlari/yer_adi_detay.html', context)