# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("monitorings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth", "0006_require_contenttypes_0002"),
    ]

    operations = [
        migrations.AddField(
            model_name="monitoringuserobjectpermission",
            name="user",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="monitoringgroupobjectpermission",
            name="content_object",
            field=models.ForeignKey(
                to="monitorings.Monitoring", on_delete=django.db.models.deletion.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="monitoringgroupobjectpermission",
            name="group",
            field=models.ForeignKey(
                to="auth.Group", on_delete=django.db.models.deletion.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="monitoringgroupobjectpermission",
            name="permission",
            field=models.ForeignKey(
                to="auth.Permission", on_delete=django.db.models.deletion.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="monitoring",
            name="user",
            field=models.ForeignKey(
                verbose_name="User",
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="monitoringuserobjectpermission",
            unique_together={("user", "permission", "content_object")},
        ),
        migrations.AlterUniqueTogether(
            name="monitoringgroupobjectpermission",
            unique_together={("group", "permission", "content_object")},
        ),
    ]
