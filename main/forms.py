from django import forms
from .models import Post, Comment, Critique, CritiqueVote, Sozluk, Kisi, Album, Sarki, Atasozu, Deyim, SozlukDetay, SarkiDetay, AtasozuDeyimDetay, KisiDetay, YerAdi, YerAdiDetay
import bleach
import re
from django.utils.translation import gettext_lazy as _



def clean_form_text(text, allowed_tags=['p', 'b', 'i']):
    """Ortak metin temizleme fonksiyonu."""
    if not text.strip():
        raise forms.ValidationError("Bu alan boş olamaz.")
    return bleach.clean(text, tags=allowed_tags, strip=False)

class PostForm(forms.ModelForm):
    link = forms.URLField(required=False)

    class Meta:
        model = Post
        fields = ['title', 'text', 'link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Eleştiri Başlığı'}),
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Bir eleştiri paylaş...'}),
            'link': forms.URLInput(attrs={'class': 'form-control border-0 mt-2', 'placeholder': 'Link ekle (isteğe bağlı)'})
        }

    def clean_text(self):
        return clean_form_text(self.cleaned_data['text'], allowed_tags=['p', 'br', 'img'])

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Yorum yap...', 'maxlength': 500})
        }

    def clean_text(self):
        text = clean_form_text(self.cleaned_data['text'])
        if len(text) > 500:
            raise forms.ValidationError("Yorum 500 karakterden uzun olamaz.")
        return text

class CritiqueForm(forms.ModelForm):
    class Meta:
        model = Critique
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Eleştirinizi yazın...', 'maxlength': 5000})
        }

    def clean_text(self):
        text = clean_form_text(self.cleaned_data['text'], allowed_tags=['p', 'b', 'i', 'img'])
        if len(text) > 5000:
            raise forms.ValidationError("Değerlendirme 5000 karakterden uzun olamaz.")
        return text

class CritiqueVoteForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = CritiqueVote
        fields = ['rating']

class SozlukForm(forms.ModelForm):
    tur = forms.ChoiceField(
        choices=[('', 'Seçiniz'), ('isim', 'İsim'), ('fiil', 'Fiil'), ('sifat', 'Sıfat'), ('zarf', 'Zarf')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Sozluk
        fields = ['kelime', 'detay', 'tur']
        widgets = {
            'kelime': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kelime girin', 'required': True}),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kelime detayını girin', 'rows': 4, 'required': True}),
        }

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError('Kelime alanı zorunludur.')
        if self.instance and self.instance.pk:
            if kelime.lower() == self.instance.kelime.lower():
                return kelime
        if Sozluk.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Bu kelime zaten sözlükte mevcut, lütfen farklı bir kelime girin.')
        return kelime

class SozlukDetayForm(forms.ModelForm):
    class Meta:
        model = SozlukDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ek detay girin', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Detay alanı zorunludur.')
        return detay

class SarkiDetayForm(forms.ModelForm):
    class Meta:
        model = SarkiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ek detay girin', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Detay alanı zorunludur.')
        return detay

class KisiForm(forms.ModelForm):
    class Meta:
        model = Kisi
        fields = ['ad', 'biyografi', 'kategoriler']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kişinin adını girin', 'required': True}),
            'biyografi': forms.Textarea(attrs={'class': 'form-control d-none', 'id': 'biyografi-hidden', 'required': True}),
            'kategoriler': forms.SelectMultiple(attrs={'class': 'form-control select2', 'required': True}),
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Ad alanı zorunludur.')
        return ad

    def clean_biyografi(self):
        biyografi = self.cleaned_data.get('biyografi')
        if not biyografi.strip():
            raise forms.ValidationError('Biyografi alanı zorunludur.')
        return biyografi
    
class KisiDetayForm(forms.ModelForm):
    class Meta:
        model = KisiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ek detay girin', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Detay alanı zorunludur.')
        return bleach.clean(detay, tags=['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'], strip=True)  

class AlbumForm(forms.ModelForm):
    yil = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Albüm yılı (isteğe bağlı)'}))

    class Meta:
        model = Album
        fields = ['ad', 'yil']  # 'tur' alanı kaldırıldı
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Albüm adını girin', 'required': True}),
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Albüm adı zorunludur.')
        return ad

