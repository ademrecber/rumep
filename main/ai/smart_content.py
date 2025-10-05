from django.conf import settings
import requests
import json

class SmartContentGenerator:
    """AI ile akıllı içerik üretimi"""
    
    def suggest_topics(self, user_interests=None):
        """Kullanıcı ilgilerine göre başlık önerileri"""
        prompts = [
            "Kürdistan tarihi hakkında güncel tartışma konuları",
            "Kürt kültürü ve sanatı üzerine ilginç başlıklar",
            "Kürtçe dil gelişimi ve modern kullanım alanları",
            "Kürt müziği ve modern sanatçılar",
            "Kürdistan coğrafyası ve doğal güzellikleri"
        ]
        return prompts[:3]  # İlk 3 öneri
    
    def auto_translate_content(self, text, target_lang='ku'):
        """İçerikleri otomatik çevir"""
        # Basit çeviri mantığı - gerçek AI servisi entegre edilebilir
        translations = {
            'tr': {
                'Merhaba': 'Silav',
                'Teşekkürler': 'Spas',
                'Güzel': 'Xweş',
                'Kitap': 'Pirtûk'
            }
        }
        return text  # Şimdilik orijinal metni döndür
    
    def generate_hashtags(self, content):
        """İçerikten otomatik hashtag üret"""
        keywords = ['kürdistan', 'kürt', 'kültür', 'tarih', 'dil', 'müzik']
        hashtags = []
        
        for keyword in keywords:
            if keyword.lower() in content.lower():
                hashtags.append(f"#{keyword}")
        
        return hashtags[:5]  # Max 5 hashtag
    
    def content_quality_score(self, content):
        """İçerik kalite puanı"""
        score = 0
        
        # Uzunluk kontrolü
        if len(content) > 100:
            score += 20
        if len(content) > 500:
            score += 20
            
        # Kürtçe karakter kontrolü
        kurdish_chars = ['ç', 'ê', 'î', 'ş', 'û']
        if any(char in content.lower() for char in kurdish_chars):
            score += 30
            
        # Link kontrolü
        if 'http' in content:
            score += 10
            
        # Emoji kontrolü
        if any(char in content for char in ['😊', '👍', '❤️']):
            score += 20
            
        return min(score, 100)