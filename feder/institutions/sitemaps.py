from django.contrib.sitemaps import Sitemap

from .models import Institution, Tag


class InstitutionSitemap(Sitemap):
    def items(self):
        return Institution.objects.all()


class TagSitemap(Sitemap):
    def items(self):
        return Tag.objects.used().all()
