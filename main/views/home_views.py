
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from ..models import Post, Katki, Profile, Sarki, Kisi, Sozluk, Atasozu, Deyim, Topic, Entry, Category
from ..forms import PostForm, TopicForm, EntryForm
from .base import profile_required
import bleach
from django.db import models
import logging
from ..utils.embed_utils import generate_embed_code
from ..utils.shortener import create_short_link
from django.utils import timezone
from datetime import timedelta
# from ..ai.utils import process_request  # Geçici olarak kapatıldı

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Bu fonksiyon artık topic_views.py'de
# Burada sadece eski sistemi koruyoruz
@login_required
@profile_required
@csrf_protect
def home_old(request):
    request.session['return_page'] = 'home'
    sekme = request.GET.get('sekme', 'ana_sayfa')
    form = PostForm()
    
    if request.method == 'POST' and sekme == 'ana_sayfa':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.text = bleach.clean(post.text, tags=['p', 'br', 'img'], attributes={'img': ['src', 'alt']}, strip=False)
            post.embed_code = generate_embed_code(post.link)
            logger.debug(f"Post için embed kodu: {post.embed_code}")
            long_url = post.link
            post.link = None
            post.save()
            create_short_link(post, long_url)
            return redirect('home')
    
    posts = Post.objects.all().annotate(
        critique_count=models.Count('critiques')
    ).order_by('-created_at')[:10] if sekme == 'ana_sayfa' else []
    
    return render(request, 'main/tabs.html', {
        'posts': posts,
        'form': form,
        'user': request.user,
        'sekme': sekme
    })


