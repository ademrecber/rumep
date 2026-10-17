from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from .models import Wallpaper


def admin_wallpaper_preview(request, pk):
    if not request.user.has_perm('main.view_wallpaper'):
        raise PermissionDenied
    wallpaper = get_object_or_404(Wallpaper, pk=pk)
    if not wallpaper.thumbnail:
        raise Http404
    try:
        stream = wallpaper.thumbnail.open('rb')
    except FileNotFoundError:
        raise Http404 from None
    response = FileResponse(stream, content_type='image/png' if wallpaper.thumbnail.name.endswith('.png') else 'image/jpeg')
    response['Cache-Control'] = 'private, no-store'
    response['X-Content-Type-Options'] = 'nosniff'
    return response

def wallpaper_api(request):
    if request.method != 'GET':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except ValueError:
        return JsonResponse({'detail': 'Invalid page'}, status=400)
    order = request.GET.get('order', 'newest')
    ordering = ('published_at', 'pk') if order == 'oldest' else ('-published_at', '-pk')
    records = list(Wallpaper.objects.filter(is_published=True).order_by(*ordering)[(page-1)*10:page*10+1])
    items = []
    for item in records[:10]:
        items.append({'id': item.pk, 'title': item.title, 'description': item.description,
                      'imageUrl': item.image.url,
                      'thumbnailUrl': item.thumbnail.url if item.thumbnail else item.image.url,
                      'width': item.width, 'height': item.height, 'updatedAt': item.updated_at.isoformat(),
                      'publishedAt': item.published_at.isoformat() if item.published_at else None})
    return JsonResponse({'items': items, 'hasMore': len(records) > 10, 'page': page})
