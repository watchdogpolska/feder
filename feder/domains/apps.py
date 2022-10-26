from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DomainsConfig(AppConfig):
    name = "feder.domains"
    verbose_name = _("Domains")
