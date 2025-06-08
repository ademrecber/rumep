from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.db.models import Q
from ..models import Sozluk, SozlukDetay
from ..forms import SozlukForm, SozlukDetayForm
import bleach
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
def sozluk_ana_sayfa(request):
    if request.method == 'POST':
        form = SozlukForm(request.POST)
        if form.is_valid():
            sozluk = form.save(commit=False)
            sozluk.kullanici = request.user
            sozluk.kelime = bleach.clean(sozluk.kelime, tags=[], strip=True).lower()
            sozluk.detay = bleach.clean(sozluk.detay, tags=['p', 'br'], strip=True)
            sozluk.tur = bleach.clean(sozluk.tur, tags=[], strip=True)
            try:
                sozluk.save()
                logger.info(f"Kelime eklendi: {sozluk.kelime}, Kullanıcı: {request.user.username}")
                return JsonResponse({'success': True})
            except ValidationError as e:
                return JsonResponse({'success': False, 'errors': {field: errors[0] for field, errors in e.message_dict.items()}})
        return JsonResponse({'success': False, 'errors': {field: errors[0]['message'] for field, errors in form.errors.get_json_data().items()}})
    
    form = SozlukForm()
    harfler = ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']
    
    return render(request, 'main/sozluk/sozluk.html', {
        'form': form,
        'harfler': harfler
    })

def sozluk_harf(request, harf):
    if harf.lower() not in ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']:
        return redirect('sozluk_ana_sayfa')
    kelimeler = Sozluk.objects.filter(kelime__istartswith=harf).order_by('kelime')[:20]
    return render(request, 'main/sozluk/sozluk_harf.html', {'harf': harf, 'kelimeler': kelimeler, 'user': request.user})

@csrf_protect
def sozluk_harf_yukle(request):
    harf = request.GET.get('harf')
    offset = int(request.GET.get('offset', 0))
    limit = 20
    if harf.lower() not in ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']:
        return JsonResponse({'error': 'Geçersiz harf'}, status=400)
    kelimeler = Sozluk.objects.filter(kelime__istartswith=harf).order_by('kelime')[offset:offset + limit]
    data = [{
        'id': kelime.id,
        'kelime': kelime.kelime,
        'detay': kelime.detay[:100] + ('...' if len(kelime.detay) > 100 else ''),
        'is_owner': kelime.kullanici == request.user
    } for kelime in kelimeler]
    has_more = Sozluk.objects.filter(kelime__istartswith=harf).count() > offset + limit
    return JsonResponse({'kelimeler': data, 'has_more': has_more})

@csrf_protect
def sozluk_ara(request):
    query = request.GET.get('q', '').strip()
    tur = request.GET.get('tur', '').strip()
    offset = int(request.GET.get('offset', 0))
    limit = 20

    kelimeler = Sozluk.objects.all()
    if query:
        query = query.upper()  # Veri tabanında kelimeler büyük harfli
        kelimeler = kelimeler.filter(Q(kelime__istartswith=query) | Q(kelime__icontains=query))
    if tur:
        kelimeler = kelimeler.filter(tur=tur)
    
    kelimeler = kelimeler.order_by('kelime')[offset:offset + limit]
    data = [{
        'id': kelime.id,
        'kelime': kelime.kelime,
        'detay': kelime.detay[:100] + ('...' if len(kelime.detay) > 100 else ''),
        'tur': kelime.tur,
        'is_owner': kelime.kullanici == request.user
    } for kelime in kelimeler]
    has_more = Sozluk.objects.filter(Q(kelime__istartswith=query) | Q(kelime__icontains=query) & Q(tur=tur) if tur else Q(kelime__istartswith=query) | Q(kelime__icontains=query)).count() > offset + limit

    return JsonResponse({'kelimeler': data, 'has_more': has_more})

@csrf_protect
def sozluk_tum_kelimeler(request):
    offset = int(request.GET.get('offset', 0))
    limit = 20
    kelimeler = Sozluk.objects.all().order_by('kelime')[offset:offset + limit]
    data = [{
        'id': kelime.id,
        'kelime': kelime.kelime,
        'detay': kelime.detay[:100] + ('...' if len(kelime.detay) > 100 else ''),
        'tur': kelime.tur,
        'is_owner': kelime.kullanici == request.user
    } for kelime in kelimeler]
    has_more = Sozluk.objects.count() > offset + limit
    return JsonResponse({'kelimeler': data, 'has_more': has_more})

def sozluk_kelime(request, kelime_id):
    kelime = get_object_or_404(Sozluk, id=kelime_id)
    detaylar = SozlukDetay.objects.filter(kelime=kelime).order_by('-eklenme_tarihi')
    detay_form = SozlukDetayForm()
    return render(request, 'main/sozluk/sozluk_kelime.html', {
        'kelime': kelime,
        'detaylar': detaylar,
        'detay_form': detay_form,
        'user': request.user
    })

