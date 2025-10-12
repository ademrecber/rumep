from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.conf import settings
# Sitemap imports removed - using static file approach
import os

def ads_txt_view(request):
    ads_txt_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'ads.txt')
    try:
        with open(ads_txt_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        # Fallback ads.txt content
        content = "google.com, pub-4275159020382475, DIRECT, f08c47fec0942fa0"
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

def sitemap_xml_view(request):
    sitemap_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'sitemap.xml')
    try:
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/xml')
    except FileNotFoundError:
        # Fallback sitemap.xml content
        content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://rumep.net/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://rumep.net/sozluk/</loc>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
</urlset>'''
        return HttpResponse(content, content_type='application/xml')

def block_malicious_requests(request):
    return HttpResponse('Not Found', status=404)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('ads.txt', ads_txt_view, name='ads_txt'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('sitemap.xml', sitemap_xml_view, name='sitemap_xml'),
    # Block common attack vectors
    path('xmlrpc.php', block_malicious_requests),
    path('wp-admin/', block_malicious_requests),
    path('wp-login.php', block_malicious_requests),
    path('wp-config.php', block_malicious_requests),
    path('', include('main.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('logout/', LogoutView.as_view(), name='logout'),
]