# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
   url(r'^$', views.TaskListView.as_view(),
    name="list"),
   url(r'^~create$', views.TaskCreateView.as_view(),
    name="create"),
   url(r'^task-(?P<pk>[\d]+)$', views.TaskDetailView.as_view(),
    name="details"),
   url(r'^task-(?P<pk>[\d]+)/~update$', views.TaskUpdateView.as_view(),
    name="update"),
   url(r'^task-(?P<pk>[\d]+)/~delete$', views.TaskDeleteView.as_view(),
    name="delete"),
   url(r'^task-(?P<pk>[\d]+)/~survey_list$', views.TaskSurveyView.as_view(),
    name="survey"),
   url(r'^task-(?P<pk>[\d]+)/~fill_survey$', views.fill_survey,
    name="fill_survey"),
   url(r'^task-(?P<task_id>[\d]+)/~delete_survey$', views.SurveyDeleteView.as_view(),
    name="delete_survey"),
]
