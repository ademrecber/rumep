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
    items = []
    for item in Wallpaper.objects.filter(is_published=True):
        items.append({'id': item.pk, 'title': item.title, 'description': item.description,
                      'imageUrl': item.image.url,
                      'thumbnailUrl': item.thumbnail.url if item.thumbnail else item.image.url,
                      'width': item.width, 'height': item.height,
                      'publishedAt': item.published_at.isoformat() if item.published_at else None})
    return JsonResponse({'items': items})
