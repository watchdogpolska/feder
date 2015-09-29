# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0009_auto_20150820_2309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monitoring',
            options={'ordering': ['created'], 'verbose_name': 'Monitoring', 'verbose_name_plural': 'Monitoring', 'permissions': (('add_questionary', 'Add questionary'), ('change_questionary', 'Change questionary'), ('delete_questionary', 'Delete questionary'), ('add_case', 'Add case'), ('change_case', 'Change case'), ('delete_case', 'Delete case'), ('add_task', 'Add task'), ('change_task', 'Change task'), ('delete_task', 'Delete task'), ('add_letter', 'Add letter'), ('reply', 'Reply'), ('change_letter', 'Change task'), ('delete_letter', 'Delete letter'))},
        ),
    ]
