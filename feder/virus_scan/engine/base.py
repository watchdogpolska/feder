import urllib.parse

from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from ..signer import TokenSigner


class BaseEngine:
    def __init__(self):
        self.signer = TokenSigner()

    def get_webhook_url(self):
        return "{}://{}{}?token={}".format(
            "https",
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
