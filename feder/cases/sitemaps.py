from django.contrib.sitemaps import Sitemap

from .models import Case


class CaseSitemap(Sitemap):
    def items(self):
        return Case.objects.all()
