# Generated by Django 3.2.24 on 2024-03-08 13:51

from django.db import migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('llm_evaluation', '0003_llmmonthlycost'),
    ]

    operations = [
        migrations.AddField(
            model_name='llmmonthlycost',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='llmmonthlycost',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
    ]
