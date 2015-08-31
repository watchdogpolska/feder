# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('monitorings', '0010_auto_20150829_0221'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('reason', models.TextField(verbose_name='Reason')),
                ('status', models.BooleanField(default=False, verbose_name='Status')),
                ('author', models.ForeignKey(related_name='alert_author', verbose_name='User', to=settings.AUTH_USER_MODEL)),
                ('monitoring', models.ForeignKey(verbose_name='Monitoring', to='monitorings.Monitoring')),
                ('solver', models.ForeignKey(related_name='alert_solver', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Alert',
                'verbose_name_plural': 'Alerts',
            },
        ),
    ]
