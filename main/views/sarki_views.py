from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Count
from django.core.exceptions import ValidationError
from ..models import Kisi, Album, Sarki, SarkiDetay
from ..forms import AlbumForm, SarkiForm, SarkiDetayForm, SarkiDuzenleForm
from .base import profile_required
import logging

logger = logging.getLogger(__name__)

def sarki_sozleri(request):
    harf = request.GET.get('harf', '').lower()
    harfler = ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']
    
    kisi_gruplari = []
    if harf:
        kisiler = Kisi.objects.filter(
            Q(ad__istartswith=harf) & Q(albumler__sarkilar__isnull=False)
        ).distinct().order_by('ad').annotate(
            album_sayisi=Count('albumler', distinct=True),
            sarki_sayisi=Count('albumler__sarkilar', distinct=True)
        )
        if kisiler.exists():
            kisi_gruplari.append((harf, kisiler))
    else:
        for h in harfler:
            kisiler = Kisi.objects.filter(
                Q(ad__istartswith=h) & Q(albumler__sarkilar__isnull=False)
            ).distinct().order_by('ad').annotate(
                album_sayisi=Count('albumler', distinct=True),
                sarki_sayisi=Count('albumler__sarkilar', distinct=True)
            )
            if kisiler.exists():
                kisi_gruplari.append((h, kisiler))
    
    # Türleri al (boş olmayanlar, Sarki modelinden)
    turler = Sarki.objects.exclude(tur='').values_list('tur', flat=True).distinct().order_by('tur')
    
    return render(request, 'main/sarki/sarki_sozleri.html', {
        'harfler': harfler,
        'kisi_gruplari': kisi_gruplari,
        'secili_harf': harf,
        'turler': turler
    })

@login_required
@require_GET
@csrf_protect
def sarki_kisi_ara(request):
    query = request.GET.get('q', '').strip().lower()
    kisiler = Kisi.objects.filter(ad__istartswith=query).order_by('ad')[:20]
    data = [{
        'id': kisi.id,
        'ad': kisi.ad,
        'biyografi': kisi.biyografi[:100] + ('...' if len(kisi.biyografi) > 100 else '')
    } for kisi in kisiler]
    return JsonResponse({'kisiler': data})

@login_required
@require_GET
@csrf_protect
def sarki_ara(request):
    query = request.GET.get('q', '').strip()
    tur = request.GET.get('tur', '').strip()
    sarkilar = Sarki.objects.all()
    
    if query:
        sarkilar = sarkilar.filter(
            Q(ad__icontains=query) | Q(sozler__icontains=query)
        )
    if tur:
        sarkilar = sarkilar.filter(tur__iexact=tur)
    
    sarkilar = sarkilar.order_by('ad')[:20]
    data = [{
        'id': sarki.id,
        'ad': sarki.ad,
        'album': sarki.album.ad,
        'kisi': sarki.album.kisi.ad,
        'sozler': sarki.sozler[:100] + ('...' if len(sarki.sozler) > 100 else '')
    } for sarki in sarkilar]
    return JsonResponse({'sarkilar': data})

