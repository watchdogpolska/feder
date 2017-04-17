# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cases', '0001_initial'),
        ('institutions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='institution',
            field=models.ForeignKey(verbose_name='Institution', to='institutions.Institution'),
        ),
    ]
