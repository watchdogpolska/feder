from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import index, sitemap
from django.http import HttpResponseServerError
from django.template import loader
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from rest_framework import routers
from teryt_tree.rest_framework_ext.viewsets import JednostkaAdministracyjnaViewSet

from feder.cases.sitemaps import CaseSitemap
from feder.cases.viewsets import CaseViewSet
from feder.institutions.sitemaps import InstitutionSitemap, TagSitemap
from feder.institutions.viewsets import InstitutionViewSet, TagViewSet
from feder.letters.sitemaps import LetterSitemap
from feder.main.sitemaps import StaticSitemap
from feder.monitorings.sitemaps import MonitoringPagesSitemap, MonitoringSitemap
from feder.monitorings.viewsets import MonitoringViewSet
from feder.questionaries.sitemaps import QuestionarySitemap
from feder.records.viewsets import RecordViewSet
from feder.tasks.sitemaps import TaskSitemap
from feder.teryt.sitemaps import JSTSitemap
from . import views

router = routers.DefaultRouter()
router.register(r"institutions", InstitutionViewSet)
router.register(r"tags", TagViewSet)
router.register(r"teryt", JednostkaAdministracyjnaViewSet)
router.register(r"records", RecordViewSet)
router.register(r"cases", CaseViewSet)
router.register(r"monitoring", MonitoringViewSet)

urlpatterns = [url(_(r"^$"), views.HomeView.as_view(), name="home")]

urlpatterns += [
    url(
        _(r"^about/$"),
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin
    url(r"^admin/", admin.site.urls),
    # User management
    url(_(r"^users/"), include("feder.users.urls", namespace="users")),
    url(r"^accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    url(
        _(r"^institutions/"),
        include("feder.institutions.urls", namespace="institutions"),
    ),
    url(
        _(r"^monitorings/"), include("feder.monitorings.urls", namespace="monitorings")
    ),
    url(_(r"^cases/"), include("feder.cases.urls", namespace="cases")),
    url(_(r"^tasks/"), include("feder.tasks.urls", namespace="tasks")),
    url(
        _(r"^questionaries/"),
        include("feder.questionaries.urls", namespace="questionaries"),
    ),
    url(_(r"^alerts/"), include("feder.alerts.urls", namespace="alerts")),
    url(_(r"^letters/"), include("feder.letters.urls", namespace="letters")),
    url(_(r"^teryt/"), include("feder.teryt.urls", namespace="teryt")),
    url(_(r"^letters/logs/"), include("feder.letters.logs.urls", namespace="logs")),
    url(_(r"^parcels/"), include("feder.parcels.urls", namespace="parcels")),
    url(r"^api/", include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

sitemaps = {
    "cases": CaseSitemap,
    "institutions": InstitutionSitemap,
    "institutions_tags": TagSitemap,
    "letters": LetterSitemap,
    "main": StaticSitemap,
    "monitorings": MonitoringSitemap,
    "monitorings_pages": MonitoringPagesSitemap,
    "questionaries": QuestionarySitemap,
    "tasks": TaskSitemap,
    "teryt": JSTSitemap,
}

urlpatterns += [
    url(
        r"^sitemap\.xml$", index, {"sitemaps": sitemaps, "sitemap_url_name": "sitemaps"}
    ),
    url(
        r"^sitemap-(?P<section>.+)\.xml$",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemaps",
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """

    t = loader.get_template("500.html")
    return HttpResponseServerError(t.render({"request": request}))