class SarkiForm(forms.ModelForm):
    link = forms.URLField(required=False)
    tur = forms.ChoiceField(
        choices=[
            ('', 'Tür Seçiniz'),
            ('pop', 'Pop'),
            ('klasik', 'Klasik'),
            ('arabesk', 'Arabesk'),
            ('dengbej', 'Dengbêj'),
            ('halk', 'Halk Müziği'),
            ('serbest', 'Serbest')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})

    )

    class Meta:
        model = Sarki
        fields = ['album', 'ad', 'sozler', 'link', 'tur']  # 'tur' alanı eklendi
        widgets = {
            'album': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şarkı adını girin', 'required': True}),
            'sozler': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Şarkı sözlerini girin', 'rows': 6, 'required': True}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Şarkı linki (isteğe bağlı)'})
        }
    
    def __init__(self, *args, **kwargs):
        super(SarkiForm, self).__init__(*args, **kwargs)
        # Albüm alanını dinamik olarak doldur
        self.fields['album'].queryset = Album.objects.all().order_by('ad')
        # Eğer form bir Sarki nesnesi ile başlatılmışsa, albüm alanını o şarkının albümü ile doldur
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['album'].initial = kwargs['instance'].album.id if kwargs['instance'].album else None
    # Şarkı adı ve albüm alanlarının temizlenmesi
    def clean(self):
        cleaned_data = super().clean()
        ad = cleaned_data.get('ad')
        album = cleaned_data.get('album')
        sozler = cleaned_data.get('sozler')
        if not ad or not ad.strip():
            raise forms.ValidationError('Şarkı adı zorunludur.')
        if not album:
                raise forms.ValidationError('Albüm seçimi zorunludur.')
        if not sozler or not sozler.strip():
            raise forms.ValidationError('Şarkı sözleri zorunludur.')
        # Albümde aynı isimde bir şarkı kontrolü
        if album:
            existing_songs = Sarki.objects.filter(album=album, ad__iexact=ad)
            if self.instance and self.instance.pk:  # Eğer düzenleme yapılıyorsa, mevcut şarkıyı hariç tut
                existing_songs = existing_songs.exclude(pk=self.instance.pk)
            if existing_songs.exists():
                raise forms.ValidationError('Bu albümde aynı isimde bir şarkı zaten mevcut.')
        return cleaned_data

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Şarkı adı zorunludur.')
        return ad
    def clean_album(self):
        album = self.cleaned_data.get('album')
        if not album:
            raise forms.ValidationError('Albüm seçimi zorunludur.')
        return album


    def clean_sozler(self):
        sozler = self.cleaned_data.get('sozler')
        if not sozler.strip():
            raise forms.ValidationError('Şarkı sözleri zorunludur.')
        # Eğer sözler çok uzun ise, 5000 karakter sınırı koy
        if len(sozler) > 5000:
            raise forms.ValidationError('Şarkı sözleri 5000 karakterden uzun olamaz.')
        return sozler

    
class SarkiDuzenleForm(forms.ModelForm):
    link = forms.URLField(required=False)
    tur = forms.ChoiceField(
        choices=[
            ('', 'Tür Seçiniz'),
            ('pop', 'Pop'),
            ('klasik', 'Klasik'),
            ('arabesk', 'Arabesk'),
            ('dengbej', 'Dengbêj'),
            ('halk', 'Halk Müziği'),
            ('serbest', 'Serbest')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Sarki
        fields = ['ad', 'sozler', 'link', 'tur']  # album field is excluded for editing
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şarkı adını girin', 'required': True}),
            'sozler': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Şarkı sözlerini girin', 'rows': 6, 'required': True}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Şarkı linki (isteğe bağlı)'})
            # album field is excluded for editing
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Şarkı adı zorunludur.')
               

        # Check for duplicate song names in the same album
        if self.instance and self.instance.album:
            existing_songs = Sarki.objects.filter(album=self.instance.album, ad__iexact=ad)
            if self.instance.pk:  # If editing an existing song
                existing_songs = existing_songs.exclude(pk=self.instance.pk)
            if existing_songs.exists():
                raise forms.ValidationError('Bu albümde aynı isimde bir şarkı zaten mevcut.')
        return ad

    def clean_sozler(self):
        sozler = self.cleaned_data.get('sozler')
        if not sozler.strip():
            raise forms.ValidationError('Şarkı sözleri zorunludur.')
        return sozler
        
    
class AtasozuDeyimForm(forms.Form):
    tur = forms.ChoiceField(
        choices=[('atasozu', 'Atasözü'), ('deyim', 'Deyim')],
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        label='Tür'
    )
    kelime = forms.CharField(
        max_length=500,  # max_length models.py ile uyumlu hale getirildi
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Atasözü veya deyimi girin', 'required': True}),
        label='Atasözü/Deyim'
    )
    anlami = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Anlamını girin', 'rows': 4, 'required': True}),
        label='Anlam'
    )
    ornek = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Örnek kullanım (isteğe bağlı)', 'rows': 4}),
        label='Örnek'
    )

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError('Atasözü/Deyim alanı zorunludur.')
        # Katı harf kontrolünü kaldırdık, yalnızca var olan kayıt kontrolü yapıyoruz
        tur = self.cleaned_data.get('tur')
        if tur == 'atasozu' and Atasozu.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Bu atasözü zaten mevcut, lütfen farklı bir ifade girin.')
        if tur == 'deyim' and Deyim.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Bu deyim zaten mevcut, lütfen farklı bir ifade girin.')
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kelime veya anlam ara...'}),
        label='Arama'
    )
    tarih_baslangic = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Başlangıç Tarihi'
    )
    tarih_bitis = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Bitiş Tarihi'
    )
    kullanici = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ekleyen kullanıcı...'}),
        label='Ekleyen Kullanıcı'
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
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ek detay girin', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Detay alanı zorunludur.')
        return bleach.clean(detay, tags=['p', 'b', 'i'], strip=True)

