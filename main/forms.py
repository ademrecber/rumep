from django import forms
from .models import Sozluk, Kisi, Album, Sarki, SarkiGrubu, Atasozu, Deyim, SozlukDetay, SarkiDetay, AtasozuDeyimDetay, KisiDetay, YerAdi, YerAdiDetay, Topic, Entry, Category, Profile
import bleach
import re
from django.utils.translation import gettext_lazy as _



def clean_form_text(text, allowed_tags=['p', 'b', 'i']):
    """Ortak metin temizleme fonksiyonu."""
    if not text.strip():
        raise forms.ValidationError(_("Bu alan boş olamaz."))
    return bleach.clean(text, tags=allowed_tags, strip=False)

class TopicForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        help_text=_('En fazla 3 kategori seçebilirsiniz.')
    )
    
    class Meta:
        model = Topic
        fields = ['title', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': _('Başlık başlığını girin...'),
                'maxlength': 200,
                'id': 'id_title'
            })
        }
    
    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if categories and len(categories) > 3:
            raise forms.ValidationError(_('En fazla 3 kategori seçebilirsiniz.'))
        return categories
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError(_('Başlık boş olamaz.'))
        title = title.strip()
        if len(title) < 1:
            raise forms.ValidationError(_('Başlık gerekli.'))
        # XSS koruması
        import bleach
        title = bleach.clean(title, tags=[], strip=True)
        return title

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['content', 'link']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control border-0 auto-grow', 
                'placeholder': _('Entry\'nizi yazın...'),
                'maxlength': 10000,
                'rows': 4,
                'id': 'id_content'
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-control mt-2',
                'placeholder': _('Bağlantı (isteğe bağlı)'),
                'id': 'id_link'
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError(_('Entry içeriği boş olamaz.'))
        content = content.strip()
        if len(content) < 1:
            raise forms.ValidationError(_('Entry içeriği gerekli.'))
        return clean_form_text(content, allowed_tags=['p', 'br', 'b', 'i', 'strong', 'em'])



class SozlukForm(forms.ModelForm):
    tur = forms.ChoiceField(
        choices=[('', _('Seçiniz')), ('isim', _('İsim')), ('fiil', _('Fiil')), ('sifat', _('Sıfat')), ('zarf', _('Zarf'))],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Sozluk
        fields = ['kelime', 'detay', 'turkce_karsiligi', 'ingilizce_karsiligi', 'tur']
        widgets = {
            'kelime': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Kelimeyi yazın'), 'required': True}),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Kelimenin detaylarını yazın'), 'rows': 4, 'required': True}),
            'turkce_karsiligi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Türkçe karşılığı (isteğe bağlı)')}),
            'ingilizce_karsiligi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('İngilizce karşılığı (isteğe bağlı)')}),
        }

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError(_('Kelime alanı zorunludur.'))
        if self.instance and self.instance.pk:
            if kelime.lower() == self.instance.kelime.lower():
                return kelime
        if Sozluk.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError(_('Bu kelime zaten sözlükte mevcut, lütfen farklı bir kelime yazın.'))
        return kelime

    def clean_turkce_karsiligi(self):
        turkce = self.cleaned_data.get('turkce_karsiligi', '')
        if turkce:
            return turkce.strip()
        return turkce

    def clean_ingilizce_karsiligi(self):
        ingilizce = self.cleaned_data.get('ingilizce_karsiligi', '')
        if ingilizce:
            return ingilizce.strip()
        return ingilizce

class SozlukDetayForm(forms.ModelForm):
    class Meta:
        model = SozlukDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Ek detayları yazın'), 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError(_('Detay alanı zorunludur.'))
        return detay

class SarkiDetayForm(forms.ModelForm):
    class Meta:
        model = SarkiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Ek detayları yazın'), 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError(_('Detay alanı zorunludur.'))
        return detay

