# Generated by Django 1.11.2 on 2017-07-08 22:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("institutions", "0008_auto_20161001_2053")]

    operations = [
        migrations.AlterModelOptions(
            name="institution",
            options={
                "ordering": ["name"],
                "verbose_name": "Institution",
                "verbose_name_plural": "Institution",
            },
        )
    ]
