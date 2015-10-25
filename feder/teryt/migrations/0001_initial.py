# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teryt_tree', '0005_auto_20150816_0342'),
    ]

    operations = [
        migrations.CreateModel(
            name='JST',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('teryt_tree.jednostkaadministracyjna',),
        ),
    ]
