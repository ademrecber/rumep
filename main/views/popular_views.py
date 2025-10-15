import bleach
from django.shortcuts import render
from django.utils.timezone import localdate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from ..models import Entry, Topic
from .base import profile_required
from datetime import timedelta
from ..templatetags.post_tags import render_emojis
import logging

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def popular(request, period='today'):
    from ..models import Category, Profile
    now = timezone.now()
    
    # URL'den tab ve period parametrelerini al
    active_tab = request.GET.get('tab', 'topics')
    active_period = request.GET.get('period', 'today')
    
    # Zaman aralığını belirle
    if active_period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif active_period == 'weekly':
        start_date = now - timedelta(days=7)
        end_date = now
    elif active_period == 'monthly':
        start_date = now - timedelta(days=30)
        end_date = now
    else:  # all-time
        start_date = None
        end_date = None
    
    # Topic'ler için zaman bazlı filtreleme
    if start_date and end_date:
        trending_topics = Topic.objects.select_related('user').filter(
            entries__created_at__gte=start_date,
            entries__created_at__lte=end_date
        ).annotate(
            period_entry_count=models.Count('entries', filter=models.Q(entries__created_at__gte=start_date, entries__created_at__lte=end_date))
        ).filter(period_entry_count__gt=0).order_by('-period_entry_count', '-updated_at')[:20]
    else:
        trending_topics = Topic.objects.select_related('user').annotate(
            total_entry_count=models.Count('entries')
        ).filter(total_entry_count__gt=0).order_by('-total_entry_count', '-updated_at')[:20]
    
    # Aktif yazarlar - son 7 gün içinde entry yazan kullanıcılar
    week_ago = now - timedelta(days=7)
    from django.contrib.auth.models import User
    active_users = User.objects.filter(
        entry__created_at__gte=week_ago
    ).distinct()
    
    active_writers = Profile.objects.select_related('user').filter(
        user__in=active_users
    ).annotate(
        topic_count=models.Count('user__topic', distinct=True),
        entry_count=models.Count('user__entry', distinct=True)
    ).order_by('-katki_puani', '-entry_count')[:15]
    
    popular_categories = Category.objects.annotate(
        topic_count=models.Count('topics')
    ).filter(topic_count__gt=0).order_by('-topic_count')[:10]

    return render(request, 'main/popular/popular.html', {
        'trending_topics': trending_topics,
        'active_writers': active_writers,
        'popular_categories': popular_categories,
        'period': period,
        'active_tab': active_tab,
        'active_period': active_period,
        'user': request.user
    })

def load_more_popular(request):
    offset = int(request.GET.get('offset', 0))
    limit = 10
    period = request.GET.get('period', 'today')
    
    now = timezone.now()
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'weekly':
        start_date = now - timedelta(days=7)
        end_date = now
    elif period == 'monthly':
        start_date = now - timedelta(days=30)
        end_date = now
    else:  # all-time
        start_date = None
        end_date = None
    
    # Topic'ler için zaman bazlı filtreleme
    if start_date and end_date:
        topics_query = Topic.objects.select_related('user').filter(
            entries__created_at__gte=start_date,
            entries__created_at__lte=end_date
        ).annotate(
            period_entry_count=models.Count('entries', filter=models.Q(entries__created_at__gte=start_date, entries__created_at__lte=end_date))
        ).filter(period_entry_count__gt=0).order_by('-period_entry_count', '-updated_at')
    else:
        topics_query = Topic.objects.select_related('user').annotate(
            total_entry_count=models.Count('entries')
        ).filter(total_entry_count__gt=0).order_by('-total_entry_count', '-updated_at')
    
    topics = topics_query[offset:offset + limit]
    
    posts_data = []
    for topic in topics:
        # İlk entry'yi al (varsa)
        first_entry = topic.entries.first()
        entry_text = ''
        if first_entry:
            # Template filter'ları uygula
            from ..templatetags.post_tags import render_emojis, with_entry_font
            processed_text = render_emojis(first_entry.content)
            processed_text = with_entry_font(processed_text, first_entry)
            entry_text = processed_text
        
        posts_data.append({
            'id': topic.id,
            'title': topic.title,
            'text': entry_text,
            'nickname': getattr(topic.user.profile, 'nickname', topic.user.username) if hasattr(topic.user, 'profile') else topic.user.username,
            'username': topic.user.username,
            'short_id': topic.slug,
            'created_at': topic.created_at.isoformat(),
            'comment_count': topic.entry_count(),
            'upvotes': topic.upvote_count() if hasattr(topic, 'upvote_count') else 0,
            'downvotes': topic.downvote_count() if hasattr(topic, 'downvote_count') else 0,
            'is_owner': topic.user == request.user if request.user.is_authenticated else False,
            'daily_entry_count': getattr(topic, 'period_entry_count', getattr(topic, 'total_entry_count', 0))
        })
    
    has_more = topics_query.count() > offset + limit
    return JsonResponse({'posts': posts_data, 'has_more': has_more}, status=200)

def agenda(request):
    """Son 24 saatte en çok entry yazılan başlıkları göster"""
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    
    # Son 24 saatte entry yazılan topic'leri bul ve entry sayısına göre sırala
    topics = Topic.objects.filter(
        entries__created_at__gte=yesterday
    ).annotate(
        daily_entry_count=models.Count('entries', filter=models.Q(entries__created_at__gte=yesterday))
    ).filter(
        daily_entry_count__gt=0
    ).order_by('-daily_entry_count', '-updated_at')[:10]
    
    return render(request, 'main/agenda.html', {
        'topics': topics,
        'user': request.user
    })

def load_more_agenda(request):
    offset = int(request.GET.get('offset', 0))
    limit = 10
    
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    
    topics_query = Topic.objects.filter(
        entries__created_at__gte=yesterday
    ).annotate(
        daily_entry_count=models.Count('entries', filter=models.Q(entries__created_at__gte=yesterday))
    ).filter(
        daily_entry_count__gt=0
    ).order_by('-daily_entry_count', '-updated_at')
    
    topics = topics_query[offset:offset + limit]
    
    posts_data = []
    for topic in topics:
        # İlk entry'yi al (varsa)
        first_entry = topic.entries.first()
        entry_text = ''
        if first_entry:
            # Template filter'ları uygula
            from ..templatetags.post_tags import render_emojis, with_entry_font
            processed_text = render_emojis(first_entry.content)
            processed_text = with_entry_font(processed_text, first_entry)
            entry_text = processed_text
        
        posts_data.append({
            'id': topic.id,
            'title': topic.title,
            'text': entry_text,
            'nickname': getattr(topic.user.profile, 'nickname', topic.user.username) if hasattr(topic.user, 'profile') else topic.user.username,
            'username': topic.user.username,
            'short_id': topic.slug,
            'created_at': topic.created_at.isoformat(),
            'comment_count': topic.entry_count(),
            'upvotes': topic.upvote_count() if hasattr(topic, 'upvote_count') else 0,
            'downvotes': topic.downvote_count() if hasattr(topic, 'downvote_count') else 0,
            'is_owner': topic.user == request.user if request.user.is_authenticated else False,
            'daily_entry_count': topic.daily_entry_count
        })
    
    has_more = topics_query.count() > offset + limit
    return JsonResponse({'posts': posts_data, 'has_more': has_more}, status=200)