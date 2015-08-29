# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0005_auto_20150829_2235'),
        ('letters', '0008_auto_20150828_2201'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='message',
            field=models.ForeignKey(verbose_name='Message', to='django_mailbox.Message', help_text='Message registerd by django-mailbox', null=True),
        ),
    ]
