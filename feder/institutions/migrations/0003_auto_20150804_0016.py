# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0002_auto_20150803_0643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='slug',
            field=autoslug.fields.AutoSlugField(
                editable=False, populate_from=b'name', unique=True, verbose_name='Slug'),
        ),
    ]
