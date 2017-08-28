from six.moves.urllib.parse import urljoin
import requests
from requests import ConnectionError


class EmailLabsClient(object):
    API_URI = 'https://api.emaillabs.net.pl/api/'

    def __init__(self, api_key, secret_key, session=None, per_page=500):
        self.api_key = api_key
        self.secret_key = secret_key
        self.s = session or requests.Session()
        self.s.auth = (api_key, secret_key)
        self.per_page = per_page

    def assert_status_code(self, response, msg=None, status_code=200):
        msg = msg or "Unable to visit {}. Excepted status code is {}. " \
                     "Received {} instead".format(response.request.url,
                                                  status_code,
                                                  response.status_code)
        if response.status_code != status_code:
            raise ConnectionError(msg)

    def assert_not_unauthorized(self, response, msg=None):
        msg = msg or "Unable to authorize request to {}. Verify credentials.".format(response.request.url)
        if response.status_code == 401:
            raise ConnectionError(msg)

    def get_emails(self, **kwargs):
        url = urljoin(self.API_URI, 'emails')
        kwargs['sort'] = kwargs.get('sort', 'created_at')
        kwargs['limit'] = kwargs.get('limit', self.per_page)
        response = self.s.get(url, params=kwargs)
        self.assert_not_unauthorized(response)
        self.assert_status_code(response)
        return response.json()['data']

    def get_emails_iter(self):
        offset = 0
        item = None

        while (item is None or len(item) == self.per_page) and offset < 500 * 25:
            item = self.get_emails(offset=offset)
            for row in item:
                yield row
            offset += self.per_page
