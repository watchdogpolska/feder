# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('questionaries', '0003_question_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='blob',
            field=jsonfield.fields.JSONField(verbose_name='Technical definition'),
        ),
        migrations.AlterField(
            model_name='question',
            name='genre',
            field=models.CharField(max_length=25, verbose_name='Genre'),
        ),
        migrations.AlterField(
            model_name='question',
            name='position',
            field=models.SmallIntegerField(default=0, verbose_name='Position'),
        ),
        migrations.AlterField(
            model_name='question',
            name='questionary',
            field=models.ForeignKey(verbose_name='Questionary', to='questionaries.Questionary'),
        ),
        migrations.AlterField(
            model_name='questionary',
            name='lock',
            field=models.BooleanField(default=False, help_text='Prevent of edit question to protect against destruction the data set', verbose_name='Lock of edition'),
        ),
        migrations.AlterField(
            model_name='questionary',
            name='monitoring',
            field=models.ForeignKey(verbose_name='Monitoring', to='monitorings.Monitoring'),
        ),
        migrations.AlterField(
            model_name='questionary',
            name='title',
            field=models.CharField(max_length=250, verbose_name='Title'),
        ),
    ]
