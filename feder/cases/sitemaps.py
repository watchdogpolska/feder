from django.contrib.sitemaps import Sitemap

from .models import Case
from guardian.shortcuts import get_anonymous_user


class CaseSitemap(Sitemap):
    def items(self):
        return Case.objects.all().for_user(get_anonymous_user())
