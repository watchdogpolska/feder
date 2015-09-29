# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0005_auto_20150903_0139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alert',
            name='solver',
        ),
    ]
