# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0003_auto_20150804_0016'),
    ]

    operations = [
        migrations.DeleteModel(
            name='JST',
        ),
        migrations.AlterField(
            model_name='institution',
            name='jst',
            field=models.ForeignKey(verbose_name='Unit of administrative division', to='teryt.JednostkaAdministracyjna'),
        ),
    ]
