# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monitoring',
            options={'ordering': ['created_on'], 'verbose_name': 'Monitoring', 'verbose_name_plural': 'Monitoring'},
        ),
        migrations.AddField(
            model_name='monitoring',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 3, 7, 35, 38, 976354, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='monitoring',
            name='modified_on',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 3, 7, 35, 47, 338599, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
