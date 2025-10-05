from django.shortcuts import render
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from ..models import Topic, Entry, Profile, Hashtag, Sozluk, Atasozu, Deyim, Kisi, Sarki, YerAdi
from datetime import datetime, timedelta

def advanced_search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')  # all, topics, entries, users, hashtags
    date_filter = request.GET.get('date', 'all')  # all, today, week, month, year
    user_filter = request.GET.get('user', '').strip()
    
    results = {
        'topics': [],
        'entries': [],
        'users': [],
        'hashtags': [],
        'query': query,
        'search_type': search_type,
        'date_filter': date_filter,
        'user_filter': user_filter,
        'total_count': 0
    }
    
    if not query:
        return render(request, 'main/advanced_search.html', results)
    
    # Date filtering
    date_from = None
    if date_filter == 'today':
        date_from = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_filter == 'week':
        date_from = datetime.now() - timedelta(days=7)
    elif date_filter == 'month':
        date_from = datetime.now() - timedelta(days=30)
    elif date_filter == 'year':
        date_from = datetime.now() - timedelta(days=365)
    
    # Search in topics
    if search_type in ['all', 'topics']:
        topic_query = Q(title__icontains=query)
        if date_from:
            topic_query &= Q(created_at__gte=date_from)
        if user_filter:
            topic_query &= Q(user__profile__username__icontains=user_filter)
        
        topics = Topic.objects.filter(topic_query).select_related('user__profile').annotate(
            entry_count=Count('entries')
        ).order_by('-updated_at')[:20]
        results['topics'] = topics
    
    # Search in entries
    if search_type in ['all', 'entries']:
        entry_query = Q(content__icontains=query)
        if date_from:
            entry_query &= Q(created_at__gte=date_from)
        if user_filter:
            entry_query &= Q(user__profile__username__icontains=user_filter)
        
        entries = Entry.objects.filter(entry_query).select_related(
            'user__profile', 'topic'
        ).order_by('-created_at')[:20]
        results['entries'] = entries
    
    # Search in users
    if search_type in ['all', 'users']:
        user_query = Q(nickname__icontains=query) | Q(username__icontains=query)
        users = Profile.objects.filter(user_query).select_related('user')[:10]
        results['users'] = users
    
    # Search in hashtags
    if search_type in ['all', 'hashtags']:
        hashtag_query = Q(name__icontains=query)
        hashtags = Hashtag.objects.filter(hashtag_query).order_by('-usage_count')[:10]
        results['hashtags'] = hashtags
    
    # Calculate total count
    results['total_count'] = (
        len(results['topics']) + 
        len(results['entries']) + 
        len(results['users']) + 
        len(results['hashtags'])
    )
    
    return render(request, 'main/advanced_search.html', results)

def search_suggestions(request):
    """AJAX endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = []
    
    # Topic suggestions
    topics = Topic.objects.filter(title__icontains=query)[:5]
    for topic in topics:
        suggestions.append({
            'type': 'topic',
            'text': topic.title,
            'url': f'/topic/{topic.slug}/',
            'icon': 'bi-chat-square-text'
        })
    
    # User suggestions
    users = Profile.objects.filter(
        Q(nickname__icontains=query) | Q(username__icontains=query)
    )[:5]
    for user in users:
        suggestions.append({
            'type': 'user',
            'text': f'{user.nickname} (@{user.username})',
            'url': f'/profile/{user.username}/',
            'icon': 'bi-person'
        })
    
    # Hashtag suggestions
    hashtags = Hashtag.objects.filter(name__icontains=query)[:5]
    for hashtag in hashtags:
        suggestions.append({
            'type': 'hashtag',
            'text': f'#{hashtag.name}',
            'url': f'/hashtag/{hashtag.slug}/',
            'icon': 'bi-hash'
        })
    
    return JsonResponse({'suggestions': suggestions[:10]})

def quick_search(request):
    """Quick search for navbar"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'main/search_results.html', {
            'query': query,
            'results': [],
            'total_count': 0
        })
    
    # Combined search
    results = []
    
    # Check if query is a code (9 digits with or without #)
    code_query = query.replace('#', '').strip()
    if code_query.isdigit() and len(code_query) == 9:
        # Search topic by code
        try:
            topic = Topic.objects.get(code=code_query)
            results.append({
                'type': 'topic',
                'title': topic.title,
                'subtitle': f'{topic.user.profile.nickname} • {topic.entry_count()} entry • Kod: #{topic.code}',
                'url': f'/topic/{topic.slug}/',
                'date': topic.created_at
            })
        except Topic.DoesNotExist:
            pass
        
        # Search entry by code
        try:
            entry = Entry.objects.get(code=code_query)
            results.append({
                'type': 'entry',
                'title': entry.topic.title,
                'subtitle': f'{entry.user.profile.nickname} • {entry.content[:100]}... • Kod: #{entry.code}',
                'url': f'/topic/{entry.topic.slug}/#entry-{entry.id}',
                'date': entry.created_at
            })
        except Entry.DoesNotExist:
            pass
    else:
        # Regular text search
        # Search topics
        topics = Topic.objects.filter(title__icontains=query).select_related('user__profile')[:10]
        for topic in topics:
            results.append({
                'type': 'topic',
                'title': topic.title,
                'subtitle': f'{topic.user.profile.nickname} • {topic.entry_count()} entry',
                'url': f'/topic/{topic.slug}/',
                'date': topic.created_at
            })
        
        # Search entries
        entries = Entry.objects.filter(content__icontains=query).select_related(
            'user__profile', 'topic'
        )[:10]
        for entry in entries:
            results.append({
                'type': 'entry',
                'title': entry.topic.title,
                'subtitle': f'{entry.user.profile.nickname} • {entry.content[:100]}...',
                'url': f'/topic/{entry.topic.slug}/#entry-{entry.id}',
                'date': entry.created_at
            })
    
    # Sort by date
    results.sort(key=lambda x: x['date'], reverse=True)
    
    return render(request, 'main/search_results.html', {
        'query': query,
        'results': results[:20],
        'total_count': len(results)
    })

