from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.utils import timezone
from datetime import timedelta
from ..models import Profile
from .base import profile_required

@login_required
@profile_required
@csrf_protect
@require_POST
def freeze_account(request):
    """
    Freeze the user's account.
    """
    profile = request.user.profile
    profile.account_status = 'frozen'
    profile.save()
    return redirect('profile')

@login_required
@profile_required
@csrf_protect
@require_POST
def unfreeze_account(request):
    """
    Unfreeze the user's account.
    """
    profile = request.user.profile
    profile.account_status = 'active'
    profile.save()
    return redirect('profile')

@login_required
@profile_required
@csrf_protect
@require_POST
def schedule_account_deletion(request):
    """
    Schedule the user's account for deletion in 30 days.
    """
    profile = request.user.profile
    profile.account_status = 'deletion_scheduled'
    profile.scheduled_deletion_date = timezone.now() + timedelta(days=30)
    profile.save()
    
    # Log the user out
    logout(request)
    
    return redirect('login_page')

@login_required
@profile_required
@csrf_protect
@require_POST
def cancel_account_deletion(request):
    """
    Cancel the scheduled deletion of the user's account.
    """
    profile = request.user.profile
    if profile.account_status == 'deletion_scheduled':
        profile.account_status = 'active'
        profile.scheduled_deletion_date = None
        profile.save()
    
    return redirect('profile')