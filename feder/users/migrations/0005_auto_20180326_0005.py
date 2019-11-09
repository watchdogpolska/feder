# Generated by Django 1.11.10 on 2018-03-26 00:05

from django.contrib.auth import validators
from django.db import migrations, models
from django.utils import six


class Migration(migrations.Migration):

    dependencies = [("users", "0004_auto_20180325_2244")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(blank=True, max_length=30, verbose_name="last name"),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                error_messages={"unique": "A user with that username already exists."},
                help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                max_length=150,
                unique=True,
                validators=[validators.UnicodeUsernameValidator()],
                verbose_name="username",
            ),
        ),
    ]
