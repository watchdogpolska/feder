# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import jsonfield.fields
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0004_auto_20150803_2303'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('position', models.SmallIntegerField()),
                ('blob', jsonfield.fields.JSONField()),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
            },
        ),
        migrations.CreateModel(
            name='Questionary',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(
                    default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(
                    default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('title', models.CharField(max_length=250)),
                ('lock', models.BooleanField()),
                ('monitoring', models.ForeignKey(to='monitorings.Monitoring')),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'Questionary',
                'verbose_name_plural': 'Questionaries',
            },
        ),
    ]
