# Generated by Django 1.11.10 on 2018-02-19 00:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("letters", "0012_letter_mark_spam_by")]

    operations = [
        migrations.AddField(
            model_name="letter",
            name="mark_spam_at",
            field=models.DateTimeField(
                help_text="Time when letter was marked as spam",
                null=True,
                verbose_name=b"Time of mark as spam",
            ),
        )
    ]
