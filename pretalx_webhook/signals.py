import json
import requests
import logging
from django.dispatch import receiver
from django.conf import settings
from pretalx.schedule.signals import schedule_release

logger = logging.getLogger(__name__)

@receiver(schedule_release, dispatch_uid="pretalx_webhook_schedule_release")
def on_schedule_release(sender, schedule, user, **kwargs):
    try:
        webhook_settings = settings.PLUGIN_SETTINGS["pretalx_webhook"]
        if not webhook_settings:
            logger.error(f"Webhook settings are empty or invalid for event {sender.slug}")
            return

        webhook_endpoint = webhook_settings["endpoint"]
        webhook_secret = webhook_settings["secret"]

        if not webhook_endpoint:
            logger.error(f"Webhook endpoint is empty for event {sender.slug}")
            return
        
        logger.info(f"Preparing payload for {sender.slug} with schedule {schedule.version}")
        payload = {
            'event': sender.slug,
            'user': str(user),
            'schedule': schedule.version,
            'changes': {
                'new_talks': [talk.submission.code for talk in schedule.changes.get('new_talks', [])],
                'canceled_talks': [talk.submission.code for talk in schedule.changes.get('canceled_talks', [])],
                'moved_talks': [talk['submission'].code for talk in schedule.changes.get('moved_talks', [])],
            },
        }

        headers = {'Content-Type': 'application/json'}
        if webhook_secret:
            headers['X-Webhook-Secret'] = webhook_secret
        else:
            logger.warning(f"Webhook secret is empty for event {sender.slug}")

        logger.info(f"POST JSON request to {webhook_endpoint} with payload: {payload}")
        response = requests.post(webhook_endpoint,
            json=payload,
            headers=headers,
        )
        
        if response.status_code == 200:
            logger.info(f"Webhook sent successfully for event {sender.slug}")
        else:
            logger.error(f"Webhook failed for event {sender.slug}. Status code: {response.status_code}")

    except Exception as e:
        logger.error(f"Error sending webhook for event {sender.slug}: {str(e)}")
