# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('institutions', '0002_auto_20150803_0643'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('attachment', models.FileField(upload_to=b'', verbose_name='Content')),
            ],
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(
                    default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(
                    default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('body', models.TextField(verbose_name='Text')),
                ('quote', models.TextField(verbose_name='Quote', blank=True)),
                ('author_institution', models.ForeignKey(to='institutions.Institution')),
                ('author_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'Letter',
                'verbose_name_plural': 'Letter',
            },
        ),
        migrations.AddField(
            model_name='attachment',
            name='record',
            field=models.ForeignKey(to='letters.Letter'),
        ),
    ]
