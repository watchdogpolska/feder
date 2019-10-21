# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import jsonfield.fields
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("monitorings", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Question",
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
                    "position",
                    models.SmallIntegerField(default=0, verbose_name="Position"),
                ),
                ("genre", models.CharField(max_length=25, verbose_name="Genre")),
                (
                    "blob",
                    jsonfield.fields.JSONField(verbose_name="Technical definition"),
                ),
            ],
            options={
                "ordering": ["position"],
                "verbose_name": "Question",
                "verbose_name_plural": "Questions",
            },
        ),
        migrations.CreateModel(
            name="Questionary",
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
                ("title", models.CharField(max_length=250, verbose_name="Title")),
                (
                    "lock",
                    models.BooleanField(
                        default=False,
                        help_text="Prevent of edit question to protect against destruction the data set",
                        verbose_name="Lock of edition",
                    ),
                ),
                (
                    "monitoring",
                    models.ForeignKey(
                        verbose_name="Monitoring",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="monitorings.Monitoring",
                    ),
                ),
            ],
            options={
                "ordering": ["created"],
                "verbose_name": "Questionary",
                "verbose_name_plural": "Questionaries",
            },
        ),
        migrations.AddField(
            model_name="question",
            name="questionary",
            field=models.ForeignKey(
                verbose_name="Questionary",
                on_delete=django.db.models.deletion.CASCADE,
                to="questionaries.Questionary",
            ),
        ),
    ]
