from datetime import timedelta
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET
from .models import SportPost, Wallpaper


@require_GET
def pending_content(request):
    now = timezone.now()
    items = []
    for kind, model in [('post', SportPost), ('wallpaper', Wallpaper)]:
        for p in model.objects.filter(is_published=True, notify_users=True, published_at__lte=now,
                                     notification_requested_at__gte=now-timedelta(hours=24), notification_requested_at__lte=now).order_by('-notification_requested_at')[:20]:
            preview = reverse('spor_feed_image', args=[p.pk, 'preview']) if kind == 'post' else reverse('wallpaper_public_preview', args=[p.pk])
            items.append({'id': f'content:{kind}:{p.pk}', 'kind': 'content', 'contentType': kind, 'contentId': p.pk,
                          'title': 'Tribünde yeni paylaşım' if kind == 'post' else 'Yeni duvar kâğıdı eklendi',
                          'body': (p.description or 'Yeni paylaşımı incele.')[:300] if kind == 'post' else f'{p.title} • Yeni duvar kâğıdını incele.'[:300],
                          'imageUrl': request.build_absolute_uri(preview), 'requestedAt': p.notification_requested_at.isoformat()})
    response = JsonResponse({'items': items})
    response['Cache-Control'] = 'public, max-age=60'
    return response


@require_GET
def wallpaper_preview(request, pk):
    p = get_object_or_404(Wallpaper, pk=pk, is_published=True)
    response = HttpResponseRedirect((p.thumbnail or p.image).url)
    response['Cache-Control'] = 'no-store'
    return response


@require_GET
def wallpaper_detail(request, pk):
    p = get_object_or_404(Wallpaper, pk=pk, is_published=True)
    return JsonResponse({'id': p.pk, 'title': p.title, 'description': p.description, 'imageUrl': p.image.url,
                         'thumbnailUrl': p.thumbnail.url if p.thumbnail else p.image.url,
                         'width': p.width, 'height': p.height, 'updatedAt': p.updated_at.isoformat(),
                         'publishedAt': p.published_at.isoformat()})
