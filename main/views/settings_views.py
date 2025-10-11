from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _

@login_required
def user_settings(request):
    """Kullanıcı ayarları sayfası"""
    return render(request, 'main/settings.html')

@login_required
def privacy_settings(request):
    """Gizlilik ayarları"""
    if request.method == 'POST':
        # Gizlilik ayarlarını kaydet
        profile = request.user.profile
        profile.is_private = request.POST.get('is_private') == 'on'
        profile.show_email = request.POST.get('show_email') == 'on'
        profile.save()
        messages.success(request, _('Gizlilik ayarları güncellendi'))
        return redirect('privacy_settings')
    
    return render(request, 'main/privacy_settings.html')

@login_required
def notification_settings(request):
    """Bildirim ayarları"""
    if request.method == 'POST':
        # Bildirim ayarlarını kaydet
        profile = request.user.profile
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.save()
        messages.success(request, _('Bildirim ayarları güncellendi'))
        return redirect('notification_settings')
    
    return render(request, 'main/notification_settings.html')