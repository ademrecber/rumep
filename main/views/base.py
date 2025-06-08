from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def profile_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        if not hasattr(request.user, 'profile'):
            return redirect('complete_profile')
        return view_func(request, *args, **kwargs)
    return wrapper