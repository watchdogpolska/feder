# Generated by Django 1.11.2 on 2017-08-08 03:09

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Institution = apps.get_model("institutions", "Institution")
    db_alias = schema_editor.connection.alias
    Institution.objects.using(db_alias).filter(regon="").all().update(regon=None)


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    Institution = apps.get_model("institutions", "Institution")
    db_alias = schema_editor.connection.alias
    Institution.objects.using(db_alias).filter(regon=None).all().update(regon="")


class Migration(migrations.Migration):
    dependencies = [("institutions", "0011_auto_20170808_0308")]

    operations = [
        migrations.AlterField(
            model_name="institution",
            name="regon",
            field=models.CharField(
                blank=True, max_length=14, null=True, verbose_name="REGON number"
            ),
        ),
        migrations.RunPython(forwards_func, reverse_func),
        migrations.AlterField(
            model_name="institution",
            name="regon",
            field=models.CharField(
                blank=True,
                max_length=14,
                null=True,
                unique=True,
                verbose_name="REGON number",
            ),
        ),
    ]
