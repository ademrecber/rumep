from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Case, When, Value, IntegerField
from ..models import Atasozu, Deyim, AtasozuDeyimDetay
from django.core.exceptions import ValidationError
from ..forms import AtasozuDeyimForm, AtasozuDeyimAramaForm, AtasozuDeyimDetayForm, AtasozuDeyimDuzenleForm
import logging
import json

logger = logging.getLogger(__name__)

def atasozu_deyim(request):
    harf = request.GET.get('harf', '').lower()
    sekme = request.GET.get('sekme', 'atasozu')
    harfler = ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']
    
    atasozu_gruplari = []
    deyim_gruplari = []
    
    # Atasözleri için gruplar
    if sekme == 'atasozu' or not sekme:
        if harf:
            # Sadece seçili harfle başlayan atasözlerini al
            atasozleri = Atasozu.objects.filter(kelime__istartswith=harf).order_by('kelime')
            if atasozleri.exists():
                atasozu_gruplari.append((harf, atasozleri))
        else:
            # Tüm harfler için atasözlerini al
            for h in harfler:
                atasozleri = Atasozu.objects.filter(kelime__istartswith=h).order_by('kelime')
                if atasozleri.exists():
                    atasozu_gruplari.append((h, atasozleri))
    
    # Deyimler için gruplar
    if sekme == 'deyim':
        if harf:
            # Sadece seçili harfle başlayan deyimleri al
            deyimler = Deyim.objects.filter(kelime__istartswith=harf).order_by('kelime')
            if deyimler.exists():
                deyim_gruplari.append((harf, deyimler))
        else:
            # Tüm harfler için deyimleri al
            for h in harfler:
                deyimler = Deyim.objects.filter(kelime__istartswith=h).order_by('kelime')
                if deyimler.exists():
                    deyim_gruplari.append((h, deyimler))
    
    return render(request, 'main/atasozu_deyim/atasozu_deyim.html', {
        'harfler': harfler,
        'atasozu_gruplari': atasozu_gruplari,
        'deyim_gruplari': deyim_gruplari,
        'secili_harf': harf,
        'sekme': sekme,
        'arama_form': AtasozuDeyimAramaForm()
    })

@login_required
@csrf_protect
def atasozu_deyim_ekle(request):
    if request.method == 'POST':
        form = AtasozuDeyimForm(request.POST)
        if form.is_valid():
            tur = form.cleaned_data['tur']
            kelime = form.cleaned_data['kelime'].upper()
            anlami = form.cleaned_data['anlami']
            ornek = form.cleaned_data['ornek']
            
            if tur == 'atasozu':
                atasozu = Atasozu(
                    kelime=kelime,
                    anlami=anlami,
                    ornek=ornek,
                    kullanici=request.user
                )
                atasozu.save()
                logger.info(f"Atasözü eklendi: {kelime}, Kullanıcı: {request.user.profile.username}")
            else:
                deyim = Deyim(
                    kelime=kelime,
                    anlami=anlami,
                    ornek=ornek,
                    kullanici=request.user
                )
                deyim.save()
                logger.info(f"Deyim eklendi: {kelime}, Kullanıcı: {request.user.profile.username}")
            
            return JsonResponse({'success': True})
        # Hataları daha ayrıntılı döndürelim
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = [str(error) for error in error_list]
        return JsonResponse({'success': False, 'errors': errors})
    
    form = AtasozuDeyimForm()
    return render(request, 'main/atasozu_deyim/atasozu_deyim_ekle.html', {'form': form})

@login_required
@csrf_protect
def atasozu_deyim_detay(request, tur, id):
    if tur == 'atasozu':
        item = get_object_or_404(Atasozu, id=id)
    else:
        item = get_object_or_404(Deyim, id=id)
    
    detaylar = AtasozuDeyimDetay.objects.filter(**{tur: item})
    
    return render(request, 'main/atasozu_deyim/atasozu_deyim_detay.html', {
        'item': item,
        'tur': tur,
        'detaylar': detaylar,
        'detay_form': AtasozuDeyimDetayForm(),
        'duzenle_form': AtasozuDeyimDuzenleForm(instance=item)
        if request.user == item.kullanici else None
    })

@login_required
@csrf_protect
@require_POST
def atasozu_deyim_sil(request, tur, id):
    if tur == 'atasozu':
        item = get_object_or_404(Atasozu, id=id)
    else:
        item = get_object_or_404(Deyim, id=id)
    
    if item.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu öğeyi silme yetkiniz yok.'}, status=403)
    
    item.delete()
    logger.info(f"{tur.capitalize()} silindi: {item.kelime}, Kullanıcı: {request.user.profile.username}")
    return JsonResponse({'success': True})

