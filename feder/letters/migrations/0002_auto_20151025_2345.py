# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('django_mailbox', '0004_bytestring_to_unicode'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('letters', '0001_initial'),
        ('cases', '0004_case_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='author_user',
            field=models.ForeignKey(verbose_name='Author (if user)', blank=True, to=settings.AUTH_USER_MODEL,
                                    null=True),
        ),
        migrations.AddField(
            model_name='letter',
            name='case',
            field=models.ForeignKey(verbose_name='Case', to='cases.Case'),
        ),
        migrations.AddField(
            model_name='letter',
            name='message',
            field=models.ForeignKey(verbose_name='Message', to='django_mailbox.Message',
                                    help_text='Message registerd by django-mailbox', null=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='record',
            field=models.ForeignKey(to='letters.Letter'),
        ),
    ]
