# Generated by Django 1.11.2 on 2017-08-10 21:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("letters", "0006_auto_20170808_0252")]

    operations = [
        migrations.AddField(
            model_name="letter",
            name="is_spam",
            field=models.IntegerField(
                choices=[(0, "Unknown"), (1, "Spam"), (2, "Non-spam")],
                db_index=True,
                default=0,
            ),
        )
    ]
