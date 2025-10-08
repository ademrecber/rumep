from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
from django.contrib import messages
from django.utils import timezone
from ..models import Topic, Entry
from ..forms import TopicForm, EntryForm
from .base import profile_required
from ..security import rate_limit, sanitize_input
import bleach

def home(request):
    from ..models import Follow, Category
    request.session['return_page'] = 'home'
    topic_form = TopicForm()
    entry_form = EntryForm()
    
    tab = request.GET.get('tab', 'home')
    category_slug = request.GET.get('category')
    
    if tab == 'following' and request.user.is_authenticated:
        # Takip edilen kullanıcıların topic'leri
        following_users = request.user.following.values_list('following', flat=True)
        topics = Topic.objects.with_related().filter(user__in=following_users)[:20]
    elif tab == 'category' and category_slug:
        # Belirli kategorinin topic'leri
        try:
            selected_category = Category.objects.get(slug=category_slug)
            topics = Topic.objects.with_related().filter(categories=selected_category)[:20]
        except Category.DoesNotExist:
            topics = Topic.objects.none()
    else:
        # Tüm topic'ler - optimized queryset kullan
        topics = Topic.objects.with_related().order_by('-created_at')[:10]
    
    # Kategoriler sekmesi için kategorileri getir
    all_categories = Category.objects.all().order_by('name')
    
    # Her kategori için topic sayısını hesapla
    for category in all_categories:
        category.topic_count = category.topics.count()
    
    # Kategori sekmesi için ayrı topic'ler
    category_topics = None
    if tab == 'category' and category_slug:
        category_topics = topics
    
    return render(request, 'main/home.html', {
        'topics': topics,
        'topic_form': topic_form,
        'entry_form': entry_form,
        'tab': tab,
        'all_categories': all_categories,
        'category_topics': category_topics,
        'user': request.user,
    })

@login_required
def create_topic(request):
    if request.method != 'POST':
        return redirect('home')
        
    topic_form = TopicForm(request.POST)
    entry_form = EntryForm(request.POST)
    
    if not (topic_form.is_valid() and entry_form.is_valid()):
        return redirect('home')
    
    try:
        # Başlık oluştur
        topic = topic_form.save(commit=False)
        topic.user = request.user
        topic.save()
        topic_form.save_m2m()
        
        # Entry oluştur
        entry = entry_form.save(commit=False)
        entry.topic = topic
        entry.user = request.user
        entry.save()
        
        return redirect('topic_detail', slug=topic.slug)
        
    except Exception as e:
        return redirect('home')

@login_required
def add_entry(request, slug):
    if request.method != 'POST':
        return redirect('topic_detail', slug=slug)
        
    topic = get_object_or_404(Topic, slug=slug)
    entry_form = EntryForm(request.POST)
    
    if not entry_form.is_valid():
        return redirect('topic_detail', slug=slug)
    
    try:
        entry = entry_form.save(commit=False)
        entry.topic = topic
        entry.user = request.user
        entry.save()
        
        # Topic güncelle
        topic.save()
        
        return redirect('topic_detail', slug=topic.slug)
        
    except Exception as e:
        return redirect('topic_detail', slug=topic.slug)

def topic_detail(request, slug):
    topic = get_object_or_404(Topic.objects.with_related(), slug=slug)
    entries = Entry.objects.with_related().filter(topic=topic).order_by('created_at')
    
    # Sayfalama
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    entry_form = EntryForm()
    
    # Kullanıcı topic'i düzenleyebilir mi kontrol et
    can_edit_topic = topic.can_be_edited_by(request.user)
    
    return render(request, 'main/topic_detail.html', {
        'topic': topic,
        'entries': page_obj,
        'entry_form': entry_form,
        'can_edit_topic': can_edit_topic,
    })

