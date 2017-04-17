from django.contrib.sitemaps import Sitemap

from .models import JST


class JSTSitemap(Sitemap):
    def items(self):
        return JST.objects.all()
