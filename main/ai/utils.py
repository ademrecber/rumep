
import os
import logging
import google.generativeai as genai
from main.models import AIProviderConfig

logger = logging.getLogger(__name__)

def enhance_text(text, task_type='general'):
    if not text.strip():
        logger.warning("Boş metin gönderildi.")
        raise ValueError("Metin boş olamaz.")
    try:
        config = AIProviderConfig.objects.get(is_active=True, provider='gemini')
        if not config.api_key:
            raise ValueError("Gemini için API anahtarı eksik.")
        genai.configure(api_key=config.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Görev tipine göre prompt seç
        if task_type == 'biography':
            prompt = f"""
                Aşağıdaki metni bir biyografi talebi olarak kabul et ve ilgili kişi hakkında detaylı, özgün ve kapsamlı bir biyografi hazırla. 
                Kişinin hayatı, kariyeri, başarıları, kültürel etkisi ve bilinen önemli eserleri veya olayları hakkında 300-400 kelime arasında bilgi ver. 
                Yazım hatalarını düzelt, metni akıcı ve doğal hale getir. Eğer kişi hakkında sınırlı bilgi varsa, bilinen gerçeklere dayanarak mantıklı ve yaratıcı bir şekilde tamamla, ancak uydurma bilgilerden kaçın. 
                Metin: {text}
            """
        else:  # general (postlar için)
            prompt = f"""
                Aşağıdaki metni düzelt, yazım hatalarını gider ve daha akıcı, doğal bir şekilde yeniden yaz. 
                Yeni içerik üretme, sadece mevcut metni geliştir ve anlamını koru. 
                Metin: {text}
            """
        
        response = model.generate_content(prompt)
        enhanced_text = response.text
        logger.info(f"Gemini: {task_type} için metin başarıyla geliştirildi.")
        return enhanced_text
    except AIProviderConfig.DoesNotExist:
        logger.error("Aktif Gemini sağlayıcısı bulunamadı.")
        raise ValueError("Aktif Gemini sağlayıcısı tanımlı değil.")
    except Exception as e:
        logger.error(f"Gemini API hatası: {str(e)}")
        raise
