import requests
import os
import logging

logger = logging.getLogger(__name__)

def enhance_text(text):
    """
    Grok API'sine metni gönderir, yazım hatalarını düzeltir ve metni güçlendirir.
    """
    if not text.strip():
        logger.warning("Boş metin gönderildi.")
        raise ValueError("Metin boş olamaz.")

    api_key = os.environ.get('XAI_API_KEY')
    if not api_key:
        logger.error("XAI_API_KEY ortam değişkeni bulunamadı.")
        raise ValueError("API anahtarı eksik.")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'messages': [
            {
                'role': 'system',
                'content': 'Metni düzelt, yazım hatalarını gider ve daha akıcı, güçlü bir şekilde yeniden yaz.'
            },
            {
                'role': 'user',
                'content': text
            }
        ],
        'model': 'grok-3-latest',
        'stream': False,
        'temperature': 0.7
    }

    try:
        response = requests.post('https://api.x.ai/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        enhanced_text = response.json()['choices'][0]['message']['content']
        logger.info("Metin başarıyla geliştirildi.")
        return enhanced_text
    except requests.RequestException as e:
        logger.error(f"Grok API hatası: {str(e)}")
        raise