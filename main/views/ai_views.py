
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import logging
from ..ai.utils import process_request

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
def process_text(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        text = request.POST.get('text', '')
        language = request.POST.get('language', 'tr')  # Varsayılan Türkçe
        if not text.strip():
            logger.warning("Boş metin alındı.")
            return JsonResponse({'success': False, 'error': 'Metin boş olamaz'}, status=400)
        try:
            enhanced_text = process_request(text, language=language)
            logger.info("Metin başarıyla işlendi.")
            return JsonResponse({'success': True, 'enhanced_text': enhanced_text}, status=200)
        except ValueError as e:
            logger.error(f"Değer hatası: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Metin işleme hatası: {str(e)}")
            return JsonResponse({'success': False, 'error': f"Metin işleme başarısız: {str(e)}"}, status=500)
    logger.warning("Geçersiz istek: Yöntem veya başlık hatalı.")
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'}, status=400)
