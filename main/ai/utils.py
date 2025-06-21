import os
import logging
from openai import OpenAI
from main.models import AIProviderConfig
# import requests  # Grok için gerekli, şu an yorumda

logger = logging.getLogger(__name__)

def enhance_text(text):
    if not text.strip():
        logger.warning("Boş metin gönderildi.")
        raise ValueError("Metin boş olamaz.")
    try:
        config = AIProviderConfig.objects.get(is_active=True, provider='deepseek')
        if not config.api_key:
            raise ValueError("DeepSeek için API anahtarı eksik.")
        client = OpenAI(api_key=config.api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Metni düzelt, yazım hatalarını gider ve daha akıcı, güçlü bir şekilde yeniden yaz."},
                {"role": "user", "content": text}
            ],
            stream=False
        )
        enhanced_text = response.choices[0].message.content
        logger.info("DeepSeek: Metin başarıyla geliştirildi.")
        return enhanced_text
    except AIProviderConfig.DoesNotExist:
        logger.error("Aktif DeepSeek sağlayıcısı bulunamadı.")
        raise ValueError("Aktif DeepSeek sağlayıcısı tanımlı değil.")
    except Exception as e:
        logger.error(f"DeepSeek API hatası: {str(e)}")
        raise

"""
# GrokProvider sınıfı (gelecekte kullanılmak üzere yorumda)
class GrokProvider:
    def __init__(self, api_key):
        self.api_key = api_key

    def enhance_text(self, text):
        if not text.strip():
            logger.warning("Boş metin gönderildi.")
            raise ValueError("Metin boş olamaz.")
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'messages': [
                {'role': 'system', 'content': 'Metni düzelt, yazım hatalarını gider ve daha akıcı, güçlü bir şekilde yeniden yaz.'},
                {'role': 'user', 'content': text}
            ],
            'model': 'grok-3-latest',
            'stream': False,
            'temperature': 0.7
        }
        try:
            response = requests.post('https://api.x.ai/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            enhanced_text = response.json()['choices'][0]['message']['content']
            logger.info("Grok: Metin başarıyla geliştirildi.")
            return enhanced_text
        except requests.RequestException as e:
            logger.error(f"Grok API hatası: {str(e)}")
            raise
"""
