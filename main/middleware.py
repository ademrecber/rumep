from django.shortcuts import redirect
from django.contrib import messages

class CSRFFailureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Exception) and 'CSRF' in str(exception):
            messages.error(request, 'Güvenlik hatası. Lütfen sayfayı yenileyin.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return None

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            'script', 'alert', 'javascript:', 'vbscript:', 'onload', 'onerror',
            'ORDER BY', 'UNION SELECT', 'DROP TABLE', '--', ';--', '/*', '*/',
            '<script', '</script>', 'eval(', 'document.cookie'
        ]

    def __call__(self, request):
        # Suspicious request detection
        query_string = request.META.get('QUERY_STRING', '')
        path = request.path
        
        for pattern in self.suspicious_patterns:
            if pattern.lower() in query_string.lower() or pattern.lower() in path.lower():
                from django.http import HttpResponseBadRequest
                return HttpResponseBadRequest('Suspicious request detected')
        
        response = self.get_response(request)
        return response
