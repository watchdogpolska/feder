# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0006_auto_20150816_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='email',
            field=models.CharField(max_length=75, null=True, db_index=True),
        ),
    ]
