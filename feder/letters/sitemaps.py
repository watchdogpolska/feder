from django.contrib.sitemaps import Sitemap

from .models import Letter


class LetterSitemap(Sitemap):
    def items(self):
        return Letter.objects.all()

    def lastmod(self, obj):
        return obj.modified
