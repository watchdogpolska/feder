# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teryt', '0006_add_mptt'),
        ('institutions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JST',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('teryt.jednostkaadministracyjna',),
        ),
        migrations.AlterField(
            model_name='email',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='jst',
            field=models.ForeignKey(to='institutions.JST'),
        ),
    ]
