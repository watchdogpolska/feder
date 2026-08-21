from functools import partial

from django.utils.text import slugify

unicode_slugify = partial(slugify, allow_unicode=True)
