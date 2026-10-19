from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
import os
from main.wallpaper_views import admin_wallpaper_preview, wallpaper_api
from main.feed_views import feed_api, feed_image

def ads_txt_view(request):
    ads_txt_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'ads.txt')
    try:
        with open(ads_txt_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        return HttpResponse("", content_type='text/plain')

def robots_txt_view(request):
    content = """User-agent: *
Allow: /
"""
    return HttpResponse(content, content_type='text/plain')

def app_ads_txt_view(request):
    return HttpResponse('google.com, pub-8541321354650330, DIRECT, f08c47fec0942fa0\n', content_type='text/plain')

def favicon_view(request):
    favicon_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'favicon.ico')
    try:
        with open(favicon_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/x-icon')
    except FileNotFoundError:
        return HttpResponse(status=404)

urlpatterns = [
    path('api/spor-feed/', feed_api, name='spor_feed_api'),
    path('api/spor-feed/<int:pk>/<str:variant>/', feed_image, name='spor_feed_image'),
    path('app-ads.txt', app_ads_txt_view, name='app_ads_txt'),
    path('api/wallpapers/', wallpaper_api, name='wallpaper_api'),
    path('rumep-studyo/wallpapers/<int:pk>/preview/', admin.site.admin_view(admin_wallpaper_preview), name='wallpaper_admin_preview'),
    path('rumep-studyo/', admin.site.urls),
    path('ads.txt', ads_txt_view, name='ads_txt'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('favicon.ico', favicon_view, name='favicon'),
    path('', include('main.urls')),
]
