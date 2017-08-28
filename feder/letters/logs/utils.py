from feder.letters.logs.client import EmailLabsClient
from feder.letters.logs.settings import EMAILLABS_APP_KEY, EMAILLABS_SECRET_KEY


def get_emaillabs_client(**kwargs):
    return EmailLabsClient(EMAILLABS_APP_KEY, EMAILLABS_SECRET_KEY, **kwargs)
