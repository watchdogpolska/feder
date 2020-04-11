import os
from django.conf import settings

ELASTICSEARCH_URL = settings.ELASTICSEARCH_URL
APACHE_TIKA_URL = settings.APACHE_TIKA_URL

os.environ["TIKA_CLIENT_ONLY"] = "true"
os.environ["TIKA_SERVER_ENDPOINT"] = settings.APACHE_TIKA_URL
