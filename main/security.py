from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone
from functools import wraps
import hashlib

def rate_limit(max_requests=10, window_seconds=60, key_func=None):
    """Rate limiting decorator"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Rate limit key oluştur
            if key_func:
                key = key_func(request)
            else:
                # Kullanıcı bazlı rate limiting
                if hasattr(request, 'user') and request.user.is_authenticated:
                    key = f"rate_limit:user:{request.user.id}:{view_func.__name__}"
                else:
                    key = f"rate_limit:ip:{request.META.get('REMOTE_ADDR', 'unknown')}:{view_func.__name__}"
            
            # Mevcut istek sayısını kontrol et
            current_requests = cache.get(key, 0)
            
            if current_requests >= max_requests:
                from django.contrib import messages
                from django.shortcuts import redirect
                if hasattr(request, 'META') and request.META.get('HTTP_REFERER'):
                    return redirect(request.META.get('HTTP_REFERER'))
                return redirect('/')
            
            # İstek sayısını artır
            cache.set(key, current_requests + 1, window_seconds)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def get_client_ip(request):
    """Gerçek IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def sanitize_input(text):
    """Input sanitization"""
    import bleach
    
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'a']
    allowed_attributes = {'a': ['href', 'title']}
    
    # HTML temizle
    clean_text = bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)
    
    # XSS koruması
    clean_text = bleach.linkify(clean_text)
    
    return clean_text

class SecurityMiddleware:
    """Güvenlik middleware'i"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Suspicious request patterns
        suspicious_patterns = [
            'script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            'eval(', 'alert(', 'document.cookie', 'window.location'
        ]
        
        # Query string ve POST data kontrol et
        query_string = request.META.get('QUERY_STRING', '').lower()
        for pattern in suspicious_patterns:
            if pattern in query_string:
                from django.http import HttpResponseBadRequest
                return HttpResponseBadRequest("Güvenlik ihlali tespit edildi")
        
        response = self.get_response(request)
        
        # Security headers ekle
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response