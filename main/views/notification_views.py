from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from ..models import Notification
from .base import profile_required

@login_required
@profile_required
def notifications(request):
    category = request.GET.get('category', 'all')
    
    notifications_query = request.user.notifications.all()
    
    if category != 'all':
        notifications_query = notifications_query.filter(category=category)
    
    notifications = notifications_query[:20]
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    return render(request, 'main/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'category': category,
    })

@login_required
@profile_required
@csrf_protect
def mark_as_read(request, notification_id):
    if request.method == 'POST':
        try:
            notification = request.user.notifications.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'error': 'Bildirim bulunamadı'}, status=404)
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

@login_required
@profile_required
@csrf_protect
def mark_all_as_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

def create_notification(user, notification_type, message, from_user=None, related_topic=None, related_entry=None, category='interaction'):
    """Bildirim oluşturma yardımcı fonksiyonu"""
    if user != from_user:  # Kendine bildirim gönderme
        Notification.objects.create(
            user=user,
            notification_type=notification_type,
            category=category,
            message=message,
            from_user=from_user,
            related_topic=related_topic,
            related_entry=related_entry
        )