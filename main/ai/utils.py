import os
import logging
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APITimeoutError, BadRequestError
from main.models import AIProviderConfig

logger = logging.getLogger(__name__)

def enhance_text(text):
    if not text.strip():
        logger.warning("Boş metin gönderildi.")
        raise ValueError("Metin boş olamaz. Lütfen geçerli bir metin sağlayın.")
    try:
        config = AIProviderConfig.objects.get(is_active=True, provider='deepseek')
    except AIProviderConfig.DoesNotExist:
        logger.error("Aktif DeepSeek sağlayıcısı bulunamadı. Lütfen veritabanınızda bir yapılandırma olduğundan emin olun.")
        raise ValueError("Aktif DeepSeek sağlayıcısı tanımlı değil.")
    except Exception as e: # Veritabanından gelebilecek diğer hataları yakala (örn: MultipleObjectsReturned)
        logger.error(f"DeepSeek sağlayıcı yapılandırması alınırken hata oluştu: {str(e)}")
        raise ValueError("DeepSeek sağlayıcı yapılandırması alınırken beklenmeyen bir hata oluştu.") from e

    if not config.api_key:
        raise ValueError("DeepSeek için API anahtarı eksik.")

    client = OpenAI(
        api_key=config.api_key,
        base_url="https://api.deepseek.com",
        timeout=30.0  # API çağrısı için 30 saniye zaman aşımı ekle
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Metni düzelt, yazım hatalarını gider ve daha akıcı, güçlü bir şekilde yeniden yaz."},
                {"role": "user", "content": text}
            ],
            stream=False,
            max_tokens=1024  # Yanıtın maksimum token uzunluğunu sınırlayın
        )

        if not response.choices or not response.choices[0].message or not response.choices[0].message.content:
            logger.error("DeepSeek API'den boş veya geçersiz yanıt döndü.")
            raise ValueError("API yanıtında içerik bulunamadı.")

        enhanced_text = response.choices[0].message.content
        logger.info("DeepSeek: Metin başarıyla geliştirildi.")
        logger.debug(f"DeepSeek API tam yanıtı: {response}") # Hata ayıklama için tam yanıtı loglayın
        return enhanced_text

    except AuthenticationError as e:
        logger.error(f"DeepSeek API kimlik doğrulama hatası: {e}")
        raise ValueError("DeepSeek API kimlik doğrulama hatası. API anahtarınızı kontrol edin.") from e
    except RateLimitError as e:
        logger.warning(f"DeepSeek API hız limiti aşıldı: {e}")
        raise ValueError("DeepSeek API hız limiti aşıldı. Lütfen daha sonra tekrar deneyin.") from e
    except APITimeoutError as e:
        logger.error(f"DeepSeek API zaman aşımı hatası: {e}")
        raise ValueError("DeepSeek API zaman aşımı. Ağ bağlantınızı veya API durumunu kontrol edin.") from e
    except BadRequestError as e:
        logger.error(f"DeepSeek API geçersiz istek hatası: {e}. Detaylar: {e.response.text if hasattr(e.response, 'text') else 'Yok'}")
        raise ValueError(f"DeepSeek API geçersiz istek. Parametreleri kontrol edin: {e}") from e
    except APIError as e:
        logger.error(f"DeepSeek API genel hata: {e}")
        raise ValueError(f"DeepSeek API'den beklenmeyen bir hata oluştu: {e}") from e
    except Exception as e:
        logger.error(f"Metin geliştirme sırasında beklenmeyen bir hata oluştu: {str(e)}")
        raise
