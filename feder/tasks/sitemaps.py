from django.contrib.sitemaps import Sitemap
from .models import Task


class TaskSitemap(Sitemap):
    def items(self):
        return Task.objects.all()

    def lastmod(self, obj):
        return obj.modified
