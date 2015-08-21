# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0007_auto_20150820_2252'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monitoring',
            options={'ordering': ['created'], 'verbose_name': 'Monitoring', 'verbose_name_plural': 'Monitoring', 'permissions': (('change_monitoring', 'Change monitoring'), ('delete_monitoring', 'Delete monitoring'), ('add_questionary', 'Add questionary'), ('change_questionary', 'Change questionary'), ('delete_questionary', 'Delete questionary'), ('add_case', 'Add case'), ('change_case', 'Change case'), ('delete_case', 'Delete case'), ('add_task', 'Add task'), ('change_task', 'Change task'), ('delete_task', 'Delete task'))},
        ),
    ]
