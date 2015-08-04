# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('teryt', '0003_auto_20150803_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jednostkaadministracyjna',
            name='slug',
            field=autoslug.fields.AutoSlugField(populate_from=b'name', unique=True, editable=False),
        ),
    ]
