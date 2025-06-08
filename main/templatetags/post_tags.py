from django import template
import re

register = template.Library()

@register.filter
def count_lines(text):
    """Gerçek satır sayısını hesaplar (boş satırları saymaz)"""
    lines = [line for line in text.splitlines() if line.strip()]
    return len(lines)

@register.filter
def render_emojis(value):
    """Metindeki kısa kodları (:emoji1:) <img> etiketine çevirir."""
    # Kısa kodları bulmak için regex
    pattern = r':emoji\d+:'
    def replace_shortcode(match):   
        shortcode = match.group(0)
        name = shortcode.strip(':')
        return f'<img src="/static/emojis/{name}.svg" alt="{name}" width="20">'
    return re.sub(pattern, replace_shortcode, value)