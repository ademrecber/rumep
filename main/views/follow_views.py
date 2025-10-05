from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from ..models import Follow, Topic, Entry
from .base import profile_required
from .notification_views import create_notification

@login_required
@profile_required
@csrf_protect
def toggle_follow(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)
        
        if target_user == request.user:
            return JsonResponse({'error': 'Kendinizi takip edemezsiniz'}, status=400)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )
        
        if not created:
            follow.delete()
            is_following = False
        else:
            is_following = True
            # Bildirim oluştur
            create_notification(
                user=target_user,
                notification_type='mention',
                message=f'{request.user.profile.nickname} sizi takip etmeye başladı',
                from_user=request.user
            )
        
        follower_count = target_user.followers.count()
        
        return JsonResponse({
            'is_following': is_following,
            'follower_count': follower_count
        })
    
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

def get_following_feed(user):
    """Takip edilen kullanıcıların içeriklerini getir"""
    following_users = user.following.values_list('following', flat=True)
    
    # Takip edilen kullanıcıların topic'leri
    topics = Topic.objects.filter(user__in=following_users).order_by('-updated_at')[:20]
    
    return topics