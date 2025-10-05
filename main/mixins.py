from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

class KurdishTextValidationMixin:
    """Kürtçe metin validasyonu için mixin"""
    
    def validate_kurdish_text(self, field_name, value):
        if not value or not value.strip():
            raise ValidationError({field_name: _('Bu alan zorunludur.')})
        
        if not re.match(r'^[a-zçêîşû\s]+$', value.lower()):
            raise ValidationError({
                field_name: _('Bu alan sadece Kürtçe harfleri içerebilir (a-z, ç, ê, î, ş, û ve boşluk).')
            })

class ContributionMixin:
    """Katkı puanı için mixin"""
    
    def add_contribution_points(self, user, content_type, content_id, points):
        from django.conf import settings
        from .models import Katki
        
        try:
            Katki.objects.create(
                user=user,
                tur=content_type,
                icerik_id=content_id,
                puan=points
            )
            if hasattr(user, 'profile'):
                user.profile.katki_puani += points
                user.profile.save()
        except Exception:
            pass  # Sessizce geç, kritik değil

class SafeDeleteMixin:
    """Güvenli silme için mixin"""
    
    def safe_delete(self, user):
        """Sadece yetkili kullanıcılar silebilir"""
        if hasattr(self, 'kullanici') and self.kullanici == user:
            return True
        if hasattr(user, 'profile') and user.profile.is_moderator():
            return True
        return False