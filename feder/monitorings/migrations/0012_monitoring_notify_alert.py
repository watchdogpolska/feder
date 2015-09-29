# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0011_auto_20150831_0233'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoring',
            name='notify_alert',
            field=models.BooleanField(default=True, help_text='Notify about new alerts person who can change monitoring', verbose_name='Notify about alerts'),
        ),
    ]
