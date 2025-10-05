from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from ..models import Entry, Topic, Notification, Profile
from ..ai.smart_content import SmartContentGenerator

@require_http_methods(["GET"])
@login_required
def check_updates(request):
    """Real-time güncellemeler için API"""
    last_check = request.GET.get('last_check')
    if last_check:
        last_check = timezone.datetime.fromtimestamp(int(last_check) / 1000)
    else:
        last_check = timezone.now() - timedelta(minutes=5)
    
    # Yeni bildirimler
    new_notifications = request.user.notifications.filter(
        created_at__gt=last_check,
        is_read=False
    ).count()
    
    # Yeni entry'ler (takip edilen konularda)
    followed_topics = request.user.topic_bookmarks.values_list('topic_id', flat=True)
    new_entries = Entry.objects.filter(
        topic_id__in=followed_topics,
        created_at__gt=last_check
    ).exclude(user=request.user)
    
    # Online kullanıcı sayısı (son 5 dakikada aktif olanlar)
    online_threshold = timezone.now() - timedelta(minutes=5)
    online_users = Profile.objects.filter(
        user__last_login__gte=online_threshold
    ).count()
    
    return JsonResponse({
        'new_notifications': new_notifications,
        'new_entries': list(new_entries.values('id', 'topic__title')[:5]),
        'online_users': online_users,
        'timestamp': timezone.now().timestamp()
    })

@require_http_methods(["POST"])
@login_required
def ai_suggest_topics(request):
    """AI ile başlık önerileri"""
    generator = SmartContentGenerator()
    
    # Kullanıcının ilgi alanlarını belirle
    user_topics = request.user.entries.values_list('topic__title', flat=True)[:10]
    
    suggestions = generator.suggest_topics(user_topics)
    
    return JsonResponse({
        'suggestions': suggestions,
        'success': True
    })

@require_http_methods(["POST"])
@login_required
def ai_generate_hashtags(request):
    """İçerikten hashtag üret"""
    content = request.POST.get('content', '')
    
    if not content:
        return JsonResponse({'error': 'İçerik gerekli'}, status=400)
    
    generator = SmartContentGenerator()
    hashtags = generator.generate_hashtags(content)
    quality_score = generator.content_quality_score(content)
    
    return JsonResponse({
        'hashtags': hashtags,
        'quality_score': quality_score,
        'success': True
    })

@require_http_methods(["GET"])
def trending_topics(request):
    """Trend olan başlıklar"""
    # Son 24 saatte en çok entry alan başlıklar
    yesterday = timezone.now() - timedelta(days=1)
    
    trending = Topic.objects.filter(
        entries__created_at__gte=yesterday
    ).annotate(
        entry_count=Count('entries')
    ).order_by('-entry_count')[:10]
    
    trending_data = []
    for topic in trending:
        trending_data.append({
            'id': topic.id,
            'title': topic.title,
            'slug': topic.slug,
            'entry_count': topic.entry_count,
            'last_entry': topic.last_entry().created_at.isoformat() if topic.last_entry() else None
        })
    
    return JsonResponse({
        'trending_topics': trending_data,
        'success': True
    })

@require_http_methods(["GET"])
def live_stats(request):
    """Canlı istatistikler"""
    today = timezone.now().date()
    
    stats = {
        'total_users': Profile.objects.count(),
        'total_topics': Topic.objects.count(),
        'total_entries': Entry.objects.count(),
        'today_entries': Entry.objects.filter(created_at__date=today).count(),
        'online_users': Profile.objects.filter(
            user__last_login__gte=timezone.now() - timedelta(minutes=5)
        ).count(),
        'active_writers': Entry.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values('user').distinct().count()
    }
    
    return JsonResponse(stats)

@require_http_methods(["POST"])
@login_required
def quick_vote(request):
    """Hızlı oylama"""
    entry_id = request.POST.get('entry_id')
    vote_type = request.POST.get('vote_type')  # 'up' or 'down'
    
    try:
        entry = Entry.objects.get(id=entry_id)
        
        if vote_type == 'up':
            if request.user in entry.upvotes.all():
                entry.upvotes.remove(request.user)
                action = 'removed_upvote'
            else:
                entry.upvotes.add(request.user)
                entry.downvotes.remove(request.user)  # Çift oy engelle
                action = 'upvoted'
        
        elif vote_type == 'down':
            if request.user in entry.downvotes.all():
                entry.downvotes.remove(request.user)
                action = 'removed_downvote'
            else:
                entry.downvotes.add(request.user)
                entry.upvotes.remove(request.user)  # Çift oy engelle
                action = 'downvoted'
        
        return JsonResponse({
            'success': True,
            'action': action,
            'upvotes': entry.upvote_count(),
            'downvotes': entry.downvote_count(),
            'score': entry.vote_score()
        })
        
    except Entry.DoesNotExist:
        return JsonResponse({'error': 'Entry bulunamadı'}, status=404)

@require_http_methods(["GET"])
def search_suggestions(request):
    """Arama önerileri"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Başlık önerileri
    topic_suggestions = Topic.objects.filter(
        title__icontains=query
    ).values('title', 'slug')[:5]
    
    # Kullanıcı önerileri
    user_suggestions = Profile.objects.filter(
        Q(nickname__icontains=query) | Q(username__icontains=query)
    ).values('nickname', 'username')[:3]
    
    return JsonResponse({
        'topics': list(topic_suggestions),
        'users': list(user_suggestions),
        'success': True
    })