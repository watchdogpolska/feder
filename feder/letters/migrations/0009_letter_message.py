# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0004_bytestring_to_unicode'),
        ('letters', '0008_auto_20150828_2201'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='message',
            field=models.ForeignKey(verbose_name='Message', to='django_mailbox.Message', help_text='Message registerd by django-mailbox', null=True),
        ),
    ]
