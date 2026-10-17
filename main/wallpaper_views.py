from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
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
