from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from ..models import Kisi, Kategori
from ..forms import KisiForm
import bleach
import logging
import re

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
def kisi_ekle(request):
    if request.method == 'POST':
        form = KisiForm(request.POST)
        if form.is_valid():
            kisi = form.save(commit=False)
            kisi.kullanici = request.user
            kisi.ad = bleach.clean(kisi.ad, tags=[], strip=True).lower()
            logger.debug(f"Ham biyografi içeriği: {kisi.biyografi}")  # Quill'den gelen ham HTML
            
            # Önce güvenli HTML temizliği yap, a tag'ı için href, target, rel ve style özniteliklerini koru
            kisi.biyografi = bleach.clean(
                kisi.biyografi,
                tags=['p', 'br', 'a', 'strong', 'em', 'ul', 'ol', 'li'],
                attributes={
                    'a': ['href', 'target', 'rel', 'style']
                },
                strip=True
            )
            logger.debug(f"Clean sonrası biyografi: {kisi.biyografi}")
            
            # Linkify'ı güvenli bir şekilde uygula - mevcut linkleri koru
            try:
                # Mevcut linkleri işaretle ve geçici olarak değiştir
                link_pattern = r'<a [^>]*href="([^"]*)"[^>]*>(.*?)</a>'
                link_placeholders = {}
                
                def replace_link(match):
                    placeholder = f"__LINK_PLACEHOLDER_{len(link_placeholders)}__"
                    link_placeholders[placeholder] = match.group(0)
                    return placeholder
                
                # Mevcut linkleri geçici yer tutucularla değiştir
                content_with_placeholders = re.sub(link_pattern, replace_link, kisi.biyografi)
                
                # Linkify'ı sadece metin içeriğine uygula
                linkified_content = bleach.linkify(
                    content_with_placeholders,
                    callbacks=[
                        lambda attrs, new: attrs.update({'target': '_blank', 'rel': 'noopener'}) or attrs
                    ],
                    parse_email=False
                )
                
                # Yer tutucuları orijinal linklerle değiştir
                for placeholder, original_link in link_placeholders.items():
                    linkified_content = linkified_content.replace(placeholder, original_link)
                
                kisi.biyografi = linkified_content
            except Exception as e:
                logger.error(f"Linkify hatası: {str(e)}")
                # Hata durumunda linkify adımını atla, temizlenmiş HTML'i kullan
            
            logger.debug(f"Linkify sonrası biyografi: {kisi.biyografi}")
            try:
                kisi.save()
                form.save_m2m()
                logger.info(f"Kişi eklendi: {kisi.ad}, Kullanıcı: {request.user.username}")
                return JsonResponse({'success': True})
            except ValidationError as e:
                logger.error(f"Doğrulama hatası: {e.message_dict}")
                return JsonResponse({'success': False, 'errors': {field: errors[0] for field, errors in e.message_dict.items()}})
        else:
            logger.error(f"Form hataları: {form.errors.get_json_data()}")
            return JsonResponse({'success': False, 'errors': {field: errors[0]['message'] for field, errors in form.errors.get_json_data().items()}})
    form = KisiForm()
    return render(request, 'main/kisi/kisi_ekle.html', {'form': form})

def kisi_liste(request):
    harf = request.GET.get('harf', None)
    kategori_slug = request.GET.get('kategori', None)
    query = request.GET.get('q', None)
    kisiler = Kisi.objects.all()
    if harf and harf.lower() in ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']:
        kisiler = kisiler.filter(ad__istartswith=harf)
    if kategori_slug:
        kisiler = kisiler.filter(kategoriler__slug=kategori_slug)
    if query:
        kisiler = kisiler.filter(ad__icontains=query)
    kisiler = kisiler.order_by('ad')[:20]
    kategoriler = Kategori.objects.all()
    harfler = ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']
    return render(request, 'main/kisi/kisi_liste.html', {
        'kisiler': kisiler,
        'kategoriler': kategoriler,
        'harfler': harfler,
        'user': request.user,
        'selected_harf': harf
    })

@csrf_protect
def kisi_liste_yukle(request):
    offset = int(request.GET.get('offset', 0))
    limit = 20
    harf = request.GET.get('harf', None)
    kategori_slug = request.GET.get('kategori', None)
    query = request.GET.get('q', None)
    kisiler = Kisi.objects.all()
    if harf and harf.lower() in ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']:
        kisiler = kisiler.filter(ad__istartswith=harf)
    if kategori_slug:
        kisiler = kisiler.filter(kategoriler__slug=kategori_slug)
    if query:
        kisiler = kisiler.filter(ad__icontains=query)
    kisiler = kisiler.order_by('ad')[offset:offset + limit]
    data = [{
        'id': kisi.id,
        'ad': kisi.ad,
        'biyografi': kisi.biyografi[:100] + ('...' if len(kisi.biyografi) > 100 else ''),
        'kategoriler': [kat.ad for kat in kisi.kategoriler.all()],
        'is_owner': kisi.kullanici == request.user
    } for kisi in kisiler]
    has_more = Kisi.objects.count() > offset + limit
    return JsonResponse({'kisiler': data, 'has_more': has_more})

def kisi_detay(request, kisi_id):
    kisi = get_object_or_404(Kisi, id=kisi_id)
    return render(request, 'main/kisi/kisi_detay.html', {'kisi': kisi, 'user': request.user})

@login_required
@csrf_protect
def kisi_sil(request, kisi_id):
    kisi = get_object_or_404(Kisi, id=kisi_id)
    if kisi.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu kişiyi silme yetkiniz yok.'}, status=403)
    kisi.delete()
    logger.info(f"Kişi silindi: {kisi.ad}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})