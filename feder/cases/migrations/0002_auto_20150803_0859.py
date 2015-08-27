# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0002_auto_20150803_0735'),
        ('institutions', '0002_auto_20150803_0643'),
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='institution',
            field=models.ForeignKey(default=1, to='institutions.Institution'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='monitoring',
            field=models.ForeignKey(default=1, to='monitorings.Monitoring'),
            preserve_default=False,
        ),
    ]
