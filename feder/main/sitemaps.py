from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class StaticSitemap(Sitemap):
    def items(self):
        return ['home', ]

    def location(self, item):
        return reverse(item)
