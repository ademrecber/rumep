
import os
import logging
from openai import OpenAI
from main.models import AIProviderConfig

logger = logging.getLogger(__name__)

def enhance_text(text):
    if not text.strip():
        logger.warning("Boş metin gönderildi.")
        raise ValueError("Metin boş olamaz.")
    try:
        config = AIProviderConfig.objects.get(is_active=True, provider='deepseek')
        if not config.api_key:
            raise ValueError("DeepSeek için API anahtarı eksik.")
        client = OpenAI(
            api_key=config.api_key,
            base_url="https://api.deepseek.com"
        )
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
   