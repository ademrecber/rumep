from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return [
            '/',
            '/sozluk/',
            '/kisi/liste/',
            '/atasozu-deyim/',
            '/yer-adlari/',
            '/popular/',
        ]

    def location(self, item):
        return item

# Sitemap sözlüğü
sitemaps = {
    'static': StaticViewSitemap,
}