@require_GET
@csrf_protect
def atasozu_deyim_ara(request):
    sekme = request.GET.get('sekme', 'atasozu')
    query = request.GET.get('query', '').strip()
    tarih_baslangic = request.GET.get('tarih_baslangic', '')
    tarih_bitis = request.GET.get('tarih_bitis', '')
    kullanici = request.GET.get('kullanici', '').strip()

    if sekme == 'atasozu':
        items = Atasozu.objects.all()
    else:
        items = Deyim.objects.all()

    # Arama: Hem başında eşleşen hem de içinde geçen sonuçları getir, ama başında eşleşenler öncelikli olsun
    if query:
        # Önce içinde geçen tüm sonuçları getir
        items = items.filter(
            Q(kelime__icontains=query) | Q(anlami__icontains=query)
        )
        # Sıralama: Başında eşleşenler üstte, sonra içinde geçenler
        items = items.annotate(
            match_priority=Case(
                When(kelime__istartswith=query, then=Value(1)),
                When(anlami__istartswith=query, then=Value(2)),
                default=Value(3),
                output_field=IntegerField()
            )
        ).order_by('match_priority', 'kelime')

    # Filtreleme: Tarih aralığı
    if tarih_baslangic:
        items = items.filter(eklenme_tarihi__gte=tarih_baslangic)
    if tarih_bitis:
        items = items.filter(eklenme_tarihi__lte=tarih_bitis)

    # Filtreleme: Kullanıcı
    if kullanici:
        items = items.filter(kullanici__username__iexact=kullanici)

    items = items[:20]  # İlk 20 sonucu al
    data = [{
        'id': item.id,
        'kelime': item.kelime,
        'anlami': item.anlami,
        'kullanici': item.kullanici.profile.username,
        'eklenme_tarihi': item.eklenme_tarihi.isoformat()
    } for item in items]

    return JsonResponse({'success': True, 'items': data})

@login_required
@csrf_protect
@require_POST
def atasozu_deyim_detay_ekle(request, tur, id):
    if tur == 'atasozu':
        parent_item = get_object_or_404(Atasozu, id=id)
    else: # Deyim olduğu varsayılır
        parent_item = get_object_or_404(Deyim, id=id)

    # Kullanıcı kendi atasözü/deyimine detay ekleyemez
    if parent_item.kullanici == request.user:
        return JsonResponse({'success': False, 'error': 'Kendi atasözü veya deyiminize detay ekleyemezsiniz.'}, status=403)

    # Formu işlemeden önce bir AtasozuDeyimDetay instance'ı oluşturun
    # ve atasozu veya deyim alanını ayarlayın.
    detay_instance = AtasozuDeyimDetay()
    if tur == 'atasozu':
        detay_instance.atasozu = parent_item
    else:
        detay_instance.deyim = parent_item
    
    # Bu instance'ı forma geçirin
    form = AtasozuDeyimDetayForm(request.POST, instance=detay_instance)

    if form.is_valid(): # Modelin clean metodu burada (form.is_valid içinde) çağrılacak
        detay = form.save(commit=False) # atasozu/deyim zaten instance üzerinde ayarlı
        detay.kullanici = request.user # Kullanıcıyı ayarla
        detay.save()
        logger.info(f"{tur.capitalize()} detayı eklendi: {parent_item.kelime}, Kullanıcı: {request.user.profile.username}")
        return JsonResponse({'success': True})
    
    # Form hatalarını JSON olarak döndür
    return JsonResponse({'success': False, 'errors': json.loads(form.errors.as_json())})

@login_required
@csrf_protect
@require_POST
def atasozu_deyim_detay_duzenle(request, detay_id):
    detay = get_object_or_404(AtasozuDeyimDetay, id=detay_id)
    
    # Sadece detayı ekleyen kullanıcı düzenleyebilir
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı düzenleme yetkiniz yok.'}, status=403)

    form = AtasozuDeyimDetayForm(request.POST, instance=detay)
    if form.is_valid():
        form.save()
        logger.info(f"Detay düzenlendi: ID {detay_id}, Kullanıcı: {request.user.profile.username}")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': json.loads(form.errors.as_json())})

@login_required
@csrf_protect
@require_POST
def atasozu_deyim_detay_sil(request, detay_id):
    detay = get_object_or_404(AtasozuDeyimDetay, id=detay_id)
    
    # Sadece detayı ekleyen kullanıcı silebilir
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı silme yetkiniz yok.'}, status=403)
    
    detay.delete()
    logger.info(f"Detay silindi: ID {detay_id}, Kullanıcı: {request.user.profile.username}")
    return JsonResponse({'success': True})

@login_required
@csrf_protect
@require_GET
def atasozu_deyim_detay_veri(request, detay_id):
    detay = get_object_or_404(AtasozuDeyimDetay, id=detay_id)
    
    # Sadece detayı ekleyen kullanıcı veriyi görebilir
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı düzenleme yetkiniz yok.'}, status=403)
    
    data = {
        'detay': detay.detay
    }
    return JsonResponse({'success': True, 'data': data})

@login_required
@csrf_protect
def atasozu_deyim_duzenle(request, tur, id):
    if tur == 'atasozu':
        item = get_object_or_404(Atasozu, id=id)
    else:
        item = get_object_or_404(Deyim, id=id)

    # Sadece öğeyi ekleyen kullanıcı düzenleyebilir
    if item.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu öğeyi düzenleme yetkiniz yok.'}, status=403)

    if request.method == 'POST':
        form = AtasozuDeyimDuzenleForm(request.POST, instance=item)
        if form.is_valid():
            kelime = form.cleaned_data['kelime'].upper()
            anlami = form.cleaned_data['anlami']
            ornek = form.cleaned_data['ornek']
            
            item.kelime = kelime
            item.anlami = anlami
            item.ornek = ornek
            item.save()
            logger.info(f"{tur.capitalize()} düzenlendi: {kelime}, Kullanıcı: {request.user.profile.username}")
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': json.loads(form.errors.as_json())})

    form = AtasozuDeyimDuzenleForm(instance=item)
    return JsonResponse({'success': True, 'form': {
        'kelime': form['kelime'].value(),
        'anlami': form['anlami'].value(),
        'ornek': form['ornek'].value()
    }})