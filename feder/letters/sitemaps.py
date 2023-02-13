from django.contrib.sitemaps import Sitemap

from .models import Letter


class LetterSitemap(Sitemap):
    limit = 500

    def items(self):
        return Letter.objects.all().exclude_spam()

    def lastmod(self, obj):
        return obj.modified
