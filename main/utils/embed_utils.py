import re
import logging
import requests
from urllib.parse import urlparse

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_embed_code(url):
    """URL’den embed kodu oluşturur."""
    if not url:
        logger.debug("URL boş, embed kodu oluşturulmadı")
        return ''
    
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc.lower()
        logger.debug(f"URL işleniyor: {url}, hostname: {hostname}")

        # Twitter/X için istemci tarafında embed
        if 'twitter.com' in hostname or 'x.com' in hostname:
            logger.debug(f"Twitter/X için istemci tarafı embed: {url}")
            return f'<blockquote class="twitter-tweet"><img src="/static/logos/x.svg" alt="X Logo" style="width: 24px; height: 24px; margin-right: 5px;"><a href="{url}"></a></blockquote>'

        # Instagram için istemci tarafında embed
        elif 'instagram.com' in hostname:
            logger.debug(f"Instagram için istemci tarafı embed: {url}")
            return f'<blockquote class="instagram-media" data-instgrm-permalink="{url}" data-instgrm-version="14"><img src="/static/logos/instagram.svg" alt="Instagram Logo" style="width: 24px; height: 24px; margin-right: 5px;"></blockquote>'
        
        # Telegram için istemci tarafında embed
        elif 't.me' in hostname or 'telegram.me' in hostname:
            logger.debug(f"Telegram için istemci tarafı embed: {url}")
            return f'<blockquote class="telegram-media"><img src="/static/logos/telegram.svg" alt="Telegram Logo" style="width: 24px; height: 24px; margin-right: 5px;"><a href="{url}"></a></blockquote>'
        
        # Facebook için istemci tarafında embed
        elif 'facebook.com' in hostname:
            logger.debug(f"Facebook için istemci tarafı embed: {url}")
            return f'<blockquote class="facebook-media"><img src="/static/logos/facebook.svg" alt="Facebook Logo" style="width: 24px; height: 24px; margin-right: 5px;"><a href="{url}"></a></blockquote>'
        
        # YouTube için özel embed
        elif 'youtube.com' in hostname or 'youtu.be' in hostname:
            logger.debug(f"YouTube URL’si: {url}")
            video_id = None
            if 'youtube.com' in hostname:
                match = re.search(r'(?:v=|\/videos\/|embed\/|youtu.be\/|\/v\/|\/e\/|watch\?v=|&v=)([^#\&\?]+)', url)
                if match:
                    video_id = match.group(1)
            elif 'youtu.be' in hostname:
                match = re.search(r'youtu\.be\/([^?]+)', url)
                if match:
                    video_id = match.group(1)
            if video_id:
                embed_code = f'<iframe src="https://www.youtube.com/embed/{video_id}" width="100%" height="315" frameborder="0" allowfullscreen></iframe>'
                logger.debug(f"YouTube embed kodu oluşturuldu: {embed_code}")
                return embed_code
            else:
                logger.error(f"YouTube video ID’si çıkarılamadı: {url}")
                return f'<a href="{url}" target="_blank">{url}</a>'
        
        # Diğer siteler için iframe denemesi
        else:
            logger.debug(f"Genel web sayfası için iframe denemesi: {url}")
            try:
                response = requests.head(url, allow_redirects=True, timeout=5)
                x_frame_options = response.headers.get('X-Frame-Options', '').lower()
                if x_frame_options in ['deny', 'sameorigin']:
                    logger.debug(f"Iframe engellendi, X-Frame-Options: {x_frame_options}")
                    return f'<a href="{url}" target="_blank">{url}</a>'
                embed_code = f'<iframe src="{url}" width="100%" height="500" frameborder="0"></iframe>'
                logger.debug(f"Genel iframe oluşturuldu: {embed_code}")
                return embed_code
            except requests.RequestException as e:
                logger.error(f"Iframe oluşturulamadı: {e}")
                return f'<a href="{url}" target="_blank">{url}</a>'

    except Exception as e:
        logger.error(f"Embed kodu oluşturulurken genel hata: {str(e)}")
        return f'<a href="{url}" target="_blank">{url}</a>'