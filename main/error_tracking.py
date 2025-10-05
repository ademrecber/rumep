import logging
import traceback
from django.core.mail import mail_admins
from django.conf import settings
from datetime import datetime, timedelta
from django.core.cache import cache

class ErrorTracker:
    """Hata takip sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger('rumep')
    
    def track_error(self, error, request=None, user=None):
        """Hatayı takip et ve kaydet"""
        error_data = {
            'error': str(error),
            'type': type(error).__name__,
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat(),
        }
        
        if request:
            error_data.update({
                'path': request.path,
                'method': request.method,
                'ip': request.META.get('REMOTE_ADDR', 'Unknown'),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            })
        
        if user and user.is_authenticated:
            error_data['user'] = user.username
        
        # Log'a kaydet
        self.logger.error(f"Error tracked: {error_data}")
        
        # Kritik hatalar için email gönder
        if self._is_critical_error(error):
            self._send_critical_error_email(error_data)
        
        # Error rate tracking
        self._track_error_rate()
        
        return error_data
    
    def _is_critical_error(self, error):
        """Kritik hata mı kontrol et"""
        critical_errors = [
            'DatabaseError',
            'IntegrityError',
            'PermissionDenied',
            'SuspiciousOperation'
        ]
        return type(error).__name__ in critical_errors
    
    def _send_critical_error_email(self, error_data):
        """Kritik hatalar için email gönder"""
        try:
            subject = f"Kritik Hata - {error_data['type']}"
            message = f"""
            Hata: {error_data['error']}
            Tip: {error_data['type']}
            Zaman: {error_data['timestamp']}
            Path: {error_data.get('path', 'N/A')}
            Kullanıcı: {error_data.get('user', 'Anonymous')}
            
            Traceback:
            {error_data['traceback']}
            """
            mail_admins(subject, message, fail_silently=True)
        except Exception:
            pass  # Email gönderimi başarısız olursa sessizce geç
    
    def _track_error_rate(self):
        """Hata oranını takip et"""
        cache_key = 'error_count_last_hour'
        current_count = cache.get(cache_key, 0)
        cache.set(cache_key, current_count + 1, 3600)  # 1 saat
        
        # Çok fazla hata varsa uyar
        if current_count > 50:  # Saatte 50'den fazla hata
            self.logger.critical(f"High error rate detected: {current_count} errors in last hour")

# Global error tracker instance
error_tracker = ErrorTracker()

def track_error(error, request=None, user=None):
    """Hata takip fonksiyonu"""
    return error_tracker.track_error(error, request, user)