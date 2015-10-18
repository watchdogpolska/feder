# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_auto_20150903_0106'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='survey',
            options={'ordering': ['task', 'credibility', 'created'], 'verbose_name': 'Survey', 'verbose_name_plural': 'Surveys'},
        ),
        migrations.AlterField(
            model_name='task',
            name='survey_required',
            field=models.SmallIntegerField(default=2, help_text='Define how much answers do you need to mark tasks as done\n or count progress', verbose_name='Required survey count'),
        ),
    ]
