from social_core.exceptions import AuthCanceled
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import translation
from django.conf import settings

class SocialAuthExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, AuthCanceled):
            messages.info(request, 'Têketin hat betalkirin, ji kerema xwe dîsa biceribîne.')
            return redirect('login_page')
        return None

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_language = request.user.profile.preferred_language
            translation.activate(user_language)
            request.LANGUAGE_CODE = user_language
        else:
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
        response = self.get_response(request)
        translation.deactivate()
        return response

class CSRFFailureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        from django.middleware.csrf import CsrfViewMiddleware
        if isinstance(exception, Exception) and 'CSRF' in str(exception):
            messages.error(request, 'Güvenlik hatası. Lütfen sayfayı yenileyin.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return None
