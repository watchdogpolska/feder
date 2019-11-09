from collections import OrderedDict

import requests
from six.moves.urllib.parse import urljoin


class EmailLabsClient:
    API_URI = "https://api.emaillabs.net.pl/api/"

    def __init__(self, api_key, secret_key, session=None, per_page=500):
        self.api_key = api_key
        self.secret_key = secret_key
        self.s = session or requests.Session()
        self.s.auth = (api_key, secret_key)
        self.per_page = per_page

    def get_emails(self, **kwargs):
        url = urljoin(self.API_URI, "emails")
        kwargs["sort"] = kwargs.get("sort", "created_at")
        kwargs["limit"] = kwargs.get("limit", self.per_page)
        response = self.s.get(url, params=OrderedDict(sorted(kwargs.items())))
        response.raise_for_status()
        return response.json()["data"]

    def get_emails_iter(self):
        offset = 0
        item = None

        while (item is None or len(item) == self.per_page) and offset < 500 * 25:
            item = self.get_emails(offset=offset)
            yield from item
            offset += self.per_page
