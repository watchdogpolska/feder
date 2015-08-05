# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questionaries', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='questionary',
            field=models.ForeignKey(default=1, to='questionaries.Questionary'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='questionary',
            name='lock',
            field=models.BooleanField(default=False),
        ),
    ]
