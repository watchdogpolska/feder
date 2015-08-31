# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponseServerError
from django.template import Context, loader
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^', include('feder.main.urls', namespace="main")),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name="about"),

    # Django Admin
    url(r'^admin/', include(admin.site.urls)),

    # User management
    url(r'^users/', include("feder.users.urls", namespace="users")),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^institutions/', include('feder.institutions.urls', namespace="institutions")),
    url(r'^monitorings/', include('feder.monitorings.urls', namespace="monitorings")),
    url(r'^cases/', include('feder.cases.urls', namespace="cases")),
    url(r'^tasks/', include('feder.tasks.urls', namespace="tasks")),
    url(r'^questionaries/', include('feder.questionaries.urls', namespace="questionaries")),
    url(r'^alerts/', include('feder.alerts.urls', namespace="alerts")),
    url(r'^letters/', include('feder.letters.urls', namespace="letters")),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^teryt/', include('feder.teryt.urls', namespace="teryt")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', 'django.views.defaults.bad_request'),
        url(r'^403/$', 'django.views.defaults.permission_denied'),
        url(r'^404/$', 'django.views.defaults.page_not_found'),
        url(r'^500/$', 'django.views.defaults.server_error'),
    ]


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """

    t = loader.get_template('500.html')
    return HttpResponseServerError(t.render(Context({
        'request': request,
    })))
