# Generated by Django 3.1.5 on 2022-11-20 23:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_auto_20191020_2235"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="first name"
            ),
        ),
    ]
