# Generated by Django 1.11.7 on 2018-01-12 17:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("letters", "0009_auto_20170826_0742")]

    operations = [
        migrations.AlterModelOptions(
            name="letter",
            options={
                "ordering": ["created"],
                "permissions": (
                    ("can_filter_eml", "Can filter eml"),
                    ("recognize_letter", "Can recognize letter"),
                ),
                "verbose_name": "Letter",
                "verbose_name_plural": "Letters",
            },
        )
    ]
