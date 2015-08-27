# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0002_letter_case'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachment',
            options={'verbose_name': 'Attachment', 'verbose_name_plural': 'Attachments'},
        ),
        migrations.AlterField(
            model_name='attachment',
            name='attachment',
            field=models.FileField(upload_to=b'letters/%Y/%m/%d', verbose_name='File'),
        ),
    ]
