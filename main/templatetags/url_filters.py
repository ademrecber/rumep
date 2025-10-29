from django import template

register = template.Library()

@register.filter
def url_safe(value):
    """Boşlukları tire ile değiştir"""
    if value:
        return str(value).replace(' ', '-')
    return value