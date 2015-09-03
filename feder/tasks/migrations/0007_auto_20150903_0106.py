# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_auto_20150820_1359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='survey',
            options={'ordering': ['credibility'], 'verbose_name': 'Survey', 'verbose_name_plural': 'Surveys'},
        ),
        migrations.AddField(
            model_name='survey',
            name='credibility',
            field=models.PositiveIntegerField(default=0, verbose_name='Credibility'),
        ),
    ]
