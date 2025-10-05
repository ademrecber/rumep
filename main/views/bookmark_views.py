from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from ..models import Entry, Bookmark, Topic, TopicBookmark
from .base import profile_required

@login_required
@profile_required
@csrf_protect
def toggle_bookmark(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(Entry, id=entry_id)
        
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            entry=entry
        )
        
        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True
        
        bookmark_count = entry.bookmarks.count()
        
        return JsonResponse({
            'is_bookmarked': is_bookmarked,
            'bookmark_count': bookmark_count
        })
    
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

@login_required
@profile_required
@csrf_protect
def toggle_topic_bookmark(request, topic_slug):
    if request.method == 'POST':
        topic = get_object_or_404(Topic, slug=topic_slug)
        
        bookmark, created = TopicBookmark.objects.get_or_create(
            user=request.user,
            topic=topic
        )
        
        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True
        
        bookmark_count = topic.topic_bookmarks.count()
        
        return JsonResponse({
            'is_bookmarked': is_bookmarked,
            'bookmark_count': bookmark_count
        })
    
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

@login_required
@profile_required
def user_bookmarks(request):
    entry_bookmarks = Bookmark.objects.filter(user=request.user).select_related(
        'entry__user__profile', 'entry__topic'
    ).order_by('-created_at')
    
    topic_bookmarks = TopicBookmark.objects.filter(user=request.user).select_related(
        'topic__user__profile'
    ).order_by('-created_at')
    
    context = {
        'entry_bookmarks': entry_bookmarks,
        'topic_bookmarks': topic_bookmarks,
        'total_entry_bookmarks': entry_bookmarks.count(),
        'total_topic_bookmarks': topic_bookmarks.count()
    }
    
    return render(request, 'main/user_bookmarks.html', context)