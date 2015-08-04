# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'name', editable=False)),
                ('level', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='JednostkaAdministracyjna',
            fields=[
                ('id', models.CharField(max_length=7, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=36, verbose_name=b'Nazwa')),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'name', editable=False)),
                ('updated_on', models.DateField()),
                ('active', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('category', models.ForeignKey(to='teryt.Category')),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='teryt.JednostkaAdministracyjna', null=True)),
            ],
            options={
                'verbose_name': 'TERYT',
                'verbose_name_plural': 'TERYT',
            },
        ),
    ]
