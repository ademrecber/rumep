from django.conf import settings

def global_settings(request):
    """
    Adds settings variables to the context of every template.
    """
    return {
        'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
    }