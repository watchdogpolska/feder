# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from .views import questionaries, questions, utils

questionaries_urlpatterns = [
    url(_(r"^$"), questionaries.QuestionaryListView.as_view(), name="list"),
    url(
        _(r"^~create-(?P<monitoring>[\d]+)$"),
        questionaries.QuestionaryCreateView.as_view(),
        name="create",
    ),
    url(
        _(r"^(?P<pk>[\d]+)$"),
        questionaries.QuestionaryDetailView.as_view(),
        name="details",
    ),
    url(
        _(r"^(?P<pk>[\d]+)/~update$"),
        questionaries.QuestionaryUpdateView.as_view(),
        name="update",
    ),
    url(
        _(r"^(?P<pk>[\d]+)/~delete$"),
        questionaries.QuestionaryDeleteView.as_view(),
        name="delete",
    ),
    url(
        _(r"^(?P<pk>[\d]+)/~tasks$"), utils.TaskMultiCreateView.as_view(), name="tasks"
    ),
    url(_(r"^(?P<pk>[\d]+)/~export$"), utils.SurveyCSVView.as_view(), name="export"),
]

question_urlpatterns = [
    url(
        _(r"^(?P<pk>[\d]+)/~question-create$"),
        questions.QuestionCreateView.as_view(),
        name="question_create",
    ),
    url(
        _(r"^question-(?P<pk>[\d]+)/~up$"),
        questions.QuestionMoveView.as_view(direction="up"),
        name="question_up",
    ),
    url(
        _(r"^question-(?P<pk>[\d]+)/~down$"),
        questions.QuestionMoveView.as_view(direction="down"),
        name="question_down",
    ),
    url(
        _(r"^question-(?P<pk>[\d]+)/~update$"),
        questions.QuestionUpdateView.as_view(),
        name="question_update",
    ),
    url(
        _(r"^question-(?P<pk>[\d]+)/~delete$"),
        questions.QuestionDeleteView.as_view(),
        name="question_delete",
    ),
]

urlpatterns = questionaries_urlpatterns + question_urlpatterns

app_name = "feder.questionaries"