class KisiForm(forms.ModelForm):
    class Meta:
        model = Kisi
        fields = ['ad', 'kisi_turu', 'biyografi', 'kategoriler', 'dogum_tarihi', 'olum_tarihi', 'dogum_yeri_secim', 'dogum_yeri_serbest', 'cinsiyet', 'meslek', 'aktif_yillar', 'bagli_grup', 'website', 'instagram', 'twitter', 'youtube']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Kişi/Grup adını yazın'), 'required': True}),
            'kisi_turu': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'biyografi': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Biyografiyi buraya yazın...', 'rows': 8, 'required': True}),
            'kategoriler': forms.SelectMultiple(attrs={'class': 'form-control select2', 'required': True}),
            'dogum_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': _('Doğum tarihi')}),
            'olum_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': _('Ölüm tarihi')}),
            'dogum_yeri_secim': forms.Select(attrs={'class': 'form-control'}),
            'dogum_yeri_serbest': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Veya buraya yazın...')}),
            'cinsiyet': forms.Select(attrs={'class': 'form-control'}),
            'meslek': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Meslek/Alan')}),
            'aktif_yillar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Aktif yıllar (örn: 1990-2020)')}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Website URL')}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Instagram kullanıcı adı')}),
            'twitter': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Twitter kullanıcı adı')}),
            'youtube': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('YouTube kanal URL')}),
            'bagli_grup': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece grup ve kurumları göster
        self.fields['bagli_grup'].queryset = Kisi.objects.filter(kisi_turu__in=['grup', 'kurum']).order_by('ad')

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError(_('Ad alanı zorunludur.'))
        return ad

    def clean_biyografi(self):
        biyografi = self.cleaned_data.get('biyografi')
        if not biyografi.strip():
            raise forms.ValidationError(_('Biyografi alanı zorunludur.'))
        return biyografi
    
    def clean(self):
        cleaned_data = super().clean()
        dogum_tarihi = cleaned_data.get('dogum_tarihi')
        olum_tarihi = cleaned_data.get('olum_tarihi')
        
        if olum_tarihi and dogum_tarihi and olum_tarihi < dogum_tarihi:
            raise forms.ValidationError({'olum_tarihi': _('Ölüm tarihi doğum tarihinden önce olamaz.')})
        
        # Doğum yeri validasyonu
        dogum_yeri_secim = cleaned_data.get('dogum_yeri_secim')
        dogum_yeri_serbest = cleaned_data.get('dogum_yeri_serbest')
        
        if dogum_yeri_secim and dogum_yeri_serbest:
            raise forms.ValidationError(_('Doğum yeri için hem listeden seçim hem de serbest metin kullanılamaz.'))
        
        return cleaned_data
    
class KisiDetayForm(forms.ModelForm):
    class Meta:
        model = KisiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Ek detayları yazın'), 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError(_('Detay alanı zorunludur.'))
        return bleach.clean(detay, tags=['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'], strip=True)  

class AlbumForm(forms.ModelForm):
    yil = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Albüm yılı (isteğe bağlı)')}))

    class Meta:
        model = Album
        fields = ['ad', 'yil']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Albüm adını yazın'), 'required': True}),
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError(_('Albüm adı zorunludur.'))
        return ad

class SarkiGrubuForm(forms.ModelForm):
    class Meta:
        model = SarkiGrubu
        fields = ['album', 'ad']
        widgets = {
            'album': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Şarkı adını yazın'), 'required': True}),
        }

class SarkiForm(forms.ModelForm):
    class Meta:
        model = Sarki
        fields = ['dil', 'sozler']
        widgets = {
            'dil': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'sozler': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Şarkı sözlerini yazın'), 'rows': 6, 'required': True}),
        }
        widgets = {
            'album': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Şarkı adını yazın'), 'required': True}),
            'sozler': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Şarkı sözlerini yazın'), 'rows': 6, 'required': True}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Şarkı bağlantısı (isteğe bağlı)')})
        }
    
    def clean_sozler(self):
        sozler = self.cleaned_data.get('sozler')
        if not sozler or not sozler.strip():
            raise forms.ValidationError(_('Şarkı sözleri zorunludur.'))
        return sozler

class SarkiDuzenleForm(forms.ModelForm):
    class Meta:
        model = Sarki
        fields = ['sozler']
        widgets = {
            'sozler': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Şarkı sözlerini yazın'), 'rows': 6, 'required': True}),
        }

    def clean_sozler(self):
        sozler = self.cleaned_data.get('sozler')
        if not sozler.strip():
            raise forms.ValidationError(_('Şarkı sözleri zorunludur.'))
        return sozler
        
    
class AtasozuDeyimForm(forms.Form):
    tur = forms.ChoiceField(
        choices=[('atasozu', _('Atasözü')), ('deyim', _('Deyim'))],
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        label=_('Tür')
    )
    kelime = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Atasözü veya deyimi yazın'), 'required': True}),
        label=_('Atasözü/Deyim')
    )
    anlami = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Anlamı yazın'), 'rows': 4, 'required': True}),
        label=_('Anlam')
    )
    ornek = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Örnek kullanım (isteğe bağlı)'), 'rows': 4}),
        label=_('Örnek')
    )

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError(_('Atasözü/Deyim alanı zorunludur.'))
        tur = self.cleaned_data.get('tur')
        if tur == 'atasozu' and Atasozu.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError(_('Bu atasözü zaten mevcut, lütfen farklı bir ifade yazın.'))
        if tur == 'deyim' and Deyim.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError(_('Bu deyim zaten mevcut, lütfen farklı bir ifade yazın.'))
        return kelime

    def clean_anlami(self):
        anlami = self.cleaned_data.get('anlami')
        return clean_form_text(anlami)

    def clean_ornek(self):
        ornek = self.cleaned_data.get('ornek', '')
        if ornek:
            return clean_form_text(ornek)
        return ornek

class AtasozuDeyimAramaForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Kelime veya anlamı arayın...')}),
        label=_('Arama')
    )
    tarih_baslangic = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Başlangıç Tarihi')
    )
    tarih_bitis = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Bitiş Tarihi')
    )
    kullanici = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ekleyen kullanıcı...')}),
        label=_('Ekleyen Kullanıcı')
    )

    def clean_query(self):
        query = self.cleaned_data.get('query', '')
        return bleach.clean(query, tags=[], strip=True)

    def clean_kullanici(self):
        kullanici = self.cleaned_data.get('kullanici', '')
        return bleach.clean(kullanici, tags=[], strip=True)

