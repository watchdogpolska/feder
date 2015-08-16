# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_task_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='case',
            field=models.ForeignKey(verbose_name='Case', to='cases.Case'),
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(max_length=75, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='task',
            name='questionary',
            field=models.ForeignKey(verbose_name='Questionary', to='questionaries.Questionary', help_text='Questionary to fill by user as task'),
        ),
        migrations.AlterUniqueTogether(
            name='survey',
            unique_together=set([('task', 'user')]),
        ),
    ]
