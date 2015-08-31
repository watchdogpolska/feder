# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0012_monitoring_notify_alert'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitoring',
            name='notify_alert',
            field=models.BooleanField(default=True, help_text='Notify about new alerts person who can view alerts', verbose_name='Notify about alerts'),
        ),
    ]
