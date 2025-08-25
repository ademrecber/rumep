from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from ..models import Post, Comment, PostVote, CommentVote, Category, Critique, Profile, CritiqueVote
from ..forms import PostForm, CommentForm, CritiqueForm, CritiqueVoteForm
from .base import profile_required
from .comment_views import build_comment_tree
import bleach
from django.db import models
from django.utils import timezone
from datetime import timedelta
import logging
from ..utils.embed_utils import generate_embed_code
from ..utils.shortener import create_short_link
import os
from django.conf import settings
from ..templatetags.post_tags import render_emojis

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@login_required
@profile_required
@csrf_protect
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user or request.user.is_staff:
        post.delete()
    return redirect('home')

@login_required
@profile_required
@csrf_protect
def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('user__profile'), id=pk)
    post.views += 1
    post.save(update_fields=['views'])

    referer = request.META.get('HTTP_REFERER', '')
    if 'popular-critiques' in referer:
        request.session['return_page'] = 'popular_critiques'
    elif 'popular' in referer:
        request.session['return_page'] = 'popular'
    elif 'search' in referer:
        request.session['return_page'] = 'search'
    else:
        request.session['return_page'] = 'home'

    comments = Comment.objects.filter(post=post).select_related('user__profile').annotate(
        reply_count=models.Count('replies'),
        total_score=(
            (models.F('upvotes') - models.F('downvotes')) +
            models.F('reply_count') +
            models.F('views')
        ) / 3.0
    ).order_by('-total_score', 'created_at')
    comment_tree = build_comment_tree(comments)

    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.text = bleach.clean(comment.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)
            if parent_id := request.POST.get('parent_id'):
                comment.parent = get_object_or_404(Comment, id=parent_id)
            comment.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment_id': str(comment.id),
                    'nickname': bleach.clean(comment.user.profile.nickname, tags=['p', 'br'], strip=True),
                    'username': bleach.clean(comment.user.profile.username, tags=['p', 'br'], strip=True),
                    'text': render_emojis(comment.text),
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'parent_id': str(comment.parent_id) if comment.parent_id else None
                }, status=201)
            return redirect('post_detail', pk=post.id)
    
    context = {
        'post': post,
        'comment_tree': comment_tree,
        'form': form,
        'comment_count': comments.count(),
        'like_count': post.like_count(),
        'post_id': str(post.id),
        'bookmarked': request.user in post.bookmarks.all()
    }
    return render(request, 'main/post_detail.html', context)

@login_required
@profile_required
@csrf_protect
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    liked = user in post.likes.all()
    
    if liked:
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
    
    post.save()
    return JsonResponse({
        'liked': liked,
        'like_count': post.like_count()
    }, status=200)

@login_required
@profile_required
@csrf_protect
@require_POST
def bookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    bookmarked = user in post.bookmarks.all()
    
    if bookmarked:
        post.bookmarks.remove(user)
        bookmarked = False
    else:
        post.bookmarks.add(user)
        bookmarked = True
    
    post.save()
    return JsonResponse({
        'bookmarked': bookmarked,
        'bookmark_count': post.bookmarks.count()
    }, status=200)

@login_required
@profile_required
@csrf_protect
@require_POST
def vote_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    vote_type = request.POST.get('vote')
    if vote_type in ['up', 'down']:
        existing_vote = PostVote.objects.filter(user=request.user, post=post).first()
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                if vote_type == 'up':
                    post.upvotes -= 1
                else:
                    post.downvotes -= 1
                existing_vote.delete()
            else:
                if vote_type == 'up':
                    post.upvotes += 1
                    post.downvotes -= 1 if post.downvotes > 0 else 0
                else:
                    post.downvotes += 1
                    post.upvotes -= 1 if post.upvotes > 0 else 0
                existing_vote.vote_type = vote_type
                existing_vote.save()
        else:
            if vote_type == 'up':
                post.upvotes += 1
            else:
                post.downvotes += 1
            PostVote.objects.create(user=request.user, post=post, vote_type=vote_type)
        post.save()
        return JsonResponse({'upvotes': post.upvotes, 'downvotes': post.downvotes}, status=200)
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

