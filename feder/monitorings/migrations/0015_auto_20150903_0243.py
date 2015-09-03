# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0014_auto_20150902_0228'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monitoring',
            options={'ordering': ['created'], 'verbose_name': 'Monitoring', 'verbose_name_plural': 'Monitoring', 'permissions': (('add_questionary', 'Can add questionary'), ('change_questionary', 'Can change questionary'), ('delete_questionary', 'Can delete questionary'), ('add_case', 'Can add case'), ('change_case', 'Can change case'), ('delete_case', 'Can delete case'), ('add_task', 'Can add task'), ('change_task', 'Can change task'), ('delete_task', 'Can delete task'), ('add_letter', 'Can add letter'), ('reply', 'Can reply'), ('change_letter', 'Can change task'), ('delete_letter', 'Can delete letter'), ('view_alert', 'Can view alert'), ('change_alert', 'Can change alert'), ('delete_alert', 'Can delete alert'), ('manage_perm', 'Can manage perms'), ('select_survey', 'Can select answer'))},
        ),
    ]
