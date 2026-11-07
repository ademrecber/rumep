from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from .models import ClubNews, ClubNewsSync
from .club_news import SYNC_KEY


@require_GET
def club_news_api(request):
    rows = ClubNews.objects.filter(is_hidden=False, is_official=True, source='Amedspor', published_at__lte=timezone.now()).exclude(title='Amedspor')[:100]
    state = ClubNewsSync.objects.filter(pk=SYNC_KEY).first()
    response = JsonResponse({'items': [dict(
        id=f'rumep-news:{row.pk}', kind=row.kind, title=row.title, body=row.summary,
        source=row.source, sourceUrl=row.source_url, publishedAt=row.published_at.isoformat(),
        official=row.is_official) for row in rows],
        'updatedAt': state.last_success_at.isoformat() if state and state.last_success_at else None,
        'partial': bool(state and state.last_error),
    }, json_dumps_params={'ensure_ascii': False})
    response['Cache-Control'] = 'public, max-age=120'
    return response
