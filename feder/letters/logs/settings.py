from django.conf import settings

EMAILLABS_APP_KEY = getattr(settings, 'EMAILLABS_APP_KEY')

EMAILLABS_SECRET_KEY = getattr(settings, 'EMAILLABS_SECRET_KEY')
