from django.contrib.sitemaps import Sitemap
from guardian.shortcuts import get_anonymous_user

from .models import Case


class CaseSitemap(Sitemap):
    def items(self):
        return Case.objects.all().for_user(get_anonymous_user())
