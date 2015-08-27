# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_auto_20150816_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='survey_done',
            field=models.SmallIntegerField(default=0, verbose_name='Done survey count'),
        ),
        migrations.AddField(
            model_name='task',
            name='survey_required',
            field=models.SmallIntegerField(default=2, verbose_name='Required survey count'),
        ),
    ]
