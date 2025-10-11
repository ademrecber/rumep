from django.http import HttpResponse, Http404
from django.conf import settings
import os
import mimetypes

def download_font(request, font_name):
    """Font dosyalarını indirilebilir hale getirir"""
    
    # Güvenlik için sadece belirli font dosyalarına izin ver
    allowed_fonts = {
        'rumep-logos-colr': 'RumepLogosCOLR.ttf',
        'rumep-logos-svg': 'RumepLogosSVG.ttf', 
        'rumep-logos-woff2': 'RumepLogosSVG.woff2'
    }
    
    if font_name not in allowed_fonts:
        raise Http404("Font bulunamadı")
    
    file_name = allowed_fonts[font_name]
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'fonts', file_name)
    
    if not os.path.exists(file_path):
        raise Http404("Font dosyası bulunamadı")
    
    # MIME type'ı belirle
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        if file_name.endswith('.ttf'):
            content_type = 'font/ttf'
        elif file_name.endswith('.woff2'):
            content_type = 'font/woff2'
        else:
            content_type = 'application/octet-stream'
    
    # Dosyayı oku ve response olarak döndür
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response['Content-Length'] = os.path.getsize(file_path)
        return response

def font_list(request):
    """Mevcut fontları listeler"""
    fonts = [
        {
            'name': 'Rumep Logos COLR',
            'file': 'rumep-logos-colr',
            'format': 'TTF',
            'description': 'Rumep logoları için renkli font'
        },
        {
            'name': 'Rumep Logos SVG',
            'file': 'rumep-logos-svg', 
            'format': 'TTF',
            'description': 'Rumep logoları için SVG font'
        },
        {
            'name': 'Rumep Logos WOFF2',
            'file': 'rumep-logos-woff2',
            'format': 'WOFF2', 
            'description': 'Web için optimize edilmiş font'
        }
    ]
    
    from django.shortcuts import render
    return render(request, 'main/font_list.html', {'fonts': fonts})