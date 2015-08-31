# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='solver',
            field=models.ForeignKey(related_name='alert_solver', verbose_name='User', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