def global_search(request):
    """Global search across all modules"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', 'all')
    
    results = {
        'query': query,
        'category': category,
        'sozluk': [],
        'kisiler': [],
        'sarkilar': [],
        'atasozu_deyim': [],
        'yer_adlari': [],
        'topics': [],
        'total_count': 0,
        'popular_searches': get_popular_searches(),
        'recent_searches': get_recent_searches(request.user) if request.user.is_authenticated else []
    }
    
    if not query or len(query) < 2:
        return render(request, 'main/global_search.html', results)
    
    # Sözlük arama
    if category in ['all', 'sozluk']:
        sozluk = Sozluk.objects.filter(
            Q(kelime__icontains=query) | Q(detay__icontains=query)
        ).select_related('kullanici__profile')[:10]
        results['sozluk'] = sozluk
    
    # Kişiler arama
    if category in ['all', 'kisiler']:
        kisiler = Kisi.objects.filter(
            Q(ad__icontains=query) | Q(biyografi__icontains=query)
        ).select_related('kullanici__profile')[:10]
        results['kisiler'] = kisiler
    
    # Şarkılar arama
    if category in ['all', 'sarkilar']:
        sarkilar = Sarki.objects.filter(
            Q(ad__icontains=query) | Q(sozler__icontains=query) | Q(album__kisi__ad__icontains=query)
        ).select_related('album__kisi', 'kullanici__profile')[:10]
        results['sarkilar'] = sarkilar
    
    # Atasözü ve Deyimler arama
    if category in ['all', 'atasozu_deyim']:
        atasozu = Atasozu.objects.filter(
            Q(kelime__icontains=query) | Q(anlami__icontains=query)
        ).select_related('kullanici__profile')[:5]
        deyim = Deyim.objects.filter(
            Q(kelime__icontains=query) | Q(anlami__icontains=query)
        ).select_related('kullanici__profile')[:5]
        results['atasozu_deyim'] = list(atasozu) + list(deyim)
    
    # Yer Adları arama
    if category in ['all', 'yer_adlari']:
        yer_adlari = YerAdi.objects.filter(
            Q(ad__icontains=query) | Q(detay__icontains=query)
        ).select_related('kullanici__profile')[:10]
        results['yer_adlari'] = yer_adlari
    
    # Topics arama
    if category in ['all', 'topics']:
        topics = Topic.objects.filter(
            Q(title__icontains=query)
        ).select_related('user__profile')[:10]
        results['topics'] = topics
    
    # Toplam sayı hesapla
    results['total_count'] = (
        len(results['sozluk']) + 
        len(results['kisiler']) + 
        len(results['sarkilar']) + 
        len(results['atasozu_deyim']) + 
        len(results['yer_adlari']) + 
        len(results['topics'])
    )
    
    # Aramayı kaydet
    if query and request.user.is_authenticated:
        save_search_history(request.user, query)
    
    # Kod araması (#123456789 formatı)
    if query.startswith('#') and len(query) == 10 and query[1:].isdigit():
        code = query[1:]
        try:
            topic = Topic.objects.get(code=code)
            results['code_result'] = {'type': 'topic', 'object': topic}
        except Topic.DoesNotExist:
            try:
                entry = Entry.objects.get(code=code)
                results['code_result'] = {'type': 'entry', 'object': entry}
            except Entry.DoesNotExist:
                pass
    
    return render(request, 'main/global_search.html', results)

def get_popular_searches():
    """En popüler aramaları getir"""
    return [
        'Kurdistan', 'Newroz', 'Diyarbakır', 'Ahmet Kaya', 'Şivan Perwer',
        'Kürt kültürü', 'Dengbej', 'Erbil', 'Süleymaniye', 'Mardin'
    ]

def get_recent_searches(user):
    """Kullanıcının son aramalarını getir"""
    # Basit implementasyon - session'da tutulabilir
    return []

def save_search_history(user, query):
    """Arama geçmişini kaydet"""
    # Basit implementasyon - daha sonra SearchHistory modeli eklenebilir
    pass