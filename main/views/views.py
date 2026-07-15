from django.http import HttpResponse, Http404
from django.conf import settings
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
import os
import mimetypes
from fontTools.ttLib import TTFont
from main.models import RuxPdfComment
from main.forms import RuxPdfCommentForm

def landing_page(request):
    """Yeni modern ana sayfa"""
    return render(request, 'main/landing_page.html')

def rumep_spor(request):
    """Rumep Spor uygulaması ana sayfası"""
    return render(request, 'rumep-spor/index.html')

def rumep_spor_privacy(request):
    """Rumep Spor uygulaması gizlilik politikası"""
    return render(request, 'rumep-spor/privacy-policy.html')

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

def get_font_characters():
    """Font dosyasındaki Private Use Area (PUA) karakterlerini otomatik bulur"""
    try:
        # Font dosyasının yolu (TTF tercih edilir çünkü okunması daha kolaydır)
        font_path = os.path.join(settings.STATICFILES_DIRS[0], 'fonts', 'RumepLogosSVG.ttf')
        
        if not os.path.exists(font_path):
            # Alternatif olarak diğer fontu dene
            font_path = os.path.join(settings.STATICFILES_DIRS[0], 'fonts', 'RumepLogosCOLR.ttf')
            
        if not os.path.exists(font_path):
            return []

        font = TTFont(font_path)
        cmap = font.getBestCmap()
        
        characters = []
        if cmap:
            # Karakter kodlarını sırala
            sorted_codes = sorted(cmap.keys())
            
            for code in sorted_codes:
                # Sadece Private Use Area (PUA) aralığını al (E000 - F8FF)
                # Genellikle özel ikonlar bu aralıkta olur
                if 0xE000 <= code <= 0xF8FF:
                    hex_code = f"U+{code:04X}"
                    # Python'da unicode karakteri oluştur
                    char = chr(code)
                    characters.append({
                        'char': char,
                        'code': hex_code
                    })
                    
        return characters
    except Exception as e:
        print(f"Font okuma hatası: {e}")
        return []

def font_list(request):
    """Mevcut fontları ve karakterleri listeler"""
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

    # Karakterleri otomatik olarak font dosyasından oku
    font_characters = get_font_characters()
    
    return render(request, 'main/font_list.html', {
        'fonts': fonts,
        'font_characters': font_characters
    })

def usage_guide(request):
    """Kullanım Kılavuzu sayfası"""
    return render(request, 'main/usage_guide.html')

def privacy_policy(request):
    """Gizlilik Politikası sayfası"""
    return render(request, 'main/privacy.html')

def terms_of_service(request):
    """Kullanım Şartları sayfası"""
    return render(request, 'main/terms.html')

def contact(request):
    """İletişim sayfası"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            try:
                # E-posta Konusu
                email_subject = f"Rumep İletişim Formu: {name}"
                
                # E-posta İçeriği
                email_body = f"Web sitenizden yeni bir mesaj var:\n\nGönderen: {name}\nE-posta: {email}\n\nMesaj:\n{message}"
                
                # E-postayı site sahibine (kendisine) gönder
                send_mail(
                    email_subject,
                    email_body,
                    settings.EMAIL_HOST_USER,  # From
                    [settings.EMAIL_HOST_USER],  # To (Kendine gönder)
                    fail_silently=False,
                )
                
                messages.success(request, 'Mesajınız başarıyla gönderildi! En kısa sürede size dönüş yapacağız.')
                return redirect('contact')
                
            except Exception as e:
                messages.error(request, 'Mesaj gönderilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.')
                print(f"Mail Hatası: {e}")
        else:
            messages.error(request, 'Lütfen tüm alanları doldurun.')

    return render(request, 'main/contact.html')

def about(request):
    """Hakkımızda sayfası"""
    return render(request, 'main/about.html')

def cookie_policy(request):
    """Çerez Politikası sayfası"""
    return render(request, 'main/cookie_policy.html')

def statistics(request):
    """İstatistikler sayfası"""
    # İstatistik verileri (örnek veriler)
    stats = {
        'total_visitors': '10.5K+',
        'active_users': '1.2K',
        'downloads': '5.8K+',
        'projects': '3'
    }
    return render(request, 'main/statistics.html', {'stats': stats})

# ── RUX VPN ──
def rux_vpn(request):
    return render(request, 'rux-vpn/index.html')

def rux_vpn_faq(request):
    return render(request, 'rux-vpn/faq.html')

def rux_vpn_privacy(request):
    return render(request, 'rux-vpn/privacy_policy.html')

def rux_vpn_terms(request):
    return render(request, 'rux-vpn/terms_of_use.html')

# ── RUX PDF ──
def rux_pdf(request):
    comments = RuxPdfComment.objects.filter(is_approved=True)
    if request.method == 'POST':
        form = RuxPdfCommentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Yorumunuz başarıyla eklendi!')
            return redirect('rux_pdf')
    else:
        form = RuxPdfCommentForm()
        
    return render(request, 'rux-pdf/index.html', {'comments': comments, 'form': form})

def rux_pdf_privacy(request):
    return render(request, 'rux-pdf/privacy_policy.html')

def rux_pdf_terms(request):
    return render(request, 'rux-pdf/terms_of_use.html')
