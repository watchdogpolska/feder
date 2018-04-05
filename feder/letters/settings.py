from django.conf import settings
from django.utils.module_loading import import_string

LETTER_SPAM_HOOK = getattr(settings, 'LETTER_SPAM_HOOK', 'feder.letters.utils.is_spam_check')

LETTER_SPAM_FUNC = import_string(LETTER_SPAM_HOOK)
