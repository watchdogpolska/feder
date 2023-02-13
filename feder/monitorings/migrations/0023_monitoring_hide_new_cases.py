# Generated by Django 2.2.27 on 2022-07-30 17:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("monitorings", "0022_auto_20210920_1959"),
    ]

    operations = [
        migrations.AddField(
            model_name="monitoring",
            name="hide_new_cases",
            field=models.BooleanField(
                default=False, verbose_name="Hide new cases when assigning?"
            ),
        ),
    ]
