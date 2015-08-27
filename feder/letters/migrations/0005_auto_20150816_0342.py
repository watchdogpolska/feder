# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0004_auto_20150803_2303'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='letter',
            options={'ordering': ['created'], 'verbose_name': 'Letter', 'verbose_name_plural': 'Letters'},
        ),
        migrations.AlterField(
            model_name='letter',
            name='author_institution',
            field=models.ForeignKey(verbose_name='Author (if institution)', blank=True, to='institutions.Institution', null=True),
        ),
        migrations.AlterField(
            model_name='letter',
            name='author_user',
            field=models.ForeignKey(verbose_name='Author (if user)', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='letter',
            name='case',
            field=models.ForeignKey(verbose_name='Case', to='cases.Case'),
        ),
    ]
