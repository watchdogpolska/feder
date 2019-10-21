# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import jsonfield.fields
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questionaries", "0001_initial"),
        ("cases", "0003_case_monitoring"),
    ]

    operations = [
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("blob", jsonfield.fields.JSONField()),
            ],
            options={"verbose_name": "Answer", "verbose_name_plural": "Answers"},
        ),
        migrations.CreateModel(
            name="Survey",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        verbose_name="created",
                        editable=False,
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        verbose_name="modified",
                        editable=False,
                    ),
                ),
                (
                    "credibility",
                    models.PositiveIntegerField(default=0, verbose_name="Credibility"),
                ),
            ],
            options={
                "ordering": ["task", "credibility", "created"],
                "verbose_name": "Survey",
                "verbose_name_plural": "Surveys",
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        verbose_name="created",
                        editable=False,
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        verbose_name="modified",
                        editable=False,
                    ),
                ),
                ("name", models.CharField(max_length=75, verbose_name="Name")),
                (
                    "survey_required",
                    models.SmallIntegerField(
                        default=2,
                        help_text="Define how much answers do you need to mark tasks as done\n or count progress",
                        verbose_name="Required survey count",
                    ),
                ),
                (
                    "survey_done",
                    models.SmallIntegerField(
                        default=0, verbose_name="Done survey count"
                    ),
                ),
                (
                    "case",
                    models.ForeignKey(
                        verbose_name="Case",
                        to="cases.Case",
                        on_delete=django.db.models.deletion.CASCADE,
                    ),
                ),
                (
                    "questionary",
                    models.ForeignKey(
                        verbose_name="Questionary",
                        to="questionaries.Questionary",
                        on_delete=django.db.models.deletion.CASCADE,
                        help_text="Questionary to fill by user as task",
                    ),
                ),
            ],
            options={
                "ordering": ["created"],
                "verbose_name": "Task",
                "verbose_name_plural": "Tasks",
            },
        ),
        migrations.AddField(
            model_name="survey",
            name="task",
            field=models.ForeignKey(
                to="tasks.Task", on_delete=django.db.models.deletion.CASCADE
            ),
        ),
    ]
