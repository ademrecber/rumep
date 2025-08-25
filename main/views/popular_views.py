import bleach
from django.shortcuts import render
from django.utils.timezone import localdate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from ..models import Post
from .base import profile_required
from datetime import timedelta
from ..templatetags.post_tags import render_emojis
import logging

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@login_required
@profile_required
def popular(request, period='today'):
    now = timezone.now()
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'yesterday':
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'weekly':
        start_date = now - timedelta(days=7)
        end_date = now
    elif period == 'monthly':
        start_date = now - timedelta(days=30)
        end_date = now
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now

    posts = Post.objects.annotate(
        total_score=(
            (models.F('upvotes') - models.F('downvotes')) +
            models.Count('comments') +
            models.F('views')
        ) / 3.0
    ).filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by('-total_score', '-created_at')[:10]

    # İşlenmiş postları bir listeye kopyala
    processed_posts = []
    for post in posts:
        original_text = post.text
        rendered_text = render_emojis(bleach.clean(post.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False))
        logger.debug(f"Post ID: {post.id}, Original Text: {original_text}, Rendered Text: {rendered_text}")
        post_dict = {
            'id': post.id,
            'title': post.title,
            'text': rendered_text,
            'user': post.user,
            'short_id': post.short_id,
            'created_at': post.created_at,
            'views': post.views,
            'upvotes': post.upvotes,
            'downvotes': post.downvotes,
            'likes': post.likes,
            'bookmarks': post.bookmarks,
            'comments': post.comments,
            'critiques': post.critiques,
            'total_score': post.total_score,
            'link': post.link,
            'embed_code': post.embed_code,
        }
        processed_posts.append(post_dict)

    return render(request, 'main/popular/popular.html', {
        'posts': processed_posts,
        'period': period,
        'user': request.user
    })

@login_required
@profile_required
@csrf_protect
def load_more_popular(request):
    offset = int(request.GET.get('offset', 0))
    limit = 10
    period = request.GET.get('period', 'today')
    
    now = timezone.now()
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'yesterday':
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'weekly':
        start_date = now - timedelta(days=7)
        end_date = now
    elif period == 'monthly':
        start_date = now - timedelta(days=30)
        end_date = now
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now

    posts_query = Post.objects.annotate(
        total_score=(
            (models.F('upvotes') - models.F('downvotes')) +
            models.Count('comments') +
            models.F('views')
        ) / 3.0,
        critique_count=models.Count('critiques')
    ).filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by('-total_score', '-created_at')

    posts = posts_query[offset:offset + limit]

    data = [{
        'id': str(post.id),
        'nickname': bleach.clean(post.user.profile.nickname, tags=['p', 'br'], strip=True),
        'username': bleach.clean(post.user.profile.username, tags=['p', 'br'], strip=True),
        'short_id': post.short_id,
        'title': post.title if post.title else '',
        'text': render_emojis(bleach.clean(post.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)),
        'link': post.link,
        'embed_code': post.embed_code or '',
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
        'timesince': (timezone.now() - post.created_at).total_seconds() / 3600,
        'like_count': post.like_count(),
        'liked': request.user.is_authenticated and post.likes.filter(id=request.user.id).exists(),
        'bookmarked': request.user.is_authenticated and post.bookmarks.filter(id=request.user.id).exists(),
        'comment_count': post.comments.count(),
        'critique_count': post.critique_count,
        'views': post.views,
        'upvotes': post.upvotes,
        'downvotes': post.downvotes,
        'total_score': float(post.total_score),
        'is_owner': post.user_id == request.user.id
    } for post in posts]
    has_more = posts_query.count() > offset + limit
    return JsonResponse({'posts': data, 'has_more': has_more}, status=200)