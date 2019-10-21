from django.apps import AppConfig
from django.core.checks import register
from django.utils.translation import ugettext_lazy as _

from .checks import test_modulators_list_settings


class CustomAppConfig(AppConfig):
    name = "feder.questionaries"
    verbose_name = _("Questionaries")

    def ready(*args, **kwargs):
        register(test_modulators_list_settings)
