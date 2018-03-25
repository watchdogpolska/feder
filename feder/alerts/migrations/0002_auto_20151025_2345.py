# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('monitorings', '0001_initial'),
        ('alerts', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='author',
            field=models.ForeignKey(related_name='alert_author', verbose_name='Author',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to=settings.AUTH_USER_MODEL,
                                    null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='monitoring',
            field=models.ForeignKey(verbose_name='Monitoring',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='monitorings.Monitoring'),
        ),
    ]
