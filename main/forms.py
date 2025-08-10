from django import forms
from .models import Post, Comment, Critique, CritiqueVote, Sozluk, Kisi, Album, Sarki, Atasozu, Deyim, SozlukDetay, SarkiDetay, AtasozuDeyimDetay, KisiDetay, YerAdi, YerAdiDetay
import bleach
import re
from django.utils.translation import gettext_lazy as _



def clean_form_text(text, allowed_tags=['p', 'b', 'i']):
    """Fonksiyona paqijkirina nivîsê ya hevpar."""
    if not text.strip():
        raise forms.ValidationError("Ev qad nikare vala be.")
    return bleach.clean(text, tags=allowed_tags, strip=False)

class PostForm(forms.ModelForm):
    link = forms.URLField(required=False)

    class Meta:
        model = Post
        fields = ['title', 'text', 'link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sernavê Nirxandinê'}),
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Nirxandinekê parve bike...'}),
            'link': forms.URLInput(attrs={'class': 'form-control border-0 mt-2', 'placeholder': 'Girêdanê lê zêde bike (bijarte)'})
        }

    def clean_text(self):
        return clean_form_text(self.cleaned_data['text'], allowed_tags=['p', 'br', 'img'])

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Şîrove bike...', 'maxlength': 500})
        }

    def clean_text(self):
        text = clean_form_text(self.cleaned_data['text'])
        if len(text) > 500:
            raise forms.ValidationError("Şîrove nikare ji 500 tîpan dirêjtir be.")
        return text

class CritiqueForm(forms.ModelForm):
    class Meta:
        model = Critique
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Nirxandina xwe binivîse...', 'maxlength': 5000})
        }

    def clean_text(self):
        text = clean_form_text(self.cleaned_data['text'], allowed_tags=['p', 'b', 'i', 'img'])
        if len(text) > 5000:
            raise forms.ValidationError("Nirxandin nikare ji 5000 tîpan dirêjtir be.")
        return text

class CritiqueVoteForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = CritiqueVote
        fields = ['rating']

class SozlukForm(forms.ModelForm):
    tur = forms.ChoiceField(
        choices=[('', 'Hilbijêre'), ('isim', 'Nav'), ('fiil', 'Lêker'), ('sifat', 'Sifet'), ('zarf', 'Zarf')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Sozluk
        fields = ['kelime', 'detay', 'tur']
        widgets = {
            'kelime': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Peyvê binivîse', 'required': True}),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kîtekîtên peyvê binivîse', 'rows': 4, 'required': True}),
        }

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError('Qada peyvê mecbûrî ye.')
        if self.instance and self.instance.pk:
            if kelime.lower() == self.instance.kelime.lower():
                return kelime
        if Sozluk.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Ev peyv jixwe di ferhengê de heye, ji kerema xwe peyveke cuda binivîse.')
        return kelime

class SozlukDetayForm(forms.ModelForm):
    class Meta:
        model = SozlukDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kîtekîtên zêde binivîse', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Qada kîtekîtê mecbûrî ye.')
        return detay

class SarkiDetayForm(forms.ModelForm):
    class Meta:
        model = SarkiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kîtekîtên zêde binivîse', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Qada kîtekîtê mecbûrî ye.')
        return detay

class KisiForm(forms.ModelForm):
    class Meta:
        model = Kisi
        fields = ['ad', 'biyografi', 'kategoriler']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Navê kesê binivîse', 'required': True}),
            'biyografi': forms.Textarea(attrs={'class': 'form-control d-none', 'id': 'biyografi-hidden', 'required': True}),
            'kategoriler': forms.SelectMultiple(attrs={'class': 'form-control select2', 'required': True}),
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Qada navê mecbûrî ye.')
        return ad

    def clean_biyografi(self):
        biyografi = self.cleaned_data.get('biyografi')
        if not biyografi.strip():
            raise forms.ValidationError('Qada biyografiyê mecbûrî ye.')
        return biyografi
    
class KisiDetayForm(forms.ModelForm):
    class Meta:
        model = KisiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kîtekîtên zêde binivîse', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Qada kîtekîtê mecbûrî ye.')
        return bleach.clean(detay, tags=['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'], strip=True)  

class AlbumForm(forms.ModelForm):
    yil = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sala albûmê (bijarte)'}))

    class Meta:
        model = Album
        fields = ['ad', 'yil']  # 'tur' alanı kaldırıldı
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Navê albûmê binivîse', 'required': True}),
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Navê albûmê mecbûrî ye.')
        return ad

