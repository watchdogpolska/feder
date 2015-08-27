from functools import partial

from slugify import slugify

ascii_slugify = partial(slugify, only_ascii=True)
