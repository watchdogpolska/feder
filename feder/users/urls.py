# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    url(regex=_(r'^$'), view=views.UserListView.as_view(), name='list'),

    # URL pattern for the UserRedirectView
    url(regex=_(r'^~redirect/$'), view=views.UserRedirectView.as_view(), name='redirect'),

    # URL pattern for the UserDetailView
    url(regex=_(r'^(?P<username>[\w.@+-]+)/$'), view=views.UserDetailView.as_view(), name='detail'),

    # URL pattern for the UserUpdateView
    url(regex=_(r'^~update/$'), view=views.UserUpdateView.as_view(), name='update'),

    # URL pattern for the UserUpdateView
    url(regex=_(r'^~autocomplete$'), view=views.UserAutocomplete.as_view(), name='autocomplete'),

]

app_name = 'feder.users'