@login_required
@profile_required
@csrf_protect
@require_POST
def vote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    vote_type = request.POST.get('vote')
    
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Geçersiz oy türü'}, status=400)

    existing_vote = CommentVote.objects.filter(user=request.user, comment=comment).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            if vote_type == 'up':
                comment.upvotes -= 1
            else:
                comment.downvotes -= 1
            existing_vote.delete()
        else:
            if vote_type == 'up':
                comment.upvotes += 1
                comment.downvotes -= 1 if comment.downvotes > 0 else 0
            else:
                comment.downvotes += 1
                comment.upvotes -= 1 if comment.upvotes > 0 else 0
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        if vote_type == 'up':
            comment.upvotes += 1
        else:
            comment.downvotes += 1
        CommentVote.objects.create(user=request.user, comment=comment, vote_type=vote_type)
    
    comment.save()
    return JsonResponse({
        'upvotes': comment.upvotes,
        'downvotes': comment.downvotes,
        'total': comment.upvotes - comment.downvotes
    }, status=200)

@login_required
@profile_required
@csrf_protect
def load_more(request):
    offset = int(request.GET.get('offset', 0))
    limit = 10
    posts = Post.objects.all().annotate(
        critique_count=models.Count('critiques')
    ).order_by('-created_at')[offset:offset + limit]
    data = [{
        'id': str(post.id),
        'nickname': bleach.clean(post.user.profile.nickname, tags=['p', 'br'], strip=True),
        'username': bleach.clean(post.user.profile.username, tags=['p', 'br'], strip=True),
        'short_id': post.short_id,
        'title': post.title,
        'text': render_emojis(bleach.clean(post.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)),
        'category': post.category.name if post.category else 'No category',
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
        'like_count': post.like_count(),
        'liked': request.user in post.likes.all(),
        'bookmarked': request.user in post.bookmarks.all(),
        'comment_count': post.comments.count(),
        'critique_count': post.critique_count,
        'views': post.views,
        'upvotes': post.upvotes,
        'downvotes': post.downvotes,
        'embed_code': post.embed_code or '',
        'link': post.link or '',
        'is_owner': post.user == request.user
    } for post in posts]
    has_more = Post.objects.count() > offset + limit
    return JsonResponse({'posts': data, 'has_more': has_more}, status=200)

@login_required
@profile_required
@csrf_protect
@require_POST
def add_critique(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CritiqueForm(request.POST)
    errors = form.errors.as_json() if not form.is_valid() else None
    if form.is_valid():
        critique = form.save(commit=False)
        critique.user = request.user
        critique.post = post
        critique.text = bleach.clean(critique.text, tags=['p', 'b', 'i', 'img'], attributes={'img': ['src', 'alt']}, strip=False)
        critique.save()
        logger.debug(f"Değerlendirme eklendi, critique_id: {critique.id}, post_id: {post_id}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'critique_id': str(critique.id),
                'short_id': critique.short_id,
                'nickname': bleach.clean(critique.user.profile.nickname, tags=['p', 'br'], strip=True),
                'username': bleach.clean(critique.user.profile.username, tags=['p', 'br'], strip=True),
                'text': render_emojis(critique.text),
                'created_at': critique.created_at.strftime('%Y-%m-%d %H:%M'),
                'rating': critique.rating,
                'is_owner': critique.user == request.user
            }, status=201)
    logger.warning(f"Değerlendirme eklenemedi, post_id: {post_id}, hatalar: {errors}")
    return JsonResponse({'success': False, 'errors': errors or 'Form geçersiz, detaylar alınamadı'}, status=400)

@login_required
@profile_required
def list_critiques(request):
    post_id = request.GET.get('post_id')
    if not post_id:
        return JsonResponse({'error': 'Post ID gerekli'}, status=400)
    critiques = Critique.objects.filter(post_id=post_id).select_related('user__profile').order_by('-rating', '-created_at')[:5]
    user = request.user
    data = [{
        'id': str(critique.id),
        'short_id': critique.short_id,
        'nickname': bleach.clean(critique.user.profile.nickname, tags=['p', 'br'], strip=True),
        'username': bleach.clean(critique.user.profile.username, tags=['p', 'br'], strip=True),
        'text': render_emojis(bleach.clean(critique.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)),
        'created_at': critique.created_at.strftime('%Y-%m-%d %H:%M'),
        'rating': critique.rating,
        'is_owner': critique.user == user,
        'user_rating': CritiqueVote.objects.filter(critique=critique, user=user).first().rating if CritiqueVote.objects.filter(critique=critique, user=user).exists() else None
    } for critique in critiques]
    return JsonResponse({'critiques': data}, status=200)

