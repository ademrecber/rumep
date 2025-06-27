
import os
import logging
import google.generativeai as genai
from main.models import AIProviderConfig

logger = logging.getLogger(__name__)

def process_request(text, language='tr'):
    if not text.strip():
        logger.warning("Boş metin gönderildi.")
        raise ValueError("Metin boş olamaz.")
    try:
        config = AIProviderConfig.objects.get(is_active=True, provider='gemini')
        if not config.api_key:
            raise ValueError("Gemini için API anahtarı eksik.")
        genai.configure(api_key=config.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Esnek prompt: Kullanıcının talebine göre yanıt üret
        prompt = f"""
            Aşağıdaki metni {language} dilinde (Kürtçe için Kurmanci lehçesi tercih et) oku ve kullanıcının talebine uygun bir şekilde yanıt ver.
            - Eğer biyografi isteniyorsa, ilgili kişi hakkında 1200 kelime arasında detaylı, özgün ve doğru bir biyografi yaz. Bilinen gerçeklere dayan, uydurma bilgilerden kaçın webdeki kaynakları kullan.
            - Eğer metin düzeltme isteniyorsa, yazım hatalarını gider, metni akıcı ve doğal hale getir, kullanıcı için yeni cümleler öner.
            - Eğer bilgi isteniyorsa, konu hakkında 1200 kelime arasında doğru ve bilgilendirici bir yanıt ver.
            - Talebin ne olduğu açık değilse, metni en uygun şekilde geliştir (örneğin, akıcı bir hikaye, bilgi veya düzeltme).
            - İnternetten araştırma yap, ve internetteki kaynaklardan detaylı ve güncel bilgiler kullan.
            - Metni geliştirirken, kullanıcıya özgün ve kaliteli bir içerik sun.
            Metin: {text}
        """
        
        response = model.generate_content(prompt)
        enhanced_text = response.text
        logger.info(f"Gemini: {language} dilinde esnek yanıt üretildi.")
        return enhanced_text
    except AIProviderConfig.DoesNotExist:
        logger.error("Aktif Gemini sağlayıcısı bulunamadı.")
        raise ValueError("Aktif Gemini sağlayıcısı tanımlı değil.")
    except Exception as e:
        logger.error(f"Gemini API hatası: {str(e)}")
        raise
