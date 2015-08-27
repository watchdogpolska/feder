# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teryt', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='E-mail')),
            ],
            options={
                'verbose_name': 'Email',
                'verbose_name_plural': 'Emails',
            },
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'name', verbose_name='Slug', editable=False)),
                ('address', models.EmailField(max_length=254, verbose_name='E-mail')),
            ],
            options={
                'verbose_name': 'Institution',
                'verbose_name_plural': 'Institution',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=15, verbose_name='Name')),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'name', verbose_name='Slug', editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='JST',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('teryt.jednostkaadministracyjna',),
        ),
        migrations.AddField(
            model_name='institution',
            name='jst',
            field=models.ForeignKey(to='institutions.JST'),
        ),
        migrations.AddField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(to='institutions.Tag', verbose_name='Tag'),
        ),
        migrations.AddField(
            model_name='email',
            name='institution',
            field=models.ForeignKey(verbose_name='Institution', to='institutions.Institution'),
        ),
    ]
