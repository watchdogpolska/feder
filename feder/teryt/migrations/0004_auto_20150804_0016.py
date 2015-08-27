# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models


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
