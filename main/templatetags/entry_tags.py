from django import template
import re
from urllib.parse import urlparse

register = template.Library()

@register.filter
def extract_links(content):
    """Entry içindeki [link]url[/link] taglarını bulur ve listeler"""
    if not content:
        return []
    
    link_pattern = r'\[link\](.*?)\[/link\]'
    links = re.findall(link_pattern, content)
    return links

@register.filter
def remove_link_tags(content):
    """Entry içindeki [link] taglarını kaldırır"""
    if not content:
        return content
    
    link_pattern = r'\[link\](.*?)\[/link\]'
    cleaned_content = re.sub(link_pattern, '', content)
    return cleaned_content.strip()

@register.filter
def render_custom_emojis(content):
    """Custom emoji karakterlerini span ile sarmalır"""
    if not content:
        return content
    
    # Unicode range E000-E009 for custom emojis
    emoji_chars = [chr(i) for i in range(0xE000, 0xE00A)]
    
    for emoji_char in emoji_chars:
        if emoji_char in content:
            content = content.replace(
                emoji_char, 
                f'<span class="custom-emoji">{emoji_char}</span>'
            )
    
    return content

@register.filter
def extract_domain(url):
    """URL'den domain adını çıkarır"""
    if not url:
        return url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain if domain else url
    except:
        return url