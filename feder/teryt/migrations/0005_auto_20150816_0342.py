# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teryt', '0004_auto_20150804_0016'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Kategoria', 'verbose_name_plural': 'Kategorie'},
        ),
        migrations.AlterModelOptions(
            name='jednostkaadministracyjna',
            options={'verbose_name': 'Jednostka podzia\u0142u terytorialnego', 'verbose_name_plural': 'Jednostki podzia\u0142u terytorialnego'},
        ),
        migrations.AlterField(
            model_name='category',
            name='level',
            field=models.IntegerField(db_index=True, choices=[(1, 'wojew\xf3dztwo'), (2, 'powiat'), (3, 'gmina')]),
        ),
        migrations.AlterField(
            model_name='jednostkaadministracyjna',
            name='name',
            field=models.CharField(max_length=36, verbose_name='Nazwa'),
        ),
        migrations.AlterField(
            model_name='jednostkaadministracyjna',
            name='updated_on',
            field=models.DateField(verbose_name='Data aktualizacji'),
        ),
    ]
