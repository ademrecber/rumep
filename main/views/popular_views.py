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
    elif period == 'yesterday':
        yesterday = now - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'weekly':
        start_date = now - timedelta(days=7)
        end_date = now
    elif period == 'monthly':
        start_date = now - timedelta(days=30)
        end_date = now
    else:
        # Default to all entries if period is not recognized
        entries_query = Entry.objects.select_related('user', 'topic').annotate(
            like_count=models.Count('likes')
        ).order_by('-like_count', '-created_at')
        entries = entries_query[offset:offset + limit]
        data = [{
            'id': entry.id,
            'nickname': bleach.clean(entry.user.profile.nickname, tags=[], strip=True),
            'username': bleach.clean(entry.user.profile.username, tags=[], strip=True),
            'topic_title': entry.topic.title,
            'topic_slug': entry.topic.slug,
            'content': render_emojis(bleach.clean(entry.content, tags=['p', 'br', 'b', 'i', 'strong', 'em'], strip=False)),
            'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M'),
            'timesince': (timezone.now() - entry.created_at).total_seconds() / 3600,
            'like_count': entry.like_count(),
            'liked': request.user.is_authenticated and entry.likes.filter(id=request.user.id).exists(),
            'is_owner': entry.user_id == request.user.id
        } for entry in entries]
        has_more = entries_query.count() > offset + limit
        return JsonResponse({'entries': data, 'has_more': has_more}, status=200)

    entries_query = Entry.objects.select_related('user', 'topic').annotate(
        like_count=models.Count('likes')
    ).filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by('-like_count', '-created_at')

    entries = entries_query[offset:offset + limit]

    data = [{
        'id': entry.id,
        'nickname': bleach.clean(entry.user.profile.nickname, tags=[], strip=True),
        'username': bleach.clean(entry.user.profile.username, tags=[], strip=True),
        'topic_title': entry.topic.title,
        'topic_slug': entry.topic.slug,
        'content': render_emojis(bleach.clean(entry.content, tags=['p', 'br', 'b', 'i', 'strong', 'em'], strip=False)),
        'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M'),
        'timesince': (timezone.now() - entry.created_at).total_seconds() / 3600,
        'like_count': entry.like_count(),
        'liked': request.user.is_authenticated and entry.likes.filter(id=request.user.id).exists(),
        'is_owner': entry.user_id == request.user.id
    } for entry in entries]
    
    has_more = entries_query.count() > offset + limit
    return JsonResponse({'entries': data, 'has_more': has_more}, status=200)

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
    
    data = [{
        'id': topic.id,
        'title': topic.title,
        'slug': topic.slug,
        'daily_entry_count': topic.daily_entry_count,
        'entry_count': topic.entry_count(),
        'vote_score': topic.vote_score(),
        'user_nickname': topic.user.profile.nickname,
        'created_at': topic.created_at.strftime('%d.%m.%Y %H:%M'),
        'first_entry_content': topic.entries.first().content[:790] if topic.entries.first() else '',
        'first_entry_full': topic.entries.first().content if topic.entries.first() else '',
        'user_upvoted': request.user in topic.upvotes.all() if request.user.is_authenticated else False,
        'user_downvoted': request.user in topic.downvotes.all() if request.user.is_authenticated else False
    } for topic in topics]
    
    has_more = topics_query.count() > offset + limit
    return JsonResponse({'topics': data, 'has_more': has_more}, status=200)