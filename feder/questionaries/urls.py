# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.QuestionaryListView.as_view(),
        name="list"),
    url(r'^~create-(?P<monitoring>[\d]+)$', views.QuestionaryCreateView.as_view(),
        name="create"),
    url(r'^questionary-(?P<pk>[\d]+)$', views.QuestionaryDetailView.as_view(),
        name="details"),
    url(r'^questionary-(?P<pk>[\d]+)/~update$', views.QuestionaryUpdateView.as_view(),
        name="update"),
    url(r'^questionary-(?P<pk>[\d]+)/~delete$', views.QuestionaryDeleteView.as_view(),
        name="delete"),
    url(r'^questionary-(?P<pk>[\d]+)/~tasks$', views.TaskMultiCreateView.as_view(),
        name="tasks"),
    url(r'^questionary-(?P<pk>[\d]+)/~question-create$', views.QuestionWizard.as_view(),
        name="question_create"),
    url(r'^question-(?P<pk>[\d]+)/~up$', views.QuestionMoveView.as_view(direction='up'),
        name="question_up"),
    url(r'^question-(?P<pk>[\d]+)/~down$', views.QuestionMoveView.as_view(direction='down'),
        name="question_down"),

]
