# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('alerts', '0004_auto_20150831_0330'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
