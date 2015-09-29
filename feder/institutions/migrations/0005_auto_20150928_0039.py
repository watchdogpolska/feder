# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0004_auto_20150811_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='address',
            field=models.EmailField(help_text='E-mail address used to contact with institutions', max_length=254, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(to='institutions.Tag', null=True, verbose_name='Tag', blank=True),
        ),
    ]
