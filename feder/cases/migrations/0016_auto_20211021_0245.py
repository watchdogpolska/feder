# Generated by Django 2.2.24 on 2021-10-21 02:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0015_case_is_quarantied"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="case",
            index=models.Index(
                fields=["created"], name="cases_case_created_a615f3_idx"
            ),
        ),
    ]
