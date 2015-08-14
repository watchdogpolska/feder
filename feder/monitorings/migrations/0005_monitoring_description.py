# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0004_auto_20150803_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoring',
            name='description',
            field=models.TextField(verbose_name='Description', blank=True),
        ),
    ]
