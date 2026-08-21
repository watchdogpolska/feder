from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import index, sitemap
from django.urls import include, path, re_path
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rest_framework import routers

from feder.cases.sitemaps import CaseSitemap
from feder.cases.viewsets import CaseReportViewSet, CaseViewSet
from feder.institutions.sitemaps import InstitutionSitemap, TagSitemap
from feder.institutions.viewsets import InstitutionViewSet, TagViewSet
from feder.letters.sitemaps import LetterSitemap
from feder.main.sitemaps import StaticSitemap
from feder.monitorings.sitemaps import MonitoringPagesSitemap, MonitoringSitemap
from feder.monitorings.views import MultiCaseTagManagement
from feder.monitorings.viewsets import MonitoringViewSet
from feder.records.viewsets import RecordViewSet
from feder.teryt.sitemaps import JSTSitemap
from feder.teryt.views import TerytViewSet

from . import views

handler500 = views.handler500  # required to have exception id

router = routers.DefaultRouter()
router.register(r"institutions", InstitutionViewSet, basename="institution")
router.register(r"tags", TagViewSet)
router.register(r"teryt", TerytViewSet)
router.register(r"records", RecordViewSet)
router.register(r"cases/report", CaseReportViewSet, basename="case-report")
router.register(r"cases", CaseViewSet)
router.register(r"monitorings", MonitoringViewSet)

urlpatterns = [path(_(""), views.HomeView.as_view(), name="home")]

urlpatterns += [
    path(
        _("about/"),
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin
    re_path(r"^admin/", admin.site.urls),
    # User management
    path(_("users/"), include("feder.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path(
        _("institutions/"),
        include("feder.institutions.urls", namespace="institutions"),
    ),
    path(_("monitorings/"), include("feder.monitorings.urls", namespace="monitorings")),
    path(_("cases/"), include("feder.cases.urls", namespace="cases")),
    path(_("cases/tags/"), include("feder.cases_tags.urls", namespace="cases_tags")),
    path(_("alerts/"), include("feder.alerts.urls", namespace="alerts")),
    path(_("letters/"), include("feder.letters.urls", namespace="letters")),
    path(_("teryt/"), include("feder.teryt.urls", namespace="teryt")),
    path(_("letters/logs/"), include("feder.letters.logs.urls", namespace="logs")),
    path(_("parcels/"), include("feder.parcels.urls", namespace="parcels")),
    path(_("virus_scan/"), include("feder.virus_scan.urls", namespace="virus_scan")),
    path(
        "api/monitorings/<int:monitoring_pk>/case-tags/update/",
        MultiCaseTagManagement.as_view(),
        name="monitoring-case-tags-update",
    ),
    path("api/", include(router.urls)),
]

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [path("rosetta/", include("rosetta.urls"))]

if "tinymce" in settings.INSTALLED_APPS:
    urlpatterns += [path("tinymce/", include("tinymce.urls"))]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

sitemaps = {
    "cases": CaseSitemap,
    "institutions": InstitutionSitemap,
    "institutions_tags": TagSitemap,
    "letters": LetterSitemap,
    "main": StaticSitemap,
    "monitorings": MonitoringSitemap,
    "monitorings_pages": MonitoringPagesSitemap,
    "teryt": JSTSitemap,
}

urlpatterns += [
    path("sitemap.xml", index, {"sitemaps": sitemaps, "sitemap_url_name": "sitemaps"}),
    path(
        "sitemap-<path:section>.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemaps",
    ),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
