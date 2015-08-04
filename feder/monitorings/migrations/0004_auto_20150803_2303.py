# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0003_auto_20150803_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitoring',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from=b'name', unique=True, verbose_name='Slug'),
        ),
    ]
