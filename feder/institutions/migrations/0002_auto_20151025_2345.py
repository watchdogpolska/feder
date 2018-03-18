# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('institutions', '0001_initial'),
        ('teryt', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='jst',
            field=models.ForeignKey(verbose_name='Unit of administrative division',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='teryt.JST'),
        ),
        migrations.AddField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(to='institutions.Tag', null=True, verbose_name='Tag', blank=True),
        ),
        migrations.AddField(
            model_name='email',
            name='institution',
            field=models.ForeignKey(verbose_name='Institution',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='institutions.Institution'),
        ),
    ]
