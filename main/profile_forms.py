from django import forms
from .models import Profile
from django.utils.translation import gettext_lazy as _

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'nickname', 'biography', 'instagram_username', 'twitter_username',
            'youtube_url', 'tiktok_username', 'linkedin_url', 'github_username',
            'website_url', 'facebook_username', 'preferred_language'
        ]
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Takma adınız')}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Kendiniz hakkında...'), 'rows': 3}),
            'instagram_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Instagram kullanıcı adı')}),
            'twitter_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Twitter kullanıcı adı')}),
            'facebook_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Facebook kullanıcı adı')}),
            'tiktok_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('TikTok kullanıcı adı')}),
            'github_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('GitHub kullanıcı adı')}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('YouTube kanal linki')}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('LinkedIn profil linki')}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Kişisel website linki')}),
            'preferred_language': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_instagram_username(self):
        username = self.cleaned_data.get('instagram_username')
        if username and not username.replace('_', '').replace('.', '').isalnum():
            raise forms.ValidationError(_('Geçersiz Instagram kullanıcı adı.'))
        return username
    
    def clean_twitter_username(self):
        username = self.cleaned_data.get('twitter_username')
        if username and not username.replace('_', '').isalnum():
            raise forms.ValidationError(_('Geçersiz Twitter kullanıcı adı.'))
        return username
    
    def clean_github_username(self):
        username = self.cleaned_data.get('github_username')
        if username and not username.replace('-', '').replace('_', '').isalnum():
            raise forms.ValidationError(_('Geçersiz GitHub kullanıcı adı.'))
        return username