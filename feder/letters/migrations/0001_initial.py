# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("institutions", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Attachment",
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
                    "attachment",
                    models.FileField(
                        upload_to=b"letters/%Y/%m/%d", verbose_name="File"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "verbose_name": "Attachment",
                "verbose_name_plural": "Attachments",
            },
        ),
        migrations.CreateModel(
            name="Letter",
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
                ("title", models.CharField(max_length=50, verbose_name="Title")),
                ("body", models.TextField(verbose_name="Text")),
                ("quote", models.TextField(verbose_name="Quote", blank=True)),
                (
                    "email",
                    models.EmailField(max_length=50, verbose_name="E-mail", blank=True),
                ),
                (
                    "eml",
                    models.FileField(
                        upload_to=b"messages/%Y/%m/%d", null=True, verbose_name="File"
                    ),
                ),
                (
                    "author_institution",
                    models.ForeignKey(
                        verbose_name="Author (if institution)",
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="institutions.Institution",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ["created"],
                "verbose_name": "Letter",
                "verbose_name_plural": "Letters",
                "permissions": (("can_filter_eml", "Can filter eml"),),
            },
        ),
    ]
