# Generated by Django 1.10.7 on 2017-08-26 07:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("letters", "0007_letter_is_spam")]

    operations = [
        migrations.AddField(
            model_name="letter",
            name="message_id_field",
            field=models.CharField(
                blank=True,
                max_length=500,
                verbose_name='ID of sent email message "Message-ID"',
            ),
        )
    ]
