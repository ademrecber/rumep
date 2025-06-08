# utils/emojis.py
EMOJI_MAP = {
    ':smile:': '😊',
    ':star:': '⭐',
    ':heart:': '❤️',
    ':cool:': '😎',
    ':fire:': '🔥',
}

def get_emojis():
    """Tüm emojileri döndürür."""
    return EMOJI_MAP

def render_emoji(code):
    """Emoji kodunu HTML’e çevirir."""
    return f'<span class="emoji emoji-{code.replace(":", "")}">{EMOJI_MAP.get(code, code)}</span>'