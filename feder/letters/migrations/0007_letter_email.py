# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0006_letter_eml'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='email',
            field=models.EmailField(max_length=50, verbose_name='E-mail', blank=True),
        ),
    ]
