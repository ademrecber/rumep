from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from ..models import Profile, Topic, Entry
from .base import profile_required
from ..templatetags.post_tags import render_emojis
import bleach

@csrf_protect
def login_page(request):
    if request.user.is_authenticated:
        if not hasattr(request.user, 'profile'):
            return redirect('complete_profile')
        return redirect('home')
    
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not hasattr(user, 'profile'):
                return redirect('complete_profile')
            return redirect('home')
        else:
            return render(request, 'main/login.html', {'error': 'Kullanıcı adı veya şifre hatalı'})
    
    return render(request, 'main/login.html')

@login_required
def complete_profile(request):
    if hasattr(request.user, 'profile'):
        return redirect('home')
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        username = request.POST.get('username')
        preferred_language = request.POST.get('preferred_language', 'tr')
        if Profile.objects.filter(nickname=nickname).exists():
            return render(request, 'main/complete_profile.html', {'error': 'Bu takma ad zaten alınmış.'})
        if Profile.objects.filter(username=username).exists():
            return render(request, 'main/complete_profile.html', {'error': 'Bu kullanıcı adı zaten alınmış.'})
        Profile.objects.create(
            user=request.user, 
            nickname=nickname, 
            username=username, 
            preferred_language=preferred_language,
            dark_mode=False
        )
        return redirect('home')
    return render(request, 'main/complete_profile.html')

@login_required
@profile_required
def profile(request, username=None):
    from ..models import Follow
    tab = request.GET.get('tab', 'posts')
    
    if username:
        profile = get_object_or_404(Profile, username=username)
        is_own_profile = (profile.user == request.user)
        
        # Kendi profiline tıklarsa profile sayfasına yönlendir
        if is_own_profile:
            return redirect('profile')
            
        template = 'main/profile_detail.html'
        
        # Takip bilgileri
        follower_count = profile.user.followers.count()
        following_count = profile.user.following.count()
        is_following = False
        
        if request.user.is_authenticated:
            is_following = Follow.objects.filter(
                follower=request.user,
                following=profile.user
            ).exists()
        
        context = {
            'profile': profile,
            'tab': tab,
            'is_own_profile': is_own_profile,
            'follower_count': follower_count,
            'following_count': following_count,
            'is_following': is_following
        }
    else:
        profile = request.user.profile
        is_own_profile = True
        template = 'main/profile.html'
        
        context = {
            'profile': profile,
            'tab': tab,
            'is_own_profile': is_own_profile
        }
    
    if tab == 'topics':
        topics = Topic.objects.filter(user=profile.user).order_by('-created_at')
        context['topics'] = topics
    elif tab == 'entries':
        entries = Entry.objects.filter(user=profile.user).select_related('topic').order_by('-created_at')
        context['entries'] = entries
    elif tab == 'votes':
        upvoted_topics = profile.user.upvoted_topics.all().order_by('-created_at')[:20]
        upvoted_entries = profile.user.upvoted_entries.all().select_related('topic').order_by('-created_at')[:20]
        context['upvoted_topics'] = upvoted_topics
        context['upvoted_entries'] = upvoted_entries
    elif tab == 'bookmarks' and profile.user == request.user:
        from ..models import Bookmark, TopicBookmark
        # Entry bookmarks
        entry_bookmarks = Bookmark.objects.filter(user=profile.user).select_related(
            'entry__user__profile', 'entry__topic'
        ).order_by('-created_at')
        bookmarked_entries = [bookmark.entry for bookmark in entry_bookmarks]
        
        # Topic bookmarks
        topic_bookmarks = TopicBookmark.objects.filter(user=profile.user).select_related(
            'topic__user__profile'
        ).order_by('-created_at')
        bookmarked_topics = [bookmark.topic for bookmark in topic_bookmarks]
        
        context.update({
            'bookmarked_entries': bookmarked_entries,
            'bookmarked_topics': bookmarked_topics
        })
        print(f"DEBUG: bookmarked_entries count: {len(bookmarked_entries)}")
        print(f"DEBUG: bookmarked_topics count: {len(bookmarked_topics)}")

    return render(request, template, context)

@login_required
@profile_required
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile
        nickname = request.POST.get('nickname')
        username = request.POST.get('username')
        biography = request.POST.get('biography', '')
        preferred_language = request.POST.get('preferred_language', 'tr')
        
        # Temel sosyal medya alanları (sadece Instagram ve Twitter)
        instagram_username = request.POST.get('instagram_username', '')
        twitter_username = request.POST.get('twitter_username', '')

        # Kullanıcı adı kontrolü
        if username != profile.username and Profile.objects.filter(username=username).exclude(user=request.user).exists():
            return render(request, 'main/profile.html', {
                'error': 'Bu kullanıcı adı zaten alınmış.',
                'profile': profile,
                'tab': 'posts'
            })
        
        # Profili güncelle
        profile.nickname = nickname
        profile.username = username
        profile.biography = biography
        profile.instagram_username = instagram_username
        profile.twitter_username = twitter_username

        profile.preferred_language = preferred_language
        profile.save()
        return redirect('profile')
    return redirect('profile')

@login_required
@profile_required
def update_social_links(request):
    if request.method == 'POST':
        profile = request.user.profile
        
        # Sosyal medya alanlarını güncelle
        profile.facebook_username = request.POST.get('facebook_username', '')
        profile.tiktok_username = request.POST.get('tiktok_username', '')
        profile.github_username = request.POST.get('github_username', '')
        profile.youtube_url = request.POST.get('youtube_url', '')
        profile.linkedin_url = request.POST.get('linkedin_url', '')
        profile.website_url = request.POST.get('website_url', '')
        
        profile.save()
        return redirect('profile')
    return redirect('profile')

@login_required
@profile_required
@csrf_protect
def update_visibility(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True}, status=200)
        return redirect('profile')
    elif request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True}, status=200)
    return JsonResponse({'success': False, 'errors': 'Geçersiz istek'}, status=400)

@login_required
@profile_required
def search(request):
    query = request.GET.get('q', '').strip()
    results = {'users': []}
    if query.startswith('@'):
        username = query[1:]
        results['users'] = Profile.objects.filter(username__icontains=username)
    return render(request, 'main/search.html', {'query': query, 'results': results})