class SarkiForm(forms.ModelForm):
    link = forms.URLField(required=False)
    tur = forms.ChoiceField(
        choices=[
            ('', 'Cure Hilbijêre'),
            ('pop', 'Pop'),
            ('klasik', 'Klasîk'),
            ('arabesk', 'Erebesk'),
            ('dengbej', 'Dengbêj'),
            ('halk', 'Muzîka Gelêrî'),
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
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Navê stranê binivîse', 'required': True}),
            'sozler': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Gotinên stranê binivîse', 'rows': 6, 'required': True}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Girêdana stranê (bijarte)'})
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
            raise forms.ValidationError('Navê stranê mecbûrî ye.')
        if not album:
                raise forms.ValidationError('Hilbijartina albûmê mecbûrî ye.')
        if not sozler or not sozler.strip():
            raise forms.ValidationError('Gotinên stranê mecbûrî ne.')
        # Albümde aynı isimde bir şarkı kontrolü
        if album:
            existing_songs = Sarki.objects.filter(album=album, ad__iexact=ad)
            if self.instance and self.instance.pk:  # Eğer düzenleme yapılıyorsa, mevcut şarkıyı hariç tut
                existing_songs = existing_songs.exclude(pk=self.instance.pk)
            if existing_songs.exists():
                raise forms.ValidationError('Di vê albûmê de jixwe stranek bi heman navî heye.')
        return cleaned_data

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Navê stranê mecbûrî ye.')
        return ad
    def clean_album(self):
        album = self.cleaned_data.get('album')
        if not album:
            raise forms.ValidationError('Hilbijartina albûmê mecbûrî ye.')
        return album


    def clean_sozler(self):
        sozler = self.cleaned_data.get('sozler')
        if not sozler.strip():
            raise forms.ValidationError('Gotinên stranê mecbûrî ne.')
        # Eğer sözler çok uzun ise, 5000 karakter sınırı koy
        if len(sozler) > 5000:
            raise forms.ValidationError('Gotinên stranê nikarin ji 5000 tîpan dirêjtir bin.')
        return sozler

    
class SarkiDuzenleForm(forms.ModelForm):
    link = forms.URLField(required=False)
    tur = forms.ChoiceField(
        choices=[
            ('', 'Cure Hilbijêre'),
            ('pop', 'Pop'),
            ('klasik', 'Klasîk'),
            ('arabesk', 'Erebesk'),
            ('dengbej', 'Dengbêj'),
            ('halk', 'Muzîka Gelêrî'),
            ('serbest', 'Serbest')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Sarki
        fields = ['ad', 'sozler', 'link', 'tur']  # album field is excluded for editing
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Navê stranê binivîse', 'required': True}),
            'sozler': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Gotinên stranê binivîse', 'rows': 6, 'required': True}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Girêdana stranê (bijarte)'})
            # album field is excluded for editing
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Navê stranê mecbûrî ye.')
               

        # Check for duplicate song names in the same album
        if self.instance and self.instance.album:
            existing_songs = Sarki.objects.filter(album=self.instance.album, ad__iexact=ad)
            if self.instance.pk:  # If editing an existing song
                existing_songs = existing_songs.exclude(pk=self.instance.pk)
            if existing_songs.exists():
                raise forms.ValidationError('Di vê albûmê de jixwe stranek bi heman navî heye.')
        return ad

    def clean_sozler(self):
        sozler = self.cleaned_data.get('sozler')
        if not sozler.strip():
            raise forms.ValidationError('Gotinên stranê mecbûrî ne.')
        return sozler
        
    
class AtasozuDeyimForm(forms.Form):
    tur = forms.ChoiceField(
        choices=[('atasozu', 'Gotina Pêşiyan'), ('deyim', 'Îdîom')],
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        label='Cure'
    )
    kelime = forms.CharField(
        max_length=500,  # max_length models.py ile uyumlu hale getirildi
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gotina pêşiyan an îdîomê binivîse', 'required': True}),
        label='Gotina Pêşiyan/Îdîom'
    )
    anlami = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Wateyê binivîse', 'rows': 4, 'required': True}),
        label='Wate'
    )
    ornek = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bikaranîna mînak (bijarte)', 'rows': 4}),
        label='Mînak'
    )

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError('Qada Gotina Pêşiyan/Îdîom mecbûrî ye.')
        # Katı harf kontrolünü kaldırdık, yalnızca var olan kayıt kontrolü yapıyoruz
        tur = self.cleaned_data.get('tur')
        if tur == 'atasozu' and Atasozu.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Ev gotina pêşiyan jixwe heye, ji kerema xwe îfadeyeke cuda binivîse.')
        if tur == 'deyim' and Deyim.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Ev îdîom jixwe heye, ji kerema xwe îfadeyeke cuda binivîse.')
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Peyv an wateyê lêbigere...'}),
        label='Lêgerîn'
    )
    tarih_baslangic = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Dîroka Destpêkê'
    )
    tarih_bitis = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Dîroka Dawiyê'
    )
    kullanici = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bikarhênerê zêdeker...'}),
        label='Bikarhênerê Zêdeker'
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
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kîtekîtên zêde binivîse', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Qada kîtekîtê mecbûrî ye.')
        return bleach.clean(detay, tags=['p', 'b', 'i'], strip=True)

