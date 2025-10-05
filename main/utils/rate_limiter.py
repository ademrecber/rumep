from django.core.cache import cache
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
import hashlib

class RateLimiter:
    def __init__(self, max_requests=5, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
    
    def is_allowed(self, user_id, action_type='default'):
        """Check if user is allowed to perform action"""
        cache_key = f"rate_limit_{action_type}_{user_id}"
        
        # Get current requests from cache
        requests = cache.get(cache_key, [])
        now = datetime.now()
        
        # Remove old requests outside time window
        requests = [req_time for req_time in requests 
                   if now - req_time < timedelta(seconds=self.time_window)]
        
        # Check if limit exceeded
        if len(requests) >= self.max_requests:
            return False, self.max_requests - len(requests)
        
        # Add current request
        requests.append(now)
        cache.set(cache_key, requests, self.time_window)
        
        return True, self.max_requests - len(requests)
    
    def get_remaining_time(self, user_id, action_type='default'):
        """Get remaining time until next request allowed"""
        cache_key = f"rate_limit_{action_type}_{user_id}"
        requests = cache.get(cache_key, [])
        
        if not requests:
            return 0
            
        oldest_request = min(requests)
        time_passed = (datetime.now() - oldest_request).seconds
        return max(0, self.time_window - time_passed)

def check_duplicate_content(user, content, content_type='entry'):
    """Check if user recently submitted same content"""
    content_hash = hashlib.md5(content.encode()).hexdigest()
    cache_key = f"content_hash_{content_type}_{user.id}_{content_hash}"
    
    if cache.get(cache_key):
        return True  # Duplicate found
    
    # Store hash for 5 minutes
    cache.set(cache_key, True, 300)
    return False

def rate_limit_decorator(max_requests=5, time_window=60, action_type='default'):
    """Decorator for rate limiting views"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            limiter = RateLimiter(max_requests, time_window)
            allowed, remaining = limiter.is_allowed(request.user.id, action_type)
            
            if not allowed:
                remaining_time = limiter.get_remaining_time(request.user.id, action_type)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': f'Çok fazla istek. {remaining_time} saniye sonra tekrar deneyin.',
                        'remaining_time': remaining_time
                    }, status=429)
                else:
                    messages.error(request, f'Çok fazla istek. {remaining_time} saniye sonra tekrar deneyin.')
                    return view_func(request, *args, **kwargs)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator