from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from .models import Monitoring
from .views import MonitoringDetailView


class MonitoringSitemap(Sitemap):
    def items(self):
        return Monitoring.objects.all()

    def lastmod(self, obj):
        return obj.modified


class MonitoringPagesSitemap(Sitemap):
    paginate_by = MonitoringDetailView.paginate_by

    def ceildiv(self, a, b):
        return -(-a // b)

    def items(self):
        items = []
        for obj in Monitoring.objects.with_case_count().all():
            for page in range(0, self.ceildiv(obj.case_count, self.paginate_by) + 1):
                items.append((obj, page + 1))
        return items

    def location(self, item):
        obj, page = item
        return reverse('monitorings:details', kwargs={'slug': obj.slug,
                                                      'page': page})
