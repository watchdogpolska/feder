import urllib.parse

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from ..signer import TokenSigner


class BaseEngine:
    name = "BaseEngine"

    def __init__(self):
        self.signer = TokenSigner()

    def get_webhook_url(self):
        return "{}://{}{}?token={}".format(
            "http" if getattr(settings, "APP_MODE", False) == "DEV" else "https",
            get_current_site(None).domain,
            reverse("virus_scan:webhook"),
            urllib.parse.quote(self.signer.sign(self.name)),
        )

    def send_scan(self, this_file, filename):
        raise NotImplementedError(f"Provide 'send' in {self.__class__.__name__}")

    def receive_scan(self, engine_id):
        raise NotImplementedError(
            f"Provide 'receive_scan' in {self.__class__.__name__}"
        )

    def get_result_url(self, engine_id):
        raise NotImplementedError(
            f"Provide 'get_result_url' in {self.__class__.__name__}"
        )
