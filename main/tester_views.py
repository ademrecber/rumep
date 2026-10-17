import re
from django import forms
from django.core import signing
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import salted_hmac
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods
from .models import SporTestApplication


class TesterForm(forms.Form):
    email = forms.EmailField(max_length=254, label='Google Play Gmail adresin', widget=forms.EmailInput(attrs={
        'placeholder': 'ornek@gmail.com', 'autocomplete': 'email', 'inputmode': 'email',
        'autocapitalize': 'none', 'spellcheck': 'false', 'aria-describedby': 'email-help',
    }))
    consent = forms.BooleanField(label='Adresimin yalnızca kapalı test erişimi için kullanılmasını kabul ediyorum.')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        local, domain = email.rsplit('@', 1)
        if domain != 'gmail.com' or not re.fullmatch(r'[a-z0-9]+(?:\.[a-z0-9]+)*', local):
            raise forms.ValidationError('Google Play’de kullandığın @gmail.com adresini yaz. Boşluk, ardışık nokta ve ek adres (+) kullanma.')
        return email


@sensitive_post_parameters('email', 'confirmation')
@never_cache
@require_http_methods(['GET', 'POST'])
def tester_signup(request):
    context = {'form': TesterForm(), 'success': request.GET.get('done') == '1'}
    if request.method == 'POST':
        # No email/IP is placed in logs, URLs, or an analytics service.
        # Cookie-based limit avoids counting all Railway proxy users as one IP.
        client = request.COOKIES.get('csrftoken') or request.META.get('REMOTE_ADDR', '')
        key = 'spor-test:' + salted_hmac('tester-rate', client).hexdigest()
        attempts = cache.get(key, 0)
        if attempts >= 20:
            context['error'] = 'Biraz fazla deneme yapıldı. Lütfen birkaç dakika sonra tekrar dene.'
            return render(request, 'rumep-spor/testers.html', context, status=429)
        cache.set(key, attempts + 1, 300)
        if request.POST.get('action') == 'confirm':
            try:
                email = signing.loads(request.POST.get('confirmation', ''), salt='spor-tester', max_age=600)
                form = TesterForm({'email': email, 'consent': True})
                if not form.is_valid():
                    raise signing.BadSignature()
                # Gmail dots do not identify separate mailboxes.
                canonical = email.split('@')[0].replace('.', '') + '@gmail.com'
                SporTestApplication.objects.get_or_create(email=canonical)
                return HttpResponseRedirect(reverse('rumep_spor_testers') + '?done=1')
            except (signing.BadSignature, TypeError, ValueError):
                context['error'] = 'Onay süresi dolmuş veya bilgiler geçersiz. Adresini yeniden yazıp onayla.'
        else:
            form = TesterForm(request.POST)
            context['form'] = form
            if form.is_valid():
                context['preview_email'] = form.cleaned_data['email']
                context['confirmation'] = signing.dumps(form.cleaned_data['email'], salt='spor-tester')
    return render(request, 'rumep-spor/testers.html', context)
