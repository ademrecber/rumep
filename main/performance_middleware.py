import time
import logging
from django.db import connection

logger = logging.getLogger(__name__)

class PerformanceMiddleware:
    """Performans izleme middleware'i"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        start_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        end_time = time.time()
        end_queries = len(connection.queries)
        
        duration = end_time - start_time
        query_count = end_queries - start_queries
        
        # Yavaş istekleri logla
        if duration > 1.0:  # 1 saniyeden uzun
            logger.warning(
                f"Yavaş istek: {request.path} - "
                f"Süre: {duration:.2f}s - "
                f"Query sayısı: {query_count}"
            )
        
        # N+1 query problemini tespit et
        if query_count > 20:
            logger.warning(
                f"Çok fazla query: {request.path} - "
                f"Query sayısı: {query_count}"
            )
        
        # Response header'a performans bilgisi ekle
        response['X-Response-Time'] = f"{duration:.3f}s"
        response['X-Query-Count'] = str(query_count)
        
        return response