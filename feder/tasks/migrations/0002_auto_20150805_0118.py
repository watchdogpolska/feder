# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionary',
            name='monitoring',
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='questionaries.Question'),
        ),
        migrations.AlterField(
            model_name='task',
            name='questionary',
            field=models.ForeignKey(to='questionaries.Questionary'),
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Questionary',
        ),
    ]
