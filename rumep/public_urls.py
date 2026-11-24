"""Public routes do not import database models or the legacy admin."""
from django.http import HttpResponse, FileResponse
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings


def health(request):
    return HttpResponse('ok', content_type='text/plain')


def publisher(request):
    return HttpResponse('google.com, pub-8541321354650330, DIRECT, f08c47fec0942fa0\n', content_type='text/plain')


def robots(request):
    return HttpResponse('User-agent: *\nAllow: /\n', content_type='text/plain')


def favicon(request):
    return FileResponse((settings.BASE_DIR / 'main/static/favicon.ico').open('rb'), content_type='image/x-icon')


def ads(request):
    return FileResponse((settings.BASE_DIR / 'ads.txt').open('rb'), content_type='text/plain')


urlpatterns = [
    path('healthz/', health),
    path('app-ads.txt', publisher),
    path('ads.txt', ads),
    path('robots.txt', robots),
    path('favicon.ico', favicon),
    path('rumep-studyo/', RedirectView.as_view(url='/rumep-studyo/content/', permanent=False)),
    path('', include('main.urls')),
]