class AtasozuDeyimDuzenleForm(forms.Form):
    kelime = forms.CharField(
        max_length=500,  # max_length models.py ile uyumlu hale getirildi
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Atasözü veya deyimi girin', 'required': True}),
        label='Atasözü/Deyim'
    )
    anlami = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Anlamını girin', 'rows': 4, 'required': True}),
        label='Anlam'
    )
    ornek = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Örnek kullanım (isteğe bağlı)', 'rows': 4}),
        label='Örnek'
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
            raise forms.ValidationError('Atasözü/Deyim alanı zorunludur.')
        # Katı harf kontrolünü kaldırdık, yalnızca var olan kayıt kontrolü yapıyoruz
        kelime = kelime.upper()
        # Mevcut instance’ın kendi kelimesi hariç kontrol
        if self.instance:
            if Atasozu.objects.filter(kelime__iexact=kelime).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('Bu atasözü zaten mevcut, lütfen farklı bir ifade girin.')
            if Deyim.objects.filter(kelime__iexact=kelime).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('Bu deyim zaten mevcut, lütfen farklı bir ifade girin.')
        else:
            if Atasozu.objects.filter(kelime__iexact=kelime).exists():
                raise forms.ValidationError('Bu atasözü zaten mevcut, lütfen farklı bir ifade girin.')
            if Deyim.objects.filter(kelime__iexact=kelime).exists():
                raise forms.ValidationError('Bu deyim zaten mevcut, lütfen farklı bir ifade girin.')
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
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Yer adını girin', 'required': True}),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Yer hakkında detay girin', 'rows': 4}),
            'kategori': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'bolge': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'enlem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enlem (ör. 37.7749)', 'step': 'any'}),
            'boylam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Boylam (ör. 40.7128)', 'step': 'any'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parent seçimini kategori ve hiyerarşiye göre sınırla
        self.fields['parent'].queryset = YerAdi.objects.filter(kategori__in=['il', 'ilce'])
        if self.instance and self.instance.kategori == 'il':
            self.fields['parent'].required = False
        elif self.instance and self.instance.kategori in ['ilce', 'kasaba', 'belde', 'koy']:
            self.fields['parent'].required = True

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Yer adı alanı zorunludur.')
        if not re.match(r'^[a-zçêîşû\s]+$', ad.lower()):
            raise forms.ValidationError('Yer adı sadece Kürtçe harfler içerebilir (a-z, ç, ê, î, ş, û ve boşluk).')
        ad_upper = ad.upper()
        if YerAdi.objects.filter(ad__iexact=ad_upper).exclude(pk=self.instance.pk if self.instance else None).exists():
            if not self.data.get('confirm_duplicate'):
                raise forms.ValidationError('Bu yer adı zaten mevcut, eklemeye devam etmek istiyor musunuz?', code='duplicate')
        return ad_upper

    def clean(self):
        cleaned_data = super().clean()
        enlem = cleaned_data.get('enlem')
        boylam = cleaned_data.get('boylam')
        kategori = cleaned_data.get('kategori')
        parent = cleaned_data.get('parent')
        if (enlem is not None and boylam is None) or (enlem is None and boylam is not None):
            raise forms.ValidationError('Enlem ve boylam birlikte girilmelidir.')
        if kategori != 'il' and not parent:
            raise forms.ValidationError({'parent': 'İl dışındaki kategoriler için bağlı olduğu yer seçilmelidir.'})
        if kategori == 'il' and parent:
            raise forms.ValidationError({'parent': 'İl kategorisi için bağlı yer seçilemez.'})
        if parent:
            if kategori == 'ilce' and parent.kategori != 'il':
                raise forms.ValidationError({'parent': 'İlçe sadece bir ile bağlı olabilir.'})
            if kategori in ['kasaba', 'belde', 'koy'] and parent.kategori not in ['il', 'ilce']:
                raise forms.ValidationError({'parent': 'Kasaba, belde veya köy sadece il veya ilçeye bağlı olabilir.'})
        return cleaned_data

class YerAdiDetayForm(forms.ModelForm):
    class Meta:
        model = YerAdiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ek detay girin', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Detay alanı zorunludur.')
        return detay