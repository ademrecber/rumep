import os
import logging
from abc import ABC, abstractmethod
from openai import OpenAI
from transformers import pipeline
from main.models import AIProviderConfig
import requests

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    @abstractmethod
    def enhance_text(self, text):
        pass

class DeepSeekProvider(AIProvider):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    def enhance_text(self, text):
        if not text.strip():
            logger.warning("Boş metin gönderildi.")
            raise ValueError("Metin boş olamaz.")
        try:
            response = self.client.chat.completions.create(
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
        except Exception as e:
            logger.error(f"DeepSeek API hatası: {str(e)}")
            raise

class HuggingFaceProvider(AIProvider):
    def __init__(self):
        self.pipeline = pipeline("text2text-generation", model="t5-small", device=-1)  # CPU-only

    def enhance_text(self, text):
        if not text.strip():
            logger.warning("Boş metin gönderildi.")
            raise ValueError("Metin boş olamaz.")
        try:
            prompt = f"Düzelt ve daha akıcı yap: {text}"
            result = self.pipeline(prompt, max_length=512, num_return_sequences=1)
            enhanced_text = result[0]['generated_text']
            logger.info("Hugging Face: Metin başarıyla geliştirildi.")
            return enhanced_text
        except Exception as e:
            logger.error(f"Hugging Face hatası: {str(e)}")
            raise

class GrokProvider(AIProvider):
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

def get_active_provider():
    try:
        config = AIProviderConfig.objects.get(is_active=True)
        if config.provider == 'deepseek':
            if not config.api_key:
                raise ValueError("DeepSeek için API anahtarı eksik.")
            return DeepSeekProvider(config.api_key)
        elif config.provider == 'huggingface':
            return HuggingFaceProvider()
        elif config.provider == 'grok':
            if not config.api_key:
                raise ValueError("Grok için API anahtarı eksik.")
            return GrokProvider(config.api_key)
        else:
            raise ValueError(f"Geçersiz sağlayıcı: {config.provider}")
    except AIProviderConfig.DoesNotExist:
        logger.error("Aktif AI sağlayıcısı bulunamadı.")
        raise ValueError("Aktif AI sağlayıcısı tanımlı değil.")
    except Exception as e:
        logger.error(f"Sağlayıcı yüklenirken hata: {str(e)}")
        raise

def enhance_text(text):
    provider = get_active_provider()
    return provider.enhance_text(text)
