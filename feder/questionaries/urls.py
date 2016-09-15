# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from .views import questions, questionaries, utils

questionaries_urlpatterns = [
    url(r'^$', questionaries.QuestionaryListView.as_view(),
        name="list"),
    url(r'^~create-(?P<monitoring>[\d]+)$', questionaries.QuestionaryCreateView.as_view(),
        name="create"),
    url(r'^questionary-(?P<pk>[\d]+)$', questionaries.QuestionaryDetailView.as_view(),
        name="details"),
    url(r'^questionary-(?P<pk>[\d]+)/~update$', questionaries.QuestionaryUpdateView.as_view(),
        name="update"),
    url(r'^questionary-(?P<pk>[\d]+)/~delete$', questionaries.QuestionaryDeleteView.as_view(),
        name="delete"),
    url(r'^questionary-(?P<pk>[\d]+)/~tasks$', utils.TaskMultiCreateView.as_view(),
        name="tasks"),
    url(r'^questionary-(?P<pk>[\d]+)/~export$', utils.save_survey_as_csv,
        name="export"),
]

question_urlpatterns = [
    url(r'^questionary-(?P<pk>[\d]+)/~question-create$', questions.QuestionCreateView.as_view(),
        name="question_create"),
    url(r'^question-(?P<pk>[\d]+)/~up$', questions.QuestionMoveView.as_view(direction='up'),
        name="question_up"),
    url(r'^question-(?P<pk>[\d]+)/~down$', questions.QuestionMoveView.as_view(direction='down'),
        name="question_down"),
    url(r'^question-(?P<pk>[\d]+)/~update$', questions.QuestionUpdateView.as_view(),
        name="question_update"),
    url(r'^question-(?P<pk>[\d]+)/~delete$', questions.QuestionDeleteView.as_view(),
        name="question_delete"),
]

urlpatterns = questionaries_urlpatterns + question_urlpatterns