@login_required
@csrf_protect
def sozluk_kelime_sil(request, kelime_id):
    try:
        kelime = get_object_or_404(Sozluk, id=kelime_id)
        if kelime.kullanici != request.user:
            return JsonResponse({'success': False, 'error': 'Bu kelimeyi silme yetkiniz yok.'}, status=403)
        if request.method == 'POST':
            kelime.delete()
            logger.info(f"Kelime silindi: {kelime.kelime}, Kullanıcı: {request.user.username}")
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Geçersiz istek'}, status=400)
    except Sozluk.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Kelime bulunamadı.'}, status=404)

@login_required
@csrf_protect
def sozluk_kelime_duzenle(request, kelime_id):
    kelime = get_object_or_404(Sozluk, id=kelime_id)
    if kelime.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu kelimeyi düzenleme yetkiniz yok.'}, status=403)
    
    if request.method == 'POST':
        form = SozlukForm(request.POST, instance=kelime)
        if form.is_valid():
            sozluk = form.save(commit=False)
            sozluk.kelime = bleach.clean(sozluk.kelime, tags=[], strip=True).lower()
            sozluk.detay = bleach.clean(sozluk.detay, tags=['p', 'br'], strip=True)
            sozluk.tur = bleach.clean(sozluk.tur, tags=[], strip=True)
            try:
                sozluk.save()
                logger.info(f"Kelime düzenlendi: {sozluk.kelime}, Kullanıcı: {request.user.username}")
                return JsonResponse({'success': True})
            except ValidationError as e:
                return JsonResponse({'success': False, 'errors': {field: errors[0] for field, errors in e.message_dict.items()}})
        return JsonResponse({'success': False, 'errors': {field: errors[0]['message'] for field, errors in form.errors.get_json_data().items()}})
    
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'}, status=400)

@login_required
@csrf_protect
def sozluk_kelime_veri(request, kelime_id):
    kelime = get_object_or_404(Sozluk, id=kelime_id)
    if kelime.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu kelimeyi düzenleme yetkiniz yok.'}, status=403)
    return JsonResponse({
        'success': True,
        'kelime': kelime.kelime,
        'detay': kelime.detay,
        'tur': kelime.tur
    })

@login_required
@csrf_protect
def sozluk_detay_ekle(request, kelime_id):
    kelime = get_object_or_404(Sozluk, id=kelime_id)
    if kelime.kullanici == request.user:
        return JsonResponse({'success': False, 'error': 'Kendi kelimenize ek detay ekleyemezsiniz.'}, status=403)
    if request.method == 'POST':
        form = SozlukDetayForm(request.POST)
        if form.is_valid():
            detay = form.save(commit=False)
            detay.kelime = kelime
            detay.kullanici = request.user
            detay.detay = bleach.clean(detay.detay, tags=['p', 'br'], strip=True)
            try:
                detay.save()
                logger.info(f"Detay eklendi: Kelime {kelime.kelime}, Kullanıcı: {request.user.username}")
                return JsonResponse({'success': True})
            except ValidationError as e:
                return JsonResponse({'success': False, 'errors': {field: errors[0] for field, errors in e.message_dict.items()}})
        return JsonResponse({'success': False, 'errors': {field: errors[0]['message'] for field, errors in form.errors.get_json_data().items()}})
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'}, status=400)

@login_required
@csrf_protect
def sozluk_detay_sil(request, detay_id):
    detay = get_object_or_404(SozlukDetay, id=detay_id)
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı silme yetkiniz yok.'}, status=403)
    if request.method == 'POST':
        detay.delete()
        logger.info(f"Detay silindi: Kelime {detay.kelime.kelime}, Kullanıcı: {request.user.username}")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'}, status=400)

@login_required
@csrf_protect
def sozluk_detay_duzenle(request, detay_id):
    detay = get_object_or_404(SozlukDetay, id=detay_id)
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı düzenleme yetkiniz yok.'}, status=403)
    
    if request.method == 'POST':
        form = SozlukDetayForm(request.POST, instance=detay)
        if form.is_valid():
            detay = form.save(commit=False)
            detay.detay = bleach.clean(detay.detay, tags=['p', 'br'], strip=True)
            try:
                detay.save()
                logger.info(f"Detay düzenlendi: Kelime {detay.kelime.kelime}, Kullanıcı: {request.user.username}")
                return JsonResponse({'success': True})
            except ValidationError as e:
                return JsonResponse({'success': False, 'errors': {field: errors[0] for field, errors in e.message_dict.items()}})
        return JsonResponse({'success': False, 'errors': {field: errors[0]['message'] for field, errors in form.errors.get_json_data().items()}})
    
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'}, status=400)

@login_required
@csrf_protect
def sozluk_detay_veri(request, detay_id):
    detay = get_object_or_404(SozlukDetay, id=detay_id)
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı düzenleme yetkiniz yok.'}, status=403)
    return JsonResponse({
        'success': True,
        'detay': detay.detay
    })