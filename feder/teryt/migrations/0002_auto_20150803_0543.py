# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teryt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='level',
            field=models.IntegerField(db_index=True, choices=[(1, b'wojew\xc3\xb3dztwo'), (2, b'powiat'), (3, b'gmina')]),
        ),
    ]
