# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0005_auto_20150816_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='eml',
            field=models.FileField(upload_to=b'messages/%Y/%m/%d', null=True, verbose_name='File'),
        ),
    ]