@login_required
@profile_required
@csrf_protect
@require_POST
def delete_critique(request, critique_id):
    critique = get_object_or_404(Critique, id=critique_id)
    if critique.user == request.user:
        critique.delete()
        logger.debug(f"Değerlendirme silindi, critique_id: {critique_id}")
        return JsonResponse({'success': True}, status=200)
    logger.warning(f"Yetkisiz değerlendirme silme denemesi, user: {request.user.username}, critique_id: {critique_id}")
    return JsonResponse({'success': False, 'error': 'Yetkisiz işlem'}, status=403)

@login_required
@profile_required
@csrf_protect
@require_POST
def vote_critique(request, critique_id):
    critique = get_object_or_404(Critique, id=critique_id)
    if critique.user == request.user:
        return JsonResponse({'success': False, 'error': 'Kendi eleştirinize puan veremezsiniz'}, status=403)
    
    form = CritiqueVoteForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        existing_vote = CritiqueVote.objects.filter(user=request.user, critique=critique).first()
        if existing_vote:
            critique.rating = (critique.rating * critique.votes.count() - existing_vote.rating + rating) / critique.votes.count()
            existing_vote.rating = rating
            existing_vote.save()
        else:
            CritiqueVote.objects.create(user=request.user, critique=critique, rating=rating)
            total_votes = critique.votes.count()
            critique.rating = (critique.rating * (total_votes - 1) + rating) / total_votes if total_votes > 0 else rating
        critique.save()
        logger.debug(f"Değerlendirme oylandı, critique_id: {critique_id}, rating: {rating}")
        return JsonResponse({
            'success': True,
            'rating': critique.rating,
            'user_rating': rating
        }, status=200)
    logger.warning(f"Değerlendirme oylama hatası, critique_id: {critique_id}, hatalar: {form.errors.as_json()}")
    return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)

@login_required
@profile_required
def popular_critiques(request):
    request.session['return_page'] = 'popular_critiques'
    period = request.GET.get('period', 'today')
    critiques = Critique.objects.select_related('user__profile', 'post').annotate(
        vote_count=models.Count('votes')
    ).order_by('-rating', '-vote_count')

    if period == 'today':
        critiques = critiques.filter(created_at__date=timezone.now().date())
    elif period == 'yesterday':
        critiques = critiques.filter(created_at__date=timezone.now().date() - timedelta(days=1))
    elif period == 'week':
        critiques = critiques.filter(created_at__gte=timezone.now() - timedelta(days=7))

    critiques = critiques[:10]
    user = request.user
    context = {
        'critiques': [{
            'id': str(critique.id),
            'short_id': critique.short_id,
            'post_id': str(critique.post.id),
            'post_short_id': critique.post.short_id,
            'post_title': critique.post.title or '',
            'nickname': critique.user.profile.nickname,
            'username': critique.user.profile.username,
            'text': render_emojis(critique.text),
            'created_at': critique.created_at.strftime('%Y-%m-%d %H:%M'),
            'rating': critique.rating,
            'is_owner': critique.user == user,
            'user_rating': CritiqueVote.objects.filter(critique=critique, user=user).first().rating if CritiqueVote.objects.filter(critique=critique, user=user).exists() else None
        } for critique in critiques],
        'period': period
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(context, status=200)
    return render(request, 'main/popular_critiques.html', context)

def redirect_short_link(request, short_code):
    from ..utils.shortener import resolve_short_link
    original_url = resolve_short_link(short_code)
    if original_url:
        return redirect(original_url)
    return redirect('home')

def get_emojis(request):
    emoji_dir = os.path.join(settings.STATICFILES_DIRS[0], 'emojis')
    emojis = []
    for filename in os.listdir(emoji_dir):
        if filename.endswith('.svg'):
            name = filename.replace('.svg', '')
            emojis.append({
                'name': name,
                'shortcode': f':{name}:',
                'src': f'/static/emojis/{filename}'
            })
    return JsonResponse({'emojis': emojis}, status=200)