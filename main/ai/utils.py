
import os
import logging
from google import genai
from main.models import AIProviderConfig

logger = logging.getLogger(__name__)

def enhance_text(text):
       if not text.strip():
           logger.warning("Boş metin gönderildi.")
           raise ValueError("Metin boş olamaz.")
       try:
           config = AIProviderConfig.objects.get(is_active=True, provider='gemini')
           if not config.api_key:
               raise ValueError("Gemini için API anahtarı eksik.")
           client = genai.Client(api_key=config.api_key)
           response = client.models.generate_content(
               model="gemini-2.5-flash",
               contents=f"Düzelt ve daha akıcı yap: {text}"
           )
           enhanced_text = response.text
           logger.info("Gemini: Metin başarıyla geliştirildi.")
           return enhanced_text
       except AIProviderConfig.DoesNotExist:
           logger.error("Aktif Gemini sağlayıcısı bulunamadı.")
           raise ValueError("Aktif Gemini sağlayıcısı tanımlı değil.")
       except Exception as e:
           logger.error(f"Gemini API hatası: {str(e)}")
           raise
   