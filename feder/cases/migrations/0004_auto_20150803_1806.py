# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0003_auto_20150803_0937'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachment',
            name='record',
        ),
        migrations.RemoveField(
            model_name='letter',
            name='author_institution',
        ),
        migrations.RemoveField(
            model_name='letter',
            name='author_user',
        ),
        migrations.DeleteModel(
            name='Attachment',
        ),
        migrations.DeleteModel(
            name='Letter',
        ),
    ]
