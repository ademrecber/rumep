from django.core.cache import cache
from django.conf import settings
import hashlib

def get_cache_key(prefix, *args):
    """Cache key oluştur"""
    key_parts = [str(arg) for arg in args]
    key_string = f"{prefix}:{'_'.join(key_parts)}"
    return hashlib.md5(key_string.encode()).hexdigest()[:16]

def cache_popular_topics(period='today'):
    """Popüler başlıkları cache'le"""
    cache_key = get_cache_key('popular_topics', period)
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        from .models import Topic
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        if period == 'today':
            date_filter = datetime.now() - timedelta(days=1)
        elif period == 'week':
            date_filter = datetime.now() - timedelta(days=7)
        else:
            date_filter = datetime.now() - timedelta(days=30)
        
        topics = Topic.objects.with_related().filter(
            created_at__gte=date_filter
        ).annotate(
            entry_count=Count('entries')
        ).order_by('-entry_count', '-updated_at')[:20]
        
        cached_data = list(topics)
        cache.set(cache_key, cached_data, 300)  # 5 dakika cache
    
    return cached_data

def cache_user_stats(user_id):
    """Kullanıcı istatistiklerini cache'le"""
    cache_key = get_cache_key('user_stats', user_id)
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        from .models import Topic, Entry
        
        topic_count = Topic.objects.filter(user_id=user_id).count()
        entry_count = Entry.objects.filter(user_id=user_id).count()
        
        cached_data = {
            'topic_count': topic_count,
            'entry_count': entry_count,
        }
        cache.set(cache_key, cached_data, 600)  # 10 dakika cache
    
    return cached_data

def invalidate_user_cache(user_id):
    """Kullanıcı cache'ini temizle"""
    cache_key = get_cache_key('user_stats', user_id)
    cache.delete(cache_key)

def cache_category_stats():
    """Kategori istatistiklerini cache'le"""
    cache_key = 'category_stats'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        from .models import Category
        from django.db.models import Count
        
        categories = Category.objects.annotate(
            topic_count=Count('topics')
        ).order_by('name')
        
        cached_data = list(categories)
        cache.set(cache_key, cached_data, 1800)  # 30 dakika cache
    
    return cached_data