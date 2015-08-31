# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0003_auto_20150831_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='author',
            field=models.ForeignKey(related_name='alert_author', verbose_name='Author', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