class AtasozuDeyimDetayForm(forms.ModelForm):
    class Meta:
        model = AtasozuDeyimDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Ek detayları yazın'), 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError(_('Detay alanı zorunludur.'))
        return bleach.clean(detay, tags=['p', 'b', 'i'], strip=True)

class AtasozuDeyimDuzenleForm(forms.Form):
    kelime = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Atasözü veya deyimi yazın'), 'required': True}),
        label=_('Atasözü/Deyim')
    )
    anlami = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Anlamı yazın'), 'rows': 4, 'required': True}),
        label=_('Anlam')
    )
    ornek = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Örnek kullanım (isteğe bağlı)'), 'rows': 4}),
        label=_('Örnek')
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['kelime'].initial = self.instance.kelime
            self.fields['anlami'].initial = self.instance.anlami
            self.fields['ornek'].initial = self.instance.ornek

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError(_('Atasözü/Deyim alanı zorunludur.'))
        kelime = kelime.upper()
        if self.instance:
            if Atasozu.objects.filter(kelime__iexact=kelime).exclude(id=self.instance.id).exists():
                raise forms.ValidationError(_('Bu atasözü zaten mevcut, lütfen farklı bir ifade yazın.'))
            if Deyim.objects.filter(kelime__iexact=kelime).exclude(id=self.instance.id).exists():
                raise forms.ValidationError(_('Bu deyim zaten mevcut, lütfen farklı bir ifade yazın.'))
        else:
            if Atasozu.objects.filter(kelime__iexact=kelime).exists():
                raise forms.ValidationError(_('Bu atasözü zaten mevcut, lütfen farklı bir ifade yazın.'))
            if Deyim.objects.filter(kelime__iexact=kelime).exists():
                raise forms.ValidationError(_('Bu deyim zaten mevcut, lütfen farklı bir ifade yazın.'))
        return kelime

    def clean_anlami(self):
        anlami = self.cleaned_data.get('anlami')
        return clean_form_text(anlami)

    def clean_ornek(self):
        ornek = self.cleaned_data.get('ornek', '')
        if ornek:
            return clean_form_text(ornek)
        return ornek
    

class YerAdiForm(forms.ModelForm):
    class Meta:
        model = YerAdi
        fields = ['ad', 'detay', 'kategori', 'bolge', 'enlem', 'boylam', 'parent']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Yer adını yazın'), 'required': True}),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Yer hakkında detay yazın'), 'rows': 4}),
            'kategori': forms.Select(attrs={'class': 'form-control', 'required': True, 'onchange': 'toggleParentField()'}),
            'bolge': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'enlem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enlem (örnek: 37.7749)'), 'step': 'any'}),
            'boylam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Boylam (örnek: 40.7128)'), 'step': 'any'}),
            'parent': forms.Select(attrs={'class': 'form-control', 'id': 'id_parent'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = YerAdi.objects.all().order_by('ad')

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError(_('Yer adı alanı zorunludur.'))
        if not re.match(r'^[a-zçêîşû\s]+$', ad.lower()):
            raise forms.ValidationError(_('Yer adı sadece Kürtçe harfleri içerebilir (a-z, ç, ê, î, ş, û ve boşluk).'))
        ad_upper = ad.upper()
        if YerAdi.objects.filter(ad__iexact=ad_upper).exclude(pk=self.instance.pk if self.instance else None).exists():
            if not self.data.get('confirm_duplicate'):
                raise forms.ValidationError(_('Bu yer adı zaten mevcut, devam etmek istiyor musunuz?'), code='duplicate')
        return ad_upper

    def clean(self):
        cleaned_data = super().clean()
        enlem = cleaned_data.get('enlem')
        boylam = cleaned_data.get('boylam')
        kategori = cleaned_data.get('kategori')
        parent = cleaned_data.get('parent')
        if (enlem is not None and boylam is None) or (enlem is None and boylam is not None):
            raise forms.ValidationError(_('Enlem ve boylam birlikte yazılmalıdır.'))
        if kategori != 'il' and not parent:
            raise forms.ValidationError({'parent': _('Şehir dışındaki kategoriler için ilgili yer seçilmelidir.')})
        if kategori == 'il' and parent:
            raise forms.ValidationError({'parent': _('Şehir kategorisi için ilgili yer seçilmez.')})
        if parent:
            if kategori == 'ilce' and parent.kategori != 'il':
                raise forms.ValidationError({'parent': _('İlçe sadece bir şehirle bağlantılı olabilir.')})
            if kategori in ['kasaba', 'belde', 'koy'] and parent.kategori not in ['il', 'ilce']:
                raise forms.ValidationError({'parent': _('Kasaba, belde veya köy sadece şehir veya ilçe ile bağlantılı olabilir.')})
        return cleaned_data

class YerAdiDetayForm(forms.ModelForm):
    class Meta:
        model = YerAdiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Ek detayları yazın'), 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError(_('Detay alanı zorunludur.'))
        return detay