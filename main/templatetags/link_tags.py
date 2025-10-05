import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def auto_link(text):
    """Entry içindeki linkleri otomatik olarak tıklanabilir yapar"""
    
    # URL regex pattern
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    def replace_url(match):
        url = match.group(0)
        # Güvenlik için URL'yi temizle
        clean_url = url.replace('"', '&quot;').replace("'", '&#39;')
        return f'<a href="{clean_url}" target="_blank" rel="noopener noreferrer" class="entry-link">{url}</a>'
    
    # URL'leri linklerle değiştir
    linked_text = url_pattern.sub(replace_url, text)
    
    return mark_safe(linked_text)