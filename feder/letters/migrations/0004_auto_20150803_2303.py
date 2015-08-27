# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0003_auto_20150803_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='letter',
            name='author_institution',
            field=models.ForeignKey(blank=True, to='institutions.Institution', null=True),
        ),
    ]