@login_required
def like_entry(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(Entry, id=entry_id)
        
        if request.user in entry.likes.all():
            entry.likes.remove(request.user)
            liked = False
        else:
            entry.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'like_count': entry.like_count()
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def load_more_topics(request):
    offset = int(request.GET.get('offset', 0))
    limit = 10
    
    topics = Topic.objects.with_related()[offset:offset+limit]
    
    topics_data = []
    for topic in topics:
        topics_data.append({
            'id': topic.id,
            'title': topic.title,
            'slug': topic.slug,
            'user': getattr(topic.user, 'username', 'Anonim'),
            'created_at': topic.created_at.strftime('%d.%m.%Y %H:%M'),
            'entry_count': topic.entry_count(),
        })
    
    return JsonResponse({
        'topics': topics_data,
        'has_more': len(topics) == limit
    })

@login_required
def agenda(request):
    # En çok entry'si olan başlıkları getir (gündem)
    topics = Topic.objects.annotate(
        entry_count=models.Count('entries')
    ).filter(entry_count__gt=0).order_by('-entry_count', '-updated_at')[:20]
    
    return render(request, 'main/agenda.html', {
        'topics': topics,
        'user': request.user
    })

@login_required
@csrf_protect
def edit_topic(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    if not topic.can_be_edited_by(request.user):
        return redirect('topic_detail', slug=topic.slug)
    
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return redirect('topic_detail', slug=topic.slug)
    else:
        form = TopicForm(instance=topic)
    
    return render(request, 'main/edit_topic.html', {'form': form, 'topic': topic})

@login_required
@csrf_protect
def delete_topic(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    if not topic.can_be_deleted_by(request.user):
        return redirect('topic_detail', slug=topic.slug)
    
    if request.method == 'POST':
        topic.delete()
        return redirect('home')
    
    return render(request, 'main/confirm_delete_topic.html', {'topic': topic})

@login_required
@csrf_protect
def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    if not entry.can_be_edited_by(request.user):
        return redirect('topic_detail', slug=entry.topic.slug)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('topic_detail', slug=entry.topic.slug)
    else:
        form = EntryForm(instance=entry)
    
    return render(request, 'main/edit_entry.html', {'form': form, 'entry': entry})

@login_required
@csrf_protect
def delete_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    if not entry.can_be_deleted_by(request.user):
        return redirect('topic_detail', slug=entry.topic.slug)
    
    if request.method == 'POST':
        topic_slug = entry.topic.slug
        entry.delete()
        return redirect('topic_detail', slug=topic_slug)
    
    return render(request, 'main/confirm_delete_entry.html', {'entry': entry})

@login_required
def vote_topic(request, slug):
    if request.method == 'POST':
        topic = get_object_or_404(Topic, slug=slug)
        vote_type = request.POST.get('vote_type')
        
        if vote_type == 'up':
            if request.user in topic.upvotes.all():
                topic.upvotes.remove(request.user)
                voted = False
            else:
                topic.upvotes.add(request.user)
                topic.downvotes.remove(request.user)
                voted = True
        elif vote_type == 'down':
            if request.user in topic.downvotes.all():
                topic.downvotes.remove(request.user)
                voted = False
            else:
                topic.downvotes.add(request.user)
                topic.upvotes.remove(request.user)
                voted = True
        else:
            return JsonResponse({'error': 'Invalid vote type'}, status=400)
        
        return JsonResponse({
            'voted': voted,
            'vote_type': vote_type,
            'upvote_count': topic.upvote_count(),
            'downvote_count': topic.downvote_count(),
            'vote_score': topic.vote_score()
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def vote_entry(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(Entry, id=entry_id)
        vote_type = request.POST.get('vote_type')
        
        if vote_type == 'up':
            if request.user in entry.upvotes.all():
                entry.upvotes.remove(request.user)
                voted = False
            else:
                entry.upvotes.add(request.user)
                entry.downvotes.remove(request.user)
                voted = True
        elif vote_type == 'down':
            if request.user in entry.downvotes.all():
                entry.downvotes.remove(request.user)
                voted = False
            else:
                entry.downvotes.add(request.user)
                entry.upvotes.remove(request.user)
                voted = True
        else:
            return JsonResponse({'error': 'Invalid vote type'}, status=400)
        
        return JsonResponse({
            'voted': voted,
            'vote_type': vote_type,
            'upvote_count': entry.upvote_count(),
            'downvote_count': entry.downvote_count(),
            'vote_score': entry.vote_score()
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_emojis(request):
    from django.http import JsonResponse
    import os
    from django.conf import settings
    
    emoji_dir = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'main/static', 'emojis')
    if not os.path.exists(emoji_dir):
        emoji_dir = os.path.join(settings.BASE_DIR, 'main/static/emojis')
    
    emojis = []
    if os.path.exists(emoji_dir):
        for filename in os.listdir(emoji_dir):
            if filename.endswith('.svg'):
                name = filename[:-4]
                emojis.append({
                    'name': name,
                    'shortcode': f':{name}:'
                })
    
    return JsonResponse(emojis, safe=False)