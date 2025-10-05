from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from ..models import Hashtag, HashtagUsage, Entry

def hashtag_detail(request, slug):
    hashtag = get_object_or_404(Hashtag, slug=slug)
    
    # Hashtag'i kullanan entry'leri getir
    hashtag_usages = HashtagUsage.objects.filter(hashtag=hashtag).select_related(
        'entry__user__profile', 'entry__topic'
    ).order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(hashtag_usages, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'hashtag': hashtag,
        'hashtag_usages': page_obj,
        'total_usage': hashtag.usage_count
    }
    
    return render(request, 'main/hashtag_detail.html', context)

def trending_hashtags(request):
    # En popüler hashtag'ler
    trending = Hashtag.objects.filter(usage_count__gt=0)[:20]
    
    # Son kullanılan hashtag'ler
    recent = Hashtag.objects.order_by('-created_at')[:20]
    
    context = {
        'trending_hashtags': trending,
        'recent_hashtags': recent
    }
    
    return render(request, 'main/trending_hashtags.html', context)