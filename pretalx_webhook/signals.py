
from django.dispatch import receiver
from django.urls import reverse
from pretalx.orga.signals import nav_event_settings


@receiver(nav_event_settings)
def pretalx_webhook_settings(sender, request, **kwargs):
    if not request.user.has_perm("orga.change_settings", request.event):
        return []
    return [
        {
            "label": "Pretalx webhook plugin",
            "url": reverse(
                "plugins:pretalx_webhook:settings",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name
            == "plugins:pretalx_webhook:settings",
        }
    ]

