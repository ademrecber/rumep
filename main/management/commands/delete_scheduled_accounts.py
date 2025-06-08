from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from main.models import Profile

class Command(BaseCommand):
    help = 'Delete accounts that were scheduled for deletion and have passed their scheduled deletion date'

    def handle(self, *args, **options):
        # Get current time
        now = timezone.now()
        
        # Find profiles scheduled for deletion with a deletion date in the past
        profiles_to_delete = Profile.objects.filter(
            account_status='deletion_scheduled',
            scheduled_deletion_date__lte=now
        )
        
        # Count how many accounts will be deleted
        count = profiles_to_delete.count()
        
        # Delete the users (this will cascade delete the profiles as well)
        User = get_user_model()
        for profile in profiles_to_delete:
            user = profile.user
            self.stdout.write(f"Deleting user: {user.username} (scheduled on {profile.scheduled_deletion_date})")
            user.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} accounts'))