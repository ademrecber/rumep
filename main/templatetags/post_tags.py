from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
import re

register = template.Library()

@register.filter
def count_lines(text):
    """Gerçek satır sayısını hesaplar (boş satırları saymaz)"""
    lines = [line for line in text.splitlines() if line.strip()]
    return len(lines)

@register.filter
def process_mentions(text):
    """Process @username mentions and convert them to links"""
    from main.models import Profile
    
    def replace_mention(match):
        username = match.group(1)
        try:
            profile = Profile.objects.get(username=username)
            profile_url = reverse('profile_detail', args=[username])
            return f'<a href="{profile_url}" class="mention-link">@{username}</a>'
        except Profile.DoesNotExist:
            return f'@{username}'
    
    # Find @username patterns
    mention_pattern = r'@([a-zA-Z0-9_]+)'
    processed_text = re.sub(mention_pattern, replace_mention, text)
    
    return mark_safe(processed_text)

@register.filter
def process_auto_links(text):
    """Process auto-links for dictionary words automatically"""
    from main.models import Sozluk, Kisi, YerAdi
    
    def replace_word(match):
        word = match.group(0)
        try:
            # Sözlükte var mı kontrol et
            sozluk = Sozluk.objects.filter(kelime__iexact=word).first()
            if sozluk:
                url = f'/sozluk/kelime/{sozluk.id}/'
                return f'<a href="{url}" class="auto-link dictionary-link">{word}</a>'
            
            # Kişi var mı kontrol et
            kisi = Kisi.objects.filter(ad__iexact=word).first()
            if kisi:
                url = f'/kisi/detay/{kisi.id}/'
                return f'<a href="{url}" class="auto-link person-link">{word}</a>'
            
            # Yer adı var mı kontrol et
            yer = YerAdi.objects.filter(ad__iexact=word).first()
            if yer:
                url = f'/yer-adi/{yer.id}/'
                return f'<a href="{url}" class="auto-link place-link">{word}</a>'
            
            return word
        except:
            return word
    
    # Sadece Türkçe/Kürtçe kelimeler için (2+ karakter)
    # Mention ve hashtag'leri etkilememek için @ ve # ile başlamayanlar
    word_pattern = r'\b(?![#@])([a-zA-ZçğıöşüÇğıöşüêîûÊÎÛ]{2,})\b'
    text = re.sub(word_pattern, replace_word, text, flags=re.IGNORECASE)
    
    return mark_safe(text)

@register.filter
def process_hashtags(text):
    """Process #hashtag and convert them to links"""
    from main.models import Hashtag
    
    def replace_hashtag(match):
        hashtag_name = match.group(1).lower()
        try:
            hashtag = Hashtag.objects.get(name__iexact=hashtag_name)
            url = reverse('hashtag_detail', args=[hashtag.slug])
            return f'<a href="{url}" class="hashtag-link">#{hashtag.name}</a>'
        except Hashtag.DoesNotExist:
            return f'<span class="hashtag-inactive">#{hashtag_name}</span>'
    
    # Find #hashtag patterns
    hashtag_pattern = r'#([a-zA-Z0-9_\u00C0-\u017F]+)'
    processed_text = re.sub(hashtag_pattern, replace_hashtag, text)
    
    return mark_safe(processed_text)

@register.filter(needs_autoescape=True)
def render_emojis(value, autoescape=True):
    """Metindeki kısa kodları (:emoji1:) <img> etiketine çevirir."""
    # First process mentions
    value = process_mentions(value)
    
    # Then process hashtags
    value = process_hashtags(value)
    
    # Then process auto-links
    value = process_auto_links(value)
    
    # Finally process emojis
    pattern = r':emoji\d+:'
    def replace_shortcode(match):   
        shortcode = match.group(0)
        name = shortcode.strip(':')
        return f'<img src="/static/emojis/{name}.svg" alt="{name}" width="20">'
    value = re.sub(pattern, replace_shortcode, value)
    
    return mark_safe(value)

@register.filter
def with_entry_font(content, entry):
    """Apply entry font to content"""
    if entry and hasattr(entry, 'font_family') and entry.font_family:
        return mark_safe(f'<span style="font-family: {entry.font_family};">{content}</span>')
    return content

@register.filter
def truncate_by_lines(text, max_lines=5):
    """Truncate text after certain number of lines"""
    lines = text.split('\n')
    if len(lines) > max_lines:
        truncated = '\n'.join(lines[:max_lines])
        return truncated + '\n[TRUNCATED]'
    return text