import logging
import os
from datetime import datetime

def setup_logging():
    """Logging yapılandırması"""
    
    # Log dizini oluştur
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Log formatı
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ana logger
    logger = logging.getLogger('rumep')
    logger.setLevel(logging.INFO)
    
    # File handler - Genel loglar
    file_handler = logging.FileHandler(f'{log_dir}/app.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error handler - Sadece hatalar
    error_handler = logging.FileHandler(f'{log_dir}/errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Security handler - Güvenlik olayları
    security_logger = logging.getLogger('security')
    security_handler = logging.FileHandler(f'{log_dir}/security.log')
    security_handler.setFormatter(formatter)
    security_logger.addHandler(security_handler)
    
    return logger

class ErrorTrackingMiddleware:
    """Hata takip middleware'i"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('rumep')

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Hatayı logla
            self.logger.error(
                f"Unhandled exception: {str(e)} - "
                f"Path: {request.path} - "
                f"User: {getattr(request.user, 'username', 'Anonymous')} - "
                f"IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
            )
            raise

def log_user_action(user, action, details=None):
    """Kullanıcı eylemlerini logla"""
    logger = logging.getLogger('rumep')
    message = f"User action - User: {user.username} - Action: {action}"
    if details:
        message += f" - Details: {details}"
    logger.info(message)

def log_security_event(event_type, details, request=None):
    """Güvenlik olaylarını logla"""
    security_logger = logging.getLogger('security')
    message = f"Security event - Type: {event_type} - Details: {details}"
    if request:
        message += f" - IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
        message += f" - User: {getattr(request.user, 'username', 'Anonymous')}"
    security_logger.warning(message)