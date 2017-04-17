from django.contrib.sitemaps import Sitemap

from .models import Questionary


class QuestionarySitemap(Sitemap):
    def items(self):
        return Questionary.objects.all()

    def lastmod(self, obj):
        return obj.modified
