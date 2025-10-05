from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter
def translate_category(category_name):
    """Kategori isimlerini çevirir"""
    translations = {
        'Spor': _('Spor'),
        'Teknoloji': _('Teknoloji'),
        'Müzik': _('Müzik'),
        'Siyaset': _('Siyaset'),
        'Sanat': _('Sanat'),
        'Bilim': _('Bilim'),
        'Eğitim': _('Eğitim'),
        'Sağlık': _('Sağlık'),
        'Ekonomi': _('Ekonomi'),
        'Kültür': _('Kültür'),
        'Tarih': _('Tarih'),
        'Edebiyat': _('Edebiyat'),
        'Sinema': _('Sinema'),
        'Oyun': _('Oyun'),
        'Yemek': _('Yemek'),
        'Seyahat': _('Seyahat'),
        'Moda': _('Moda'),
        'Doğa': _('Doğa'),
        'Felsefe': _('Felsefe'),
        'Din': _('Din'),
    }
    return translations.get(category_name, category_name)