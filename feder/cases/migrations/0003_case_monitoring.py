# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0001_initial'),
        ('cases', '0002_case_institution'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='monitoring',
            field=models.ForeignKey(verbose_name='Monitoring', to='monitorings.Monitoring'),
        ),
    ]
