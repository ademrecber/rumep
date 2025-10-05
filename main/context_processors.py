from .models import Notification, Topic, Profile
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

def notification_count(request):
    """Okunmamış bildirim sayısını tüm template'lerde kullanılabilir hale getirir"""
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}

def user_role_context(request):
    """Kullanıcı rol bilgilerini tüm template'lerde kullanılabilir hale getirir"""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        return {
            'user_role': profile.user_role,
            'user_role_display': profile.get_user_role_display(),
            'user_role_badge': profile.get_role_display_with_badge(),
            'is_writer': profile.is_writer(),
            'is_moderator': profile.is_moderator(),
            'is_admin': profile.is_admin(),
            'is_super_admin': profile.is_super_admin(),
        }
    return {
        'user_role': 'user',
        'user_role_display': _('Kullanıcı'),
        'user_role_badge': _('Kullanıcı'),
        'is_writer': False,
        'is_moderator': False,
        'is_admin': False,
        'is_super_admin': False,
    }

def sidebar_data(request):
    """Sağ sidebar için popüler başlıklar ve aktif yazarlar"""
    # Popüler başlıklar (tüm zamanlar)
    popular_topics = Topic.objects.annotate(
        total_entries=Count('entries')
    ).filter(total_entries__gt=0).order_by('-total_entries')[:5]
    
    # Aktif yazarlar (en çok topic ve entry yazan)
    active_authors = Profile.objects.annotate(
        topic_count=Count('user__topic'),
        entry_count=Count('user__entry')
    ).filter(
        topic_count__gt=0
    ).order_by('-topic_count', '-entry_count')[:5]
    
    return {
        'sidebar_popular_topics': popular_topics,
        'sidebar_active_authors': active_authors,
    }