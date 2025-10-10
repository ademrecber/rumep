from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.conf import settings
import os

def ads_txt_view(request):
    ads_txt_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'ads.txt')
    with open(ads_txt_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/plain')

def robots_txt_view(request):
    robots_txt_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'robots.txt')
    try:
        with open(robots_txt_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        # Fallback robots.txt content
        content = """User-agent: *
Allow: /

# Sitemap
Sitemap: https://rumep.net/sitemap.xml

# Disallow admin and private areas
Disallow: /admin/
Disallow: /login/
Disallow: /logout/
Disallow: /profile/edit/
Disallow: /api/

# Allow important pages
Allow: /sozluk/
Allow: /kisi/
Allow: /sarki/
Allow: /atasozu-deyim/
Allow: /yer-adlari/
Allow: /popular/

# Crawl delay
Crawl-delay: 1"""
        return HttpResponse(content, content_type='text/plain')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ads.txt', ads_txt_view, name='ads_txt'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('', include('main.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('logout/', LogoutView.as_view(), name='logout'),
]