from django.conf import settings
from django.core import checks
from django.core.checks import Tags, register

API_URL = "https://panel.emaillabs.net.pl/pl/site/api"


@register(Tags.database, production=True)
def emaillabs_api_key_checks(app_configs, **kwargs):
    errors = []
    if not getattr(settings, "EMAILLABS_APP_KEY", False):
        errors.append(
            checks.Warning(
                "Missing EMAILLABS_APP_KEY settings.",
                hint="Visit {} to get API app key. "
                "Next to set EMAILLABS_APP_KEY settings.".format(API_URL),
                id="letters.logs.E001",
            )
        )
    if not getattr(settings, "EMAILLABS_SECRET_KEY", False):
        errors.append(
            checks.Warning(
                "Missing EMAILLABS_SECRET_KEY settings.",
                hint="Visit {} to get API secret key. "
                "Next to set EMAILLABS_SECRET_KEY settings.".format(API_URL),
                id="letters.logs.E002",
            )
        )
    return errors
