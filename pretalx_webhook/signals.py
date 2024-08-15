import json
import requests
import logging
from django.dispatch import receiver
from django.urls import reverse
from django.conf import settings
from pretalx.orga.signals import nav_event_settings
from pretalx.schedule.signals import schedule_release

logger = logging.getLogger(__name__)

@receiver(schedule_release, dispatch_uid="pretalx_webhook_schedule_release")
def on_schedule_release(sender, schedule, user, **kwargs):
    try:
        # Get the webhook settings for this event
        webhook_settings = settings.PLUGIN_SETTINGS["pretalx_webhook"]
        if not webhook_settings:
            logger.info(f"Webhook settings are empty or invalid for event {sender.slug}")
            return

        webhook_endpoint = webhook_settings["endpoint"]
        webhook_secret = webhook_settings["secret"]

        if not webhook_endpoint:
            logger.info(f"Webhook endpoint is empty for event {sender.slug}")
            return

        # Prepare the payload
        payload = {
            # 'event': sender.slug,
            # 'schedule_version': schedule.version,
            'sender': sender,
            'schedule': schedule,
            'user': user,
            'args': kwargs,
        }

        headers = {'Content-Type': 'application/json'}
        if webhook_settings.secret_key:
            headers['X-Webhook-Secret'] = webhook_settings.secret_key
        else:
            logger.warning(f"Webhook secret is empty for event {sender.slug}")

        # Send the POST request to the webhook endpoint
        response = requests.post(webhook_endpoint,
            json=json.dumps(payload),
            headers=headers,
        )
        
        # Log the response (you may want to handle this differently)
        if response.status_code == 200:
            logger.info(f"Webhook sent successfully for event {sender.slug}")
        else:
            logger.error(f"Webhook failed for event {sender.slug}. Status code: {response.status_code}")

    except Exception as e:
        logger.error(f"Error sending webhook for event {sender.slug}: {str(e)}")