class AtasozuDeyimDuzenleForm(forms.Form):
    kelime = forms.CharField(
        max_length=500,  # max_length models.py ile uyumlu hale getirildi
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gotina pêşiyan an îdîomê binivîse', 'required': True}),
        label='Gotina Pêşiyan/Îdîom'
    )
    anlami = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Wateyê binivîse', 'rows': 4, 'required': True}),
        label='Wate'
    )
    ornek = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bikaranîna mînak (bijarte)', 'rows': 4}),
        label='Mînak'
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
            raise forms.ValidationError('Qada Gotina Pêşiyan/Îdîom mecbûrî ye.')
        # Katı harf kontrolünü kaldırdık, yalnızca var olan kayıt kontrolü yapıyoruz
        kelime = kelime.upper()
        # Mevcut instance’ın kendi kelimesi hariç kontrol
        if self.instance:
            if Atasozu.objects.filter(kelime__iexact=kelime).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('Ev gotina pêşiyan jixwe heye, ji kerema xwe îfadeyeke cuda binivîse.')
            if Deyim.objects.filter(kelime__iexact=kelime).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('Ev îdîom jixwe heye, ji kerema xwe îfadeyeke cuda binivîse.')
        else:
            if Atasozu.objects.filter(kelime__iexact=kelime).exists():
                raise forms.ValidationError('Ev gotina pêşiyan jixwe heye, ji kerema xwe îfadeyeke cuda binivîse.')
            if Deyim.objects.filter(kelime__iexact=kelime).exists():
                raise forms.ValidationError('Ev îdîom jixwe heye, ji kerema xwe îfadeyeke cuda binivîse.')
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
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Navê cihê binivîse', 'required': True}),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Derbarê cihê de kîtekît binivîse', 'rows': 4}),
            'kategori': forms.Select(attrs={'class': 'form-control', 'required': True, 'onchange': 'toggleParentField()'}),
            'bolge': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'enlem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enlem (mînak: 37.7749)', 'step': 'any'}),
            'boylam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Boylam (mînak: 40.7128)', 'step': 'any'}),
            'parent': forms.Select(attrs={'class': 'form-control', 'id': 'id_parent'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parent seçimini dinamik olarak JavaScript yönetecek
        self.fields['parent'].queryset = YerAdi.objects.all().order_by('ad')

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Qada navê cihê mecbûrî ye.')
        if not re.match(r'^[a-zçêîşû\s]+$', ad.lower()):
            raise forms.ValidationError('Navê cihê tenê tîpên Kurdî dikare bigire (a-z, ç, ê, î, ş, û û valahî).')
        ad_upper = ad.upper()
        if YerAdi.objects.filter(ad__iexact=ad_upper).exclude(pk=self.instance.pk if self.instance else None).exists():
            if not self.data.get('confirm_duplicate'):
                raise forms.ValidationError('Ev navê cihê jixwe heye, ma hûn dixwazin berdewam bikin?', code='duplicate')
        return ad_upper

    def clean(self):
        cleaned_data = super().clean()
        enlem = cleaned_data.get('enlem')
        boylam = cleaned_data.get('boylam')
        kategori = cleaned_data.get('kategori')
        parent = cleaned_data.get('parent')
        if (enlem is not None and boylam is None) or (enlem is None and boylam is not None):
            raise forms.ValidationError('Enlem û boylam divê bi hev re bên nivîsandin.')
        if kategori != 'il' and not parent:
            raise forms.ValidationError({'parent': 'Ji bo kategoriyên derveyî bajêr divê cihê têkildar bê hilbijartin.'})
        if kategori == 'il' and parent:
            raise forms.ValidationError({'parent': 'Ji bo kategoriya bajêr cihê têkildar nayê hilbijartin.'})
        if parent:
            if kategori == 'ilce' and parent.kategori != 'il':
                raise forms.ValidationError({'parent': 'Navçe tenê dikare bi bajarekê ve bê girêdan.'})
            if kategori in ['kasaba', 'belde', 'koy'] and parent.kategori not in ['il', 'ilce']:
                raise forms.ValidationError({'parent': 'Qesebe, belde an gund tenê dikarin bi bajêr an navçeyê ve bên girêdan.'})
        return cleaned_data

class YerAdiDetayForm(forms.ModelForm):
    class Meta:
        model = YerAdiDetay
        fields = ['detay']
        widgets = {
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kîtekîtên zêde binivîse', 'rows': 4, 'required': True}),
        }

    def clean_detay(self):
        detay = self.cleaned_data.get('detay')
        if not detay.strip():
            raise forms.ValidationError('Qada kîtekîtê mecbûrî ye.')
        return detay