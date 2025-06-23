
import os
import logging
import google.generativeai as genai
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
        genai.configure(api_key=config.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
            Aşağıdaki metni bir biyografi talebi olarak kabul et ve ilgili kişi hakkında detaylı, akıcı ve doğru bir biyografi hazırla. 
            Yazım hatalarını düzelt, metni akıcı hale getir ve 200-300 kelime arasında kapsamlı bir biyografi üret. 
            Metin: {text}
        """
        response = model.generate_content(prompt)
        enhanced_text = response.text
        logger.info("Gemini: Biyografi başarıyla üretildi.")
        return enhanced_text
    except AIProviderConfig.DoesNotExist:
        logger.error("Aktif Gemini sağlayıcısı bulunamadı.")
        raise ValueError("Aktif Gemini sağlayıcısı tanımlı değil.")
    except Exception as e:
        logger.error(f"Gemini API hatası: {str(e)}")
        raise
