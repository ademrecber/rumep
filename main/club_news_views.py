from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from .models import ClubNews, ClubNewsSync


@require_GET
def club_news_api(request):
    rows = ClubNews.objects.filter(is_hidden=False, published_at__lte=timezone.now())[:100]
    state = ClubNewsSync.objects.filter(pk='public-news').first()
    response = JsonResponse({'items': [dict(
        id=f'rumep-news:{row.pk}', kind=row.kind, title=row.title, body=row.summary,
        source=row.source, sourceUrl=row.source_url, publishedAt=row.published_at.isoformat(),
        official=row.is_official) for row in rows],
        'updatedAt': state.last_success_at.isoformat() if state and state.last_success_at else None,
        'partial': bool(state and state.last_error),
    }, json_dumps_params={'ensure_ascii': False})
    response['Cache-Control'] = 'public, max-age=120'
    return response
