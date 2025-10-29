from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Count
from django.core.exceptions import ValidationError
from ..models import Kisi, Album, Sarki, SarkiGrubu, SarkiDetay
from ..forms import AlbumForm, SarkiForm, SarkiGrubuForm, SarkiDetayForm, SarkiDuzenleForm
from .base import profile_required
import logging

logger = logging.getLogger(__name__)

def sarki_sozleri(request):
    harf = request.GET.get('harf', '').lower()
    harfler = ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']
    
    kisi_gruplari = []
    if harf:
        kisiler = Kisi.objects.filter(
            Q(ad__istartswith=harf) & Q(albumler__sarki_gruplari__dil_versiyonlari__isnull=False)
        ).distinct().order_by('ad').annotate(
            album_sayisi=Count('albumler', distinct=True),
            sarki_sayisi=Count('albumler__sarki_gruplari__dil_versiyonlari', distinct=True)
        )
        if kisiler.exists():
            kisi_gruplari.append((harf, kisiler))
    else:
        for h in harfler:
            kisiler = Kisi.objects.filter(
                Q(ad__istartswith=h) & Q(albumler__sarki_gruplari__dil_versiyonlari__isnull=False)
            ).distinct().order_by('ad').annotate(
                album_sayisi=Count('albumler', distinct=True),
                sarki_sayisi=Count('albumler__sarki_gruplari__dil_versiyonlari', distinct=True)
            )
            if kisiler.exists():
                kisi_gruplari.append((h, kisiler))
    
    # Türleri al - şimdilik boş bırakıyoruz çünkü tür alanı kaldırıldı
    turler = []
    
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
    # Sadece kişi ve grup türündeki kayıtları getir (kurum hariç)
    kisiler = Kisi.objects.filter(
        ad__istartswith=query,
        kisi_turu__in=['kisi', 'grup']
    ).order_by('ad')[:20]
    data = [{
        'id': kisi.id,
        'ad': kisi.ad,
        'kisi_turu': kisi.get_kisi_turu_display(),
        'biyografi': kisi.biyografi[:100] + ('...' if len(kisi.biyografi) > 100 else '')
    } for kisi in kisiler]
    return JsonResponse({'kisiler': data})

@login_required
@require_GET
@csrf_protect
def sarki_ara(request):
    query = request.GET.get('q', '').strip()
    sarki_gruplari = SarkiGrubu.objects.all()
    
    if query:
        sarki_gruplari = sarki_gruplari.filter(
            Q(ad__icontains=query) | Q(dil_versiyonlari__sozler__icontains=query)
        ).distinct()
    
    sarki_gruplari = sarki_gruplari.order_by('ad')[:20]
    data = [{
        'id': sarki_grubu.id,
        'ad': sarki_grubu.ad,
        'album': sarki_grubu.album.ad,
        'kisi': sarki_grubu.album.kisi.ad,
        'dil_sayisi': sarki_grubu.dil_versiyonlari.count()
    } for sarki_grubu in sarki_gruplari]
    return JsonResponse({'sarki_gruplari': data})

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
    sarki_grup_form = SarkiGrubuForm()
    sarki_grubu = None
    dil_secenekleri = [('ku', 'Kürtçe'), ('tr', 'Türkçe'), ('en', 'İngilizce'), ('ar', 'Arapça'), ('fa', 'Farsça')]
    mevcut_diller = []
    
    # Eğer sarki_grubu_id varsa, mevcut şarkı grubunu al
    sarki_grubu_id = request.GET.get('sarki_grubu_id')
    if sarki_grubu_id:
        sarki_grubu = get_object_or_404(SarkiGrubu, id=sarki_grubu_id)
        mevcut_diller = list(sarki_grubu.dil_versiyonlari.values_list('dil', flat=True))
    
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
        elif 'sarki_grup_submit' in request.POST:
            album_id = request.POST.get('album')
            ad = request.POST.get('ad')
            if album_id and ad:
                album = get_object_or_404(Album, id=album_id)
                sarki_grubu = SarkiGrubu.objects.create(
                    album=album,
                    ad=ad,
                    kullanici=request.user
                )
                return redirect(f'/sarki/ekle/?kisi_id={kisi.id}&sarki_grubu_id={sarki_grubu.id}')
        elif 'sarki_submit' in request.POST:
            sarki_grubu_id = request.POST.get('sarki_grubu_id')
            dil = request.POST.get('dil')
            sozler = request.POST.get('sozler')
            link = request.POST.get('link')
            if sarki_grubu_id and dil and sozler:
                sarki_grubu = get_object_or_404(SarkiGrubu, id=sarki_grubu_id)
                Sarki.objects.create(
                    sarki_grubu=sarki_grubu,
                    dil=dil,
                    sozler=sozler,
                    link=link if link else None
                )
                return redirect(f'/sarki/ekle/?kisi_id={kisi.id}&sarki_grubu_id={sarki_grubu.id}')
    
    return render(request, 'main/sarki/sarki_ekle.html', {
        'kisi': kisi,
        'albumler': albumler,
        'album_form': album_form,
        'sarki_grup_form': sarki_grup_form,
        'sarki_grubu': sarki_grubu,
        'dil_secenekleri': dil_secenekleri,
        'mevcut_diller': mevcut_diller
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
    albumler = Album.objects.filter(kisi=kisi).prefetch_related(
        'sarki_gruplari__dil_versiyonlari'
    ).order_by('ad')
    return render(request, 'main/sarki/album_liste.html', {
        'kisi': kisi,
        'albumler': albumler
    })

@login_required
@csrf_protect
def sarki_liste(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    sarki_gruplari = SarkiGrubu.objects.filter(album=album).prefetch_related('dil_versiyonlari').order_by('ad')
    return render(request, 'main/sarki/sarki_liste.html', {
        'album': album,
        'sarki_gruplari': sarki_gruplari
    })

@login_required
@csrf_protect
def sarki_detay(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    detaylar = sarki.detaylar.all()
    dil_secenekleri = [('ku', 'Kürtçe'), ('tr', 'Türkçe'), ('en', 'İngilizce'), ('ar', 'Arapça'), ('fa', 'Farsça')]
    mevcut_diller = list(sarki.sarki_grubu.dil_versiyonlari.values_list('dil', flat=True))
    return render(request, 'main/sarki/sarki_detay.html', {
        'sarki': sarki,
        'detaylar': detaylar,
        'dil_secenekleri': dil_secenekleri,
        'mevcut_diller': mevcut_diller
    })

@login_required
@profile_required
@require_POST
def sarki_sil(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    if sarki.sarki_grubu.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıyı silme yetkiniz yok.'}, status=403)
    sarki.delete()
    logger.info(f"Şarkı silindi: {sarki.sarki_grubu.ad}, Kullanıcı: {request.user.username}")
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
    if sarki.sarki_grubu.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıyı düzenleme yetkiniz yok.'}, status=403)
    
    if request.method == 'POST':
        # Şarkı grubu adını güncelle
        ad = request.POST.get('ad')
        if ad:
            sarki.sarki_grubu.ad = ad
            sarki.sarki_grubu.save()
        
        # Şarkı dil, sözler ve link güncelle
        sarki.dil = request.POST.get('dil', sarki.dil)
        sarki.sozler = request.POST.get('sozler', sarki.sozler)
        sarki.link = request.POST.get('link') or None
        sarki.save()
        logger.info(f"Şarkı düzenlendi: {sarki.sarki_grubu.ad}, Kullanıcı: {request.user.username}")
        return JsonResponse({'success': True})
    
    # GET isteği için JSON verisi döndürelim
    data = {
        'ad': sarki.sarki_grubu.ad,
        'dil': sarki.dil,
        'sozler': sarki.sozler,
        'link': sarki.link
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

@login_required
@profile_required
@require_POST
def sarki_yeni_dil_ekle(request):
    sarki_grubu_id = request.POST.get('sarki_grubu_id')
    dil = request.POST.get('dil')
    sozler = request.POST.get('sozler')
    link = request.POST.get('link')
    
    if not all([sarki_grubu_id, dil, sozler]):
        return JsonResponse({'success': False, 'error': 'Tüm alanları doldurun.'}, status=400)
    
    sarki_grubu = get_object_or_404(SarkiGrubu, id=sarki_grubu_id)
    
    if sarki_grubu.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıya dil ekleme yetkiniz yok.'}, status=403)
    
    # Aynı dilde zaten var mı kontrol et
    if sarki_grubu.dil_versiyonlari.filter(dil=dil).exists():
        return JsonResponse({'success': False, 'error': 'Bu dilde zaten söz mevcut.'}, status=400)
    
    # Yeni dil versiyonu oluştur
    Sarki.objects.create(
        sarki_grubu=sarki_grubu,
        dil=dil,
        sozler=sozler,
        link=link if link else None
    )
    
    logger.info(f"Yeni dil versiyonu eklendi: {sarki_grubu.ad} - {dil}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})

@login_required
@csrf_protect
def sarki_detay_slug(request, slug):
    sarki = get_object_or_404(Sarki, slug=slug)
    detaylar = sarki.detaylar.all()
    dil_secenekleri = [('ku', 'Kürtçe'), ('tr', 'Türkçe'), ('en', 'İngilizce'), ('ar', 'Arapça'), ('fa', 'Farsça')]
    mevcut_diller = list(sarki.sarki_grubu.dil_versiyonlari.values_list('dil', flat=True))
    return render(request, 'main/sarki/sarki_detay.html', {
        'sarki': sarki,
        'detaylar': detaylar,
        'dil_secenekleri': dil_secenekleri,
        'mevcut_diller': mevcut_diller
    })