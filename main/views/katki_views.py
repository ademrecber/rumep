from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET
from django.urls import reverse
from ..models import Katki, Profile, Sarki, Kisi, Sozluk, Atasozu, Deyim
from django.db.models import Q
import bleach
import logging
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db import connection

logger = logging.getLogger(__name__)

@require_GET
@csrf_protect
def load_more_katkilar(request):
    """
    Load more contributions with pagination and filtering.
    
    Parameters:
    - offset: Starting position for pagination
    - tur: Type filter for contributions
    
    Returns:
    - JSON response with contributions data and pagination info
    """
    try:
        # Get and validate parameters
        offset = max(0, int(request.GET.get('offset', 0)))
        limit = min(50, int(request.GET.get('limit', 10)))  # Limit to prevent abuse
        tur = request.GET.get('tur', '')
        
        # Validate tur parameter
        valid_types = ['sarki', 'kisi', 'sozluk', 'atasozu', 'deyim', '']
        if tur not in valid_types:
            return JsonResponse({'error': 'Geçersiz tür parametresi'}, status=400)
        
        # Build query
        query = Q()
        if tur:
            query = Q(tur=tur)
        
        # Generate cache key based on parameters
        cache_key = f'katkilar_{tur}_{offset}_{limit}_v2'  # Updated cache key to avoid stale data
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return JsonResponse(cached_data, status=200)
        
        # Fetch data with optimized query
        katkilar = Katki.objects.select_related('user__profile').filter(query).order_by('-eklenme_tarihi')[offset:offset + limit]
        
        data = []
        for katki in katkilar:
            # Basic data that's always available
            katki_data = {
                'id': katki.id,
                'nickname': bleach.clean(katki.user.profile.nickname, tags=[], strip=True),
                'username': bleach.clean(katki.user.profile.username, tags=[], strip=True),
                'katki_puani': katki.user.profile.katki_puani,
                'tur': katki.tur,
                'eklenme_tarihi': katki.eklenme_tarihi.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'baslik': 'Bilinmeyen',  # Default title
                'detay_url': '#'  # Default URL
            }
            
            # Get specific data based on contribution type
            try:
                if katki.tur == 'sarki':
                    sarki = Sarki.objects.filter(id=katki.icerik_id).only('ad').first()
                    if sarki:
                        katki_data['baslik'] = bleach.clean(sarki.ad, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('sarki_detay', args=[katki.icerik_id])
                elif katki.tur == 'kisi':
                    kisi = Kisi.objects.filter(id=katki.icerik_id).only('ad').first()
                    if kisi:
                        katki_data['baslik'] = bleach.clean(kisi.ad, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('kisi_detay', args=[katki.icerik_id])
                elif katki.tur == 'sozluk':
                    sozluk = Sozluk.objects.filter(id=katki.icerik_id).only('kelime').first()
                    if sozluk:
                        katki_data['baslik'] = bleach.clean(sozluk.kelime, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('sozluk_kelime', args=[katki.icerik_id])
                elif katki.tur == 'atasozu':
                    atasozu = Atasozu.objects.filter(id=katki.icerik_id).only('kelime').first()
                    if atasozu:
                        katki_data['baslik'] = bleach.clean(atasozu.kelime, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('atasozu_deyim_detay', args=['atasozu', katki.icerik_id])
                    else:
                        katki_data['baslik'] = 'Bilinmeyen Atasözü'
                        katki_data['detay_url'] = reverse('atasozu_deyim_detay', args=['atasozu', katki.icerik_id])
                elif katki.tur == 'deyim':
                    deyim = Deyim.objects.filter(id=katki.icerik_id).only('kelime').first()
                    if deyim:
                        katki_data['baslik'] = bleach.clean(deyim.kelime, tags=[], strip=True)
                        katki_data['detay_url'] = reverse('atasozu_deyim_detay', args=['deyim', katki.icerik_id])
                    else:
                        katki_data['baslik'] = 'Bilinmeyen Deyim'
                        katki_data['detay_url'] = reverse('atasozu_deyim_detay', args=['deyim', katki.icerik_id])
            except Exception as e:
                logger.error(f"Katkı detayları yüklenirken hata: {str(e)}")
            
            data.append(katki_data)
        
        # Use count() with the same filter for consistency
        total_count = Katki.objects.filter(query).count()
        has_more = total_count > offset + limit
        
        response_data = {'katkilar': data, 'has_more': has_more, 'total_count': total_count}
        
        # Cache the result for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return JsonResponse(response_data, status=200)
    
    except ValueError as e:
        logger.warning(f"Geçersiz parametre: {str(e)}")
        return JsonResponse({'error': 'Geçersiz parametre değeri'}, status=400)
    except Exception as e:
        logger.error(f"Katkılar yüklenirken beklenmeyen hata: {str(e)}")
        return JsonResponse({'error': 'Sunucu hatası'}, status=500)

@require_GET
@csrf_protect
def load_more_liderler(request):
    """
    Load more leaders with pagination.
    
    Parameters:
    - offset: Starting position for pagination
    
    Returns:
    - JSON response with leaders data and pagination info
    """
    try:
        # Get and validate parameters
        offset = max(0, int(request.GET.get('offset', 0)))
        limit = min(50, int(request.GET.get('limit', 10)))  # Limit to prevent abuse
        
        # Generate cache key
        cache_key = f'liderler_{offset}_{limit}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return JsonResponse(cached_data, status=200)
        
        # Fetch data with optimized query
        liderler = Profile.objects.filter(katki_puani__gt=0).order_by('-katki_puani')[offset:offset + limit]
        
        data = [{
            'nickname': bleach.clean(lider.nickname, tags=[], strip=True),
            'username': bleach.clean(lider.username, tags=[], strip=True),
            'katki_puani': lider.katki_puani,
            'profile_url': reverse('profile_detail', args=[lider.username])
        } for lider in liderler]
        
        total_count = Profile.objects.filter(katki_puani__gt=0).count()
        has_more = total_count > offset + limit
        
        response_data = {'liderler': data, 'has_more': has_more, 'total_count': total_count}
        
        # Cache the result for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return JsonResponse(response_data, status=200)
    
    except ValueError as e:
        logger.warning(f"Geçersiz parametre: {str(e)}")
        return JsonResponse({'error': 'Geçersiz parametre değeri'}, status=400)
    except Exception as e:
        logger.error(f"Liderler yüklenirken beklenmeyen hata: {str(e)}")
        return JsonResponse({'error': 'Sunucu hatası'}, status=500)