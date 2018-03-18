# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(_(r'^$'), views.TaskListView.as_view(),
        name="list"),
    url(_(r'^~create-(?P<case>[\d]+)$'), views.TaskCreateView.as_view(),
        name="create"),
    url(_(r'^(?P<pk>[\d]+)$'), views.TaskDetailView.as_view(),
        name="details"),
    url(_(r'^(?P<pk>[\d]+)/~update$'), views.TaskUpdateView.as_view(),
        name="update"),
    url(_(r'^(?P<pk>[\d]+)/~delete$'), views.TaskDeleteView.as_view(),
        name="delete"),
    url(_(r'^(?P<pk>[\d]+)/~survey_list$'), views.TaskSurveyView.as_view(),
        name="survey"),
    url(_(r'^(?P<pk>[\d]+)/~fill_survey$'), views.SurveyFillView.as_view(),
        name="fill_survey"),
    url(_(r'^(?P<task_id>[\d]+)/~delete_survey$'), views.SurveyDeleteView.as_view(),
        name="delete_survey"),
    url(_(r'^(?P<task_id>[\d]+)/~select-up-(?P<pk>[\d]+)$'),
        views.SurveySelectView.as_view(direction='up'),
        name="select_up_survey"),
    url(_(r'^(?P<task_id>[\d]+)/~select-down-(?P<pk>[\d]+)$'),
        views.SurveySelectView.as_view(direction='down'),
        name="select_down_survey"),
]

app_name = 'feder.tasks'
