from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def profile_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        
        # Profil otomatik oluştur
        try:
            if not hasattr(request.user, 'profile'):
                from ..models import Profile
                Profile.objects.create(
                    user=request.user,
                    nickname=request.user.username,
                    username=request.user.username
                )
        except:
            pass
            
        return view_func(request, *args, **kwargs)
    return wrapper