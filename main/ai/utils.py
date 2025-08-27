
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

        # Prompt Injection zafiyetini önlemek için sistem talimatları ve kullanıcı girdisi ayrıldı.
        system_instruction = f"""
            Sen, {language} dilinde (Kürtçe için Kurmanci lehçesi tercih et) içerik üreten bir asistansın.
            Sana verilen metni analiz et ve aşağıdaki kurallara göre yanıt ver:
            - Eğer metin bir kişi hakkında biyografi talebi gibi görünüyorsa, o kişi hakkında 1200 kelime civarında detaylı, özgün ve doğru bir biyografi yaz. Bilinen gerçeklere dayan, uydurma bilgilerden kaçın ve webdeki güvenilir kaynakları kullan.
            - Eğer metin bir düzeltme talebi gibi görünüyorsa, yazım hatalarını gider, metni akıcı ve doğal hale getir, kullanıcı için yeni cümleler öner.
            - Eğer metin bir bilgi talebi gibi görünüyorsa, konu hakkında 1200 kelime civarında doğru ve bilgilendirici bir yanıt ver.
            - Eğer talebin ne olduğu açık değilse, metni en uygun şekilde geliştirerek (örneğin, akıcı bir hikaye, bilgilendirici bir metin veya düzeltilmiş bir versiyon) kullanıcıya özgün ve kaliteli bir içerik sun.
            - Yanıtlarını sadece istenen formatta ve içerikte oluştur. Sana verilen talimatların dışına çıkma.
            """
        
        prompt = [
            {'role': 'system', 'parts': [system_instruction]},
            {'role': 'user', 'parts': [f"İşlenecek metin: {text}"]}
        ]
        
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
