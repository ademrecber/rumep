from social_core.exceptions import AuthCanceled
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import translation
from django.conf import settings

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://platform.twitter.com https://www.instagram.com https://code.jquery.com https://www.google-analytics.com https://maps.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-src 'self' https://platform.twitter.com https://www.instagram.com; "
            "object-src 'none';"
        )
        
        response['Content-Security-Policy'] = csp
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response

class SocialAuthExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, AuthCanceled):
            messages.info(request, 'Giriş iptal edildi, lütfen tekrar deneyin.')
            return redirect('login_page')
        return None

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Middleware çalışıyor, kullanıcı: {request.user}")  # Hata ayıklama
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_language = request.user.profile.preferred_language
            print(f"Kullanıcı dili: {user_language}")  # Hata ayıklama
            translation.activate(user_language)
            request.LANGUAGE_CODE = user_language
        else:
            print(f"Varsayılan dil: {settings.LANGUAGE_CODE}")  # Hata ayıklama
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
        response = self.get_response(request)
        translation.deactivate()
        return response