from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from ..models import Profile, Post, Comment, Critique
from .base import profile_required
from ..templatetags.post_tags import render_emojis
import bleach

def login_page(request):
    if request.user.is_authenticated:
        if not hasattr(request.user, 'profile'):
            return redirect('complete_profile')
        return redirect('home')
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
        Profile.objects.create(user=request.user, nickname=nickname, username=username, preferred_language=preferred_language)
        return redirect('home')
    return render(request, 'main/complete_profile.html')

@login_required
@profile_required
def profile(request, username=None):
    tab = request.GET.get('tab', 'posts')
    
    if username:
        profile = get_object_or_404(Profile, username=username)
        is_own_profile = (profile.user == request.user)
        template = 'main/profile_detail.html'
    else:
        profile = request.user.profile
        is_own_profile = True
        template = 'main/profile.html'

    context = {
        'profile': profile,
        'tab': tab,
        'posts_count': Post.objects.filter(user=profile.user).count(),
        'is_own_profile': is_own_profile
    }

    posts_visible = getattr(profile, 'posts_visible', True)
    critiques_visible = getattr(profile, 'critiques_visible', True)
    comments_visible = getattr(profile, 'comments_visible', True)

    if tab == 'posts' and (posts_visible or is_own_profile):
        posts = Post.objects.filter(user=profile.user).order_by('-created_at')
        context['posts'] = [{
            'id': post.id,
            'user': post.user,
            'text': render_emojis(bleach.clean(post.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)),
            'link': post.link,
            'embed_code': post.embed_code,
            'created_at': post.created_at,
            'short_id': post.short_id,
            'title': post.title,
            'like_count': post.like_count(),
            'comments': post.comments.count(),
            'critiques': post.critiques.count(),
            'views': post.views,
            'upvotes': post.upvotes,
            'downvotes': post.downvotes
        } for post in posts]
    elif tab == 'likes' and is_own_profile:
        liked_posts = Post.objects.filter(likes=profile.user).order_by('-created_at')
        context['liked_posts'] = [{
            'id': post.id,
            'user': post.user,
            'text': render_emojis(bleach.clean(post.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)),
            'link': post.link,
            'embed_code': post.embed_code,
            'created_at': post.created_at,
            'short_id': post.short_id,
            'title': post.title,
            'like_count': post.like_count(),
            'comments': post.comments.count(),
            'critiques': post.critiques.count(),
            'views': post.views,
            'upvotes': post.upvotes,
            'downvotes': post.downvotes
        } for post in liked_posts]
    elif tab == 'comments' and (comments_visible or is_own_profile):
        comments = Comment.objects.filter(user=profile.user).order_by('-created_at')
        context['comments'] = [{
            'id': comment.id,
            'user': comment.user,
            'text': render_emojis(bleach.clean(comment.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)),
            'created_at': comment.created_at,
            'post': comment.post
        } for comment in comments]
    elif tab == 'critiques' and (critiques_visible or is_own_profile):
        critiques = Critique.objects.filter(user=profile.user).order_by('-created_at')
        context['critiques'] = [{
            'id': critique.id,
            'user': critique.user,
            'text': render_emojis(bleach.clean(critique.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)),
            'created_at': critique.created_at,
            'post': critique.post,
            'rating': critique.rating,
            'short_id': critique.short_id
        } for critique in critiques]
    elif tab == 'bookmarks' and is_own_profile:
        bookmarked_posts = Post.objects.filter(bookmarks=profile.user).order_by('-created_at')
        context['bookmarked_posts'] = [{
            'id': post.id,
            'user': post.user,
            'text': render_emojis(bleach.clean(post.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)),
            'link': post.link,
            'embed_code': post.embed_code,
            'created_at': post.created_at,
            'short_id': post.short_id,
            'title': post.title,
            'like_count': post.like_count(),
            'comments': post.comments.count(),
            'critiques': post.critiques.count(),
            'views': post.views,
            'upvotes': post.upvotes,
            'downvotes': post.downvotes
        } for post in bookmarked_posts]

    return render(request, template, context)