@login_required
@profile_required
def sarki_ekle(request):
    kisi_id = request.GET.get('kisi_id')
    kisi = None
    albumler = []
    if kisi_id:
        kisi = get_object_or_404(Kisi, id=kisi_id)
        albumler = Album.objects.filter(kisi=kisi).order_by('ad')
    
    album_form = AlbumForm()
    sarki_form = SarkiForm()
    
    if request.method == 'POST':
        if 'album_submit' in request.POST:
            album_form = AlbumForm(request.POST)
            if album_form.is_valid() and kisi:
                album = album_form.save(commit=False)
                album.kisi = kisi
                album.kullanici = request.user
                try:
                    album.save()
                    logger.info(f"Albüm eklendi: {album.ad}, Kullanıcı: {request.user.username}")
                    return JsonResponse({'success': True})
                except ValidationError as e:
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)
            return JsonResponse({'success': False, 'errors': album_form.errors.as_json()})
        elif 'sarki_submit' in request.POST:
            logger.debug(f"Form gönderilen veri: {request.POST}")
            sarki_form = SarkiForm(request.POST)
            album_id = request.POST.get('album')
            logger.debug(f"Album ID: {album_id}")
            if album_id:
                if sarki_form.is_valid():
                    album = get_object_or_404(Album, id=album_id)
                    sarki = sarki_form.save(commit=False)
                    sarki.album = album
                    sarki.kullanici = request.user
                    sarki.save()
                    logger.info(f"Şarkı eklendi: {sarki.ad}, Kullanıcı: {request.user.username}")
                    return JsonResponse({'success': True})
                else:
                    logger.error(f"Şarkı ekleme hatası: Form geçersiz. Hatalar: {sarki_form.errors}")
                    logger.error(f"Form gönderilen veri tekrar: {request.POST}")
                    return JsonResponse({'success': False, 'errors': sarki_form.errors.as_json()})
            else:
                logger.error("Albüm ID eksik.")
                return JsonResponse({'success': False, 'errors': '{"album": [{"message": "Albüm seçimi zorunludur.", "code": "required"}]}'})
    
    return render(request, 'main/sarki/sarki_ekle.html', {
        'kisi': kisi,
        'albumler': albumler,
        'album_form': album_form,
        'sarki_form': sarki_form
    })

@login_required
@profile_required
def sarki_album_ekle(request, kisi_id):
    kisi = get_object_or_404(Kisi, id=kisi_id)
    album_form = AlbumForm()
    
    if request.method == 'POST':
        album_form = AlbumForm(request.POST)
        if album_form.is_valid():
            album = album_form.save(commit=False)
            album.kisi = kisi
            album.kullanici = request.user
            try:
                album.save()
                logger.info(f"Albüm eklendi: {album.ad}, Kullanıcı: {request.user.username}")
                return redirect('sarki_ekle', kisi_id=kisi.id)
            except ValidationError as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return render(request, 'main/sarki/album_ekle.html', {
        'kisi': kisi,
        'album_form': album_form
    })

@login_required
@csrf_protect
def sarki_album_liste(request, kisi_id):
    kisi = get_object_or_404(Kisi, id=kisi_id)
    albumler = Album.objects.filter(kisi=kisi).order_by('ad')
    return render(request, 'main/sarki/album_liste.html', {
        'kisi': kisi,
        'albumler': albumler
    })

