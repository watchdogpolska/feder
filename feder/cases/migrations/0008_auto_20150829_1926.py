# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Case = apps.get_model("cases", "Case")
    for case in Case.objects.filter(email=None).all():
        case.email = "case-{0}@example.com".format(case.pk)
        case.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0007_case_email'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
        migrations.AlterField(
            model_name='case',
            name='email',
            field=models.CharField(unique=True, max_length=75, db_index=True),
        ),
    ]
