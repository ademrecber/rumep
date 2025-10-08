from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def profile_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        
        # Admin ve staff kullanıcılar için profil kontrolü yok
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Profil yoksa otomatik oluştur
        if not hasattr(request.user, 'profile'):
            from ..models import Profile
            Profile.objects.get_or_create(
                user=request.user,
                defaults={
                    'nickname': request.user.username,
                    'username': request.user.username
                }
            )
        
        # Nickname yoksa username'i kullan
        if hasattr(request.user, 'profile') and not request.user.profile.nickname:
            request.user.profile.nickname = request.user.username
            request.user.profile.save()
            
        return view_func(request, *args, **kwargs)
    return wrapper