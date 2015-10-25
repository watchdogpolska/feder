# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import autoslug.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monitoring',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'name', unique=True, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('notify_alert', models.BooleanField(default=True, help_text='Notify about new alerts person who can view alerts', verbose_name='Notify about alerts')),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'Monitoring',
                'verbose_name_plural': 'Monitoring',
                'permissions': (('add_questionary', 'Can add questionary'), ('change_questionary', 'Can change questionary'), ('delete_questionary', 'Can delete questionary'), ('add_case', 'Can add case'), ('change_case', 'Can change case'), ('delete_case', 'Can delete case'), ('add_task', 'Can add task'), ('change_task', 'Can change task'), ('delete_task', 'Can delete task'), ('add_letter', 'Can add letter'), ('reply', 'Can reply'), ('change_letter', 'Can change task'), ('delete_letter', 'Can delete letter'), ('view_alert', 'Can view alert'), ('change_alert', 'Can change alert'), ('delete_alert', 'Can delete alert'), ('manage_perm', 'Can manage perms'), ('select_survey', 'Can select answer')),
            },
        ),
        migrations.CreateModel(
            name='MonitoringGroupObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MonitoringUserObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='monitorings.Monitoring')),
                ('permission', models.ForeignKey(to='auth.Permission')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
