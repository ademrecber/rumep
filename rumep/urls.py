from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
import os

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

def favicon_view(request):
    favicon_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'favicon.ico')
    try:
        with open(favicon_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/x-icon')
    except FileNotFoundError:
        return HttpResponse(status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ads.txt', ads_txt_view, name='ads_txt'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('favicon.ico', favicon_view, name='favicon'),
    path('', include('main.urls')),
]