@login_required
@profile_required
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile
        nickname = request.POST.get('nickname')
        username = request.POST.get('username')
        instagram_username = request.POST.get('instagram_username', '')
        twitter_username = request.POST.get('twitter_username', '')
        preferred_language = request.POST.get('preferred_language', 'tr')

        if username != profile.username and Profile.objects.filter(username=username).exclude(user=request.user).exists():
            return render(request, 'main/profile.html', {
                'error': 'Bu kullanıcı adı zaten alınmış.',
                'profile': profile,
                'tab': 'posts',
                'posts': Post.objects.filter(user=request.user),
                'posts_count': Post.objects.filter(user=request.user).count()
            })

        if instagram_username and Profile.objects.filter(instagram_username=instagram_username).exclude(user=request.user).exists():
            return render(request, 'main/profile.html', {
                'error': 'Bu Instagram kullanıcı adı zaten alınmış.',
                'profile': profile,
                'tab': 'posts',
                'posts': Post.objects.filter(user=request.user),
                'posts_count': Post.objects.filter(user=request.user).count()
            })
        if twitter_username and Profile.objects.filter(twitter_username=twitter_username).exclude(user=request.user).exists():
            return render(request, 'main/profile.html', {
                'error': 'Bu Twitter kullanıcı adı zaten alınmış.',
                'profile': profile,
                'tab': 'posts',
                'posts': Post.objects.filter(user=request.user),
                'posts_count': Post.objects.filter(user=request.user).count()
            })

        profile.nickname = nickname
        profile.username = username
        profile.instagram_username = instagram_username
        profile.twitter_username = twitter_username
        profile.preferred_language = preferred_language
        profile.save()
        return redirect('profile')
    return redirect('profile')

@login_required
@profile_required
@csrf_protect
def update_visibility(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.posts_visible = request.POST.get('posts_visible') == 'on'
        profile.critiques_visible = request.POST.get('critiques_visible') == 'on'
        profile.comments_visible = request.POST.get('comments_visible') == 'on'
        profile.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'posts_visible': profile.posts_visible,
                'critiques_visible': profile.critiques_visible,
                'comments_visible': profile.comments_visible
            }, status=200)
        return redirect('profile')
    elif request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'posts_visible': profile.posts_visible,
            'critiques_visible': profile.critiques_visible,
            'comments_visible': profile.comments_visible
        }, status=200)
    return JsonResponse({'success': False, 'errors': 'Geçersiz istek'}, status=400)

@login_required
@profile_required
def search(request):
    query = request.GET.get('q', '').strip()
    results = {'users': [], 'posts': [], 'ids': []}
    if query.startswith('@'):
        username = query[1:]
        results['users'] = Profile.objects.filter(username__icontains=username)
    elif query.startswith('$'):
        short_id = query[1:]
        results['ids'] = Post.objects.filter(short_id__icontains=short_id)
    else:
        results['ids'] = Post.objects.filter(short_id__icontains=query)
        results['posts'] = Post.objects.filter(text__icontains=query)
    return render(request, 'main/search.html', {'query': query, 'results': results})

@login_required
@profile_required
@csrf_protect
@require_POST
def unlike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        post.save()
    tab = request.GET.get('tab', 'likes')
    return redirect(f"/profile/?tab={tab}")

@login_required
@profile_required
@csrf_protect
@require_POST
def remove_bookmark(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.bookmarks.all():
        post.bookmarks.remove(request.user)
        post.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'bookmarked': False,
            'bookmark_count': post.bookmarks.count()
        }, status=200)
    tab = request.GET.get('tab', 'bookmarks')
    return redirect(f"/profile/?tab={tab}")

@login_required
@profile_required
@csrf_protect
@require_POST
def profile_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user or request.user.is_staff:
        post.delete()
    tab = request.GET.get('tab', 'posts')
    return redirect(f"/profile/?tab={tab}")

@login_required
@profile_required
@csrf_protect
@require_POST
def profile_delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
    tab = request.GET.get('tab', 'comments')
    return redirect(f"/profile/?tab={tab}")

@login_required
@profile_required
@csrf_protect
@require_POST
def profile_delete_critique(request, critique_id):
    critique = get_object_or_404(Critique, id=critique_id)
    if critique.user == request.user:
        critique.delete()
    tab = request.GET.get('tab', 'critiques')
    return redirect(f"/profile/?tab={tab}")