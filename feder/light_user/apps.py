from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LightUserConfig(AppConfig):
    name = "feder.light_user"
    verbose_name = _("Light Users")

    def ready(self):
        pass
