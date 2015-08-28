# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0007_letter_email'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='letter',
            options={'ordering': ['created'], 'verbose_name': 'Letter', 'verbose_name_plural': 'Letters', 'permissions': (('can_filter_eml', 'Can filter eml'),)},
        ),
    ]