@login_required
@csrf_protect
def sarki_liste(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    sarkilar = Sarki.objects.filter(album=album).order_by('ad')
    return render(request, 'main/sarki/sarki_liste.html', {
        'album': album,
        'sarkilar': sarkilar
    })

@login_required
@csrf_protect
def sarki_detay(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    detaylar = sarki.detaylar.all()
    return render(request, 'main/sarki/sarki_detay.html', {
        'sarki': sarki,
        'detaylar': detaylar
    })

@login_required
@profile_required
@require_POST
def sarki_sil(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    if sarki.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıyı silme yetkiniz yok.'}, status=403)
    sarki.delete()
    logger.info(f"Şarkı silindi: {sarki.ad}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})

@login_required
@profile_required
@require_POST
def sarki_album_sil(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    logger.debug(f"Albüm silme isteği: Albüm ID {album_id}, Kullanıcı: {request.user.username}")
    if album.kullanici != request.user:
        logger.warning(f"Yetkisiz silme girişimi: Albüm ID {album_id}, Kullanıcı: {request.user.username}")
        return JsonResponse({'success': False, 'error': 'Bu albümü silme yetkiniz yok.'}, status=403)
    if album.diger_kullanicilarin_sarkilari_var_mi():
        logger.info(f"Albüm silme engellendi: Albüm ID {album_id}, başka kullanıcıların şarkıları var.")
        return JsonResponse({'success': False, 'error': 'Bu albümde başka kullanıcıların eklediği şarkılar var, silinemez.'}, status=400)
    album.delete()
    logger.info(f"Albüm silindi: {album.ad}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})

@login_required
@profile_required
@require_POST
def sarki_detay_ekle(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    form = SarkiDetayForm(request.POST)
    if form.is_valid():
        detay = form.save(commit=False)
        detay.sarki = sarki
        detay.kullanici = request.user
        detay.save()
        logger.info(f"Şarkı detayı eklendi: {sarki.ad}, Kullanıcı: {request.user.username}")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors.as_json()})

@login_required
@csrf_protect
@require_GET
def sarki_detay_veri(request, detay_id):
    detay = get_object_or_404(SarkiDetay, id=detay_id)
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı düzenleme yetkiniz yok.'}, status=403)
    data = {
        'detay': detay.detay
    }
    return JsonResponse({'success': True, 'data': data})

@login_required
@profile_required
@require_POST
def sarki_detay_duzenle(request, detay_id):
    detay = get_object_or_404(SarkiDetay, id=detay_id)
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı düzenleme yetkiniz yok.'}, status=403)
    form = SarkiDetayForm(request.POST, instance=detay)
    if form.is_valid():
        form.save()
        logger.info(f"Şarkı detayı düzenlendi: {detay.sarki.ad}, Kullanıcı: {request.user.username}")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors.as_json()})

@login_required
@profile_required
@require_POST
def sarki_detay_sil(request, detay_id):
    detay = get_object_or_404(SarkiDetay, id=detay_id)
    if detay.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu detayı silme yetkiniz yok.'}, status=403)
    detay.delete()
    logger.info(f"Şarkı detayı silindi: {detay.sarki.ad}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})

@login_required
@csrf_protect
@require_GET
def sarki_album_degistir_veri(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    if sarki.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıyı düzenleme yetkiniz yok.'}, status=403)
    albumler = Album.objects.filter(kisi=sarki.album.kisi).order_by('ad')
    data = {
        'album_id': sarki.album.id,
        'albumler': [{'id': album.id, 'ad': album.ad} for album in albumler]
    }
    return JsonResponse({'success': True, 'data': data})

@login_required
@profile_required
@require_POST
def sarki_album_degistir(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    if sarki.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıyı düzenleme yetkiniz yok.'}, status=403)
    album_id = request.POST.get('album')
    album = get_object_or_404(Album, id=album_id)
    if album.kisi != sarki.album.kisi:
        return JsonResponse({'success': False, 'error': 'Bu albüm aynı kişiye ait değil.'}, status=400)
    sarki.album = album
    sarki.save()
    logger.info(f"Şarkı albümü değiştirildi: {sarki.ad}, Yeni Albüm: {album.ad}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})


@login_required
@profile_required
def sarki_duzenle(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    if sarki.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıyı düzenleme yetkiniz yok.'}, status=403)
    
    if request.method == 'POST':
        form = SarkiDuzenleForm(request.POST, instance=sarki)  # SarkiDuzenleForm kullanıyoruz
        if form.is_valid():
            form.save()
            logger.info(f"Şarkı düzenlendi: {sarki.ad}, Kullanıcı: {request.user.username}")
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    
    # GET isteği için JSON verisi döndürelim
    data = {
        'ad': sarki.ad,
        'sozler': sarki.sozler,
        'link': sarki.link or '',
        'tur': sarki.tur or ''
    }
    return JsonResponse({'success': True, 'data': data})

@login_required
@profile_required
@require_POST
def sarki_duzenle_kaydet(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    if sarki.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıyı düzenleme yetkiniz yok.'}, status=403)
    form = SarkiForm(request.POST, instance=sarki)
    
    if form.is_valid():
        form.save()
        logger.info(f"Şarkı düzenlendi: {sarki.ad}, Kullanıcı: {request.user.username}")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors.as_json()})