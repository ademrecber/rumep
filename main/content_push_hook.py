"""Wake the existing sender after commit; the periodic poll remains the fallback."""
import json
import logging
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from django.db import transaction

logger = logging.getLogger(__name__)
HOOK_URL = 'https://amedspor-football-api.emrahrecber88.workers.dev/hooks/content-published'


def schedule_content_push(kind, pk, using=None):
    transaction.on_commit(lambda: send_content_push(kind, pk, using), using=using)


def send_content_push(kind, pk, using=None):
    token = os.environ.get('CONTENT_PUSH_WEBHOOK_TOKEN', '')
    if not token:
        return
    from .models import SportPost, Wallpaper
    from .content_notifications import content_payload
    model = SportPost if kind == 'post' else Wallpaper
    obj = model.objects.using(using).filter(pk=pk, is_published=True, notify_users=True).first()
    if obj is None or obj.notification_requested_at is None:
        return
    data = content_payload(obj, kind, 'https://rumep.net')
    request = Request(HOOK_URL, data=json.dumps(data).encode('utf-8'), method='POST',
                      headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}',
                               'User-Agent': 'Rumep-Content-Publisher/1.0'})
    try:
        with urlopen(request, timeout=8) as response:
            if response.status != 200:
                logger.warning('Content push hook deferred: %s', response.status)
    except HTTPError as error:
        logger.warning('Content push hook HTTP %s; scheduled poll will retry', error.code)
    except Exception:
        # Saving content succeeds even if delivery must wait for the backup poll.
        # Never log credentials, payloads or URL exception details.
        logger.warning('Content push hook unavailable; scheduled poll will retry')
