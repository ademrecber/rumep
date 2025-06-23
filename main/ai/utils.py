
import os
import logging
import google.generativeai as genai
from main.models import AIProviderConfig

logger = logging.getLogger(__name__)

def enhance_text(text, task_type='general', language='tr'):
    if not text.strip():
        logger.warning("Boş metin gönderildi.")
        raise ValueError("Metin boş olamaz.")
    try:
        config = AIProviderConfig.objects.get(is_active=True, provider='gemini')
        if not config.api_key:
            raise ValueError("Gemini için API anahtarı eksik.")
        genai.configure(api_key=config.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Görev tipine ve dile göre prompt seç
        if task_type == 'biography':
            prompt = f"""
                Aşağıdaki metni bir biyografi talebi olarak kabul et ve ilgili kişi hakkında detaylı, özgün ve kapsamlı bir biyografi hazırla.
                Biyografi, {language} dilinde (Kürtçe için Kurmanci lehçesi tercih et) yazılmalı.
                Kişinin hayatı, kariyeri, başarıları, kültürel etkisi ve bilinen önemli eserleri veya olayları hakkında 2 bin kelime arasında bilgi ver.
                Yazım hatalarını düzelt, metni akıcı ve doğal hale getir. Bilinen gerçeklere dayan, uydurma bilgilerden kaçın.
                Metin: {text}
            """
        elif task_type == 'info':
            prompt = f"""
                Aşağıdaki metni bir bilgi talebi olarak kabul et ve ilgili konuda {language} dilinde (Kürtçe için Kurmanci lehçesi tercih et) detaylı, doğru ve bilgilendirici bir yanıt üret.
                Konuyla ilgili 2 bin kelime arasında özgün bilgi ver, yazım hatalarını düzelt ve akıcı bir metin hazırla.
                Metin: {text}
            """
        else:  # general (postlar için)
            prompt = f"""
                Aşağıdaki metni {language} dilinde düzelt, yazım hatalarını gider ve daha akıcı, doğal bir şekilde yeniden yaz.
                Yeni içerik üretme, sadece mevcut metni geliştir ve anlamını koru.
                Metin: {text}
            """
        
        response = model.generate_content(prompt)
        enhanced_text = response.text
        logger.info(f"Gemini: {task_type} için {language} dilinde metin başarıyla geliştirildi.")
        return enhanced_text
    except AIProviderConfig.DoesNotExist:
        logger.error("Aktif Gemini sağlayıcısı bulunamadı.")
        raise ValueError("Aktif Gemini sağlayıcısı tanımlı değil.")
    except Exception as e:
        logger.error(f"Gemini API hatası: {str(e)}")
        raise
