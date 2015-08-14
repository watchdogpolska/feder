# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_survey_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='name',
            field=models.CharField(default='xyz', max_length=75),
            preserve_default=False,
        ),
    ]
