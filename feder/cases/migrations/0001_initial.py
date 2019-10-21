# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import autoslug.fields
import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Case",
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
                ("name", models.CharField(max_length=50, verbose_name="Name")),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        editable=False,
                        populate_from=b"name",
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                ("email", models.CharField(unique=True, max_length=75, db_index=True)),
            ],
            options={
                "ordering": ["created"],
                "verbose_name": "Case",
                "verbose_name_plural": "Case",
            },
        )
    ]
