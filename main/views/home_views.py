
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from ..models import Post, Katki, Profile, Sarki, Kisi, Sozluk, Atasozu, Deyim
from ..forms import PostForm
from .base import profile_required
import bleach
from django.db import models
import logging
from ..utils.embed_utils import generate_embed_code
from ..utils.shortener import create_short_link
from ..ai.utils import enhance_text

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@login_required
@profile_required
@csrf_protect
def home(request):
    request.session['return_page'] = 'home'
    sekme = request.GET.get('sekme', 'ana_sayfa')
    form = PostForm()
    
    if request.method == 'POST' and sekme == 'ana_sayfa':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.text = bleach.clean(post.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)
            post.embed_code = generate_embed_code(post.link)
            logger.debug(f"Post için embed kodu: {post.embed_code}")
            long_url = post.link
            post.link = None
            post.save()
            create_short_link(post, long_url)
            return redirect('home')
    
    posts = Post.objects.all().annotate(
        critique_count=models.Count('critiques')
    ).order_by('-created_at')[:10] if sekme == 'ana_sayfa' else []
    
    katkilar = []
    if sekme == 'katkilar':
        katkilar_qs = Katki.objects.select_related('user__profile').order_by('-eklenme_tarihi')[:10]
        for katki in katkilar_qs:
            katki_data = {
                'id': katki.id,
                'user': katki.user,
                'tur': katki.tur,
                'eklenme_tarihi': katki.eklenme_tarihi,
                'icerik_id': katki.icerik_id,
            }
            try:
                if katki.tur == 'sarki':
                    sarki = Sarki.objects.filter(id=katki.icerik_id).only('ad').first()
                    if sarki:
                        katki_data['sarki'] = sarki
                        katki_data['baslik'] = bleach.clean(sarki.ad, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('sarki_detay', args=[katki.icerik_id])
                    else:
                        katki_data['baslik'] = 'Bilinmeyen'
                        katki_data['detay_url'] = reverse('sarki_detay', args=[katki.icerik_id])
                elif katki.tur == 'kisi':
                    kisi = Kisi.objects.filter(id=katki.icerik_id).only('ad').first()
                    if kisi:
                        katki_data['kisi'] = kisi
                        katki_data['baslik'] = bleach.clean(kisi.ad, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('kisi_detay', args=[katki.icerik_id])
                    else:
                        katki_data['baslik'] = 'Bilinmeyen'
                        katki_data['detay_url'] = reverse('kisi_detay', args=[katki.icerik_id])
                elif katki.tur == 'sozluk':
                    sozluk = Sozluk.objects.filter(id=katki.icerik_id).only('kelime').first()
                    if sozluk:
                        katki_data['sozluk'] = sozluk
                        katki_data['baslik'] = bleach.clean(sozluk.kelime, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('sozluk_kelime', args=[katki.icerik_id])
                    else:
                        katki_data['baslik'] = 'Bilinmeyen'
                        katki_data['detay_url'] = reverse('sozluk_kelime', args=[katki.icerik_id])
                elif katki.tur == 'atasozu':
                    atasozu = Atasozu.objects.filter(id=katki.icerik_id).only('kelime').first()
                    if atasozu:
                        katki_data['atasozu'] = atasozu
                        katki_data['baslik'] = bleach.clean(atasozu.kelime, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('atasozu_deyim_detay', args=['atasozu', katki.icerik_id])
                    else:
                        katki_data['baslik'] = 'Bilinmeyen'
                        katki_data['detay_url'] = reverse('atasozu_deyim_detay', args=['atasozu', katki.icerik_id])
                elif katki.tur == 'deyim':
                    deyim = Deyim.objects.filter(id=katki.icerik_id).only('kelime').first()
                    if deyim:
                        katki_data['deyim'] = deyim
                        katki_data['baslik'] = bleach.clean(deyim.kelime, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('atasozu_deyim_detay', args=['deyim', katki.icerik_id])
                    else:
                        katki_data['baslik'] = 'Bilinmeyen'
                        katki_data['detay_url'] = reverse('atasozu_deyim_detay', args=['deyim', katki.icerik_id])
                katkilar.append(katki_data)
            except Exception as e:
                logger.error(f"Katkı işlenirken hata: {str(e)}")
                continue
    
    liderler = Profile.objects.filter(katki_puani__gt=0).order_by('-katki_puani')[:10] if sekme == 'katkilar' else []
    
    return render(request, 'main/tabs.html', {
        'posts': posts,
        'katkilar': katkilar,
        'liderler': liderler,
        'form': form,
        'user': request.user,
        'sekme': sekme
    })



@login_required
@csrf_protect
def enhance_post_text(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        text = request.POST.get('text', '')
        if not text.strip():
            logger.warning("Boş metin alındı.")
            return JsonResponse({'success': False, 'error': 'Metin boş olamaz'}, status=400)
        try:
            enhanced_text = enhance_text(text, task_type='general', language='tr')
            logger.info("Metin başarıyla geliştirildi.")
            return JsonResponse({'success': True, 'enhanced_text': enhanced_text}, status=200)
        except ValueError as e:
            logger.error(f"Değer hatası: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Metin geliştirme hatası: {str(e)}")
            return JsonResponse({'success': False, 'error': f"Metin geliştirme başarısız: {str(e)}"}, status=500)
    logger.warning("Geçersiz istek: Yöntem veya başlık hatalı.")
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'}, status=400)


