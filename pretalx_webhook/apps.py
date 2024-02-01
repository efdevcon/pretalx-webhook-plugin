from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "pretalx_webhook"
    verbose_name = "Pretalx webhook plugin"

    class PretalxPluginMeta:
        name = gettext_lazy("Pretalx webhook plugin")
        author = "Devcon"
        description = gettext_lazy("pretalx plugin for Pretalx webhook plugin")
        visible = True
        version = __version__
        category = "INTEGRATION"

    def ready(self):
        from . import signals  # NOQA
