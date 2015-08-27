# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20150805_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='task',
            field=models.ForeignKey(default=1, to='tasks.Task'),
            preserve_default=False,
        ),
    ]
