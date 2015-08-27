# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionaries', '0002_auto_20150805_0127'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='genre',
            field=models.CharField(default='char', max_length=25),
            preserve_default=False,
        ),
    ]
