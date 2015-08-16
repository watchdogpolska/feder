# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0005_auto_20150804_0016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='institution',
            field=models.ForeignKey(verbose_name='Institution', to='institutions.Institution'),
        ),
        migrations.AlterField(
            model_name='case',
            name='monitoring',
            field=models.ForeignKey(verbose_name='Monitoring', to='monitorings.Monitoring'),
        ),
    ]
