# Generated by Django 4.2.21 on 2025-05-15 19:04

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('virus_scan', '0006_alter_request_object_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='EngineApiKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('engine', models.CharField(choices=[('MetaDefender', 'MetaDefender'), ('Attachmentscanner', 'Attachmentscanner'), ('VirusTotal', 'VirusTotal')], default='MetaDefender', max_length=32)),
                ('key', models.CharField(max_length=100, unique=True)),
                ('url', models.CharField(max_length=200)),
                ('prevention_limit', models.IntegerField(default=100, verbose_name='Prevention limit')),
                ('prevention_remaining', models.IntegerField(default=0, verbose_name='Prevention remaining')),
                ('prevention_interval_sec', models.IntegerField(default=86400, verbose_name='Prevention interval in seconds')),
                ('prevention_reset_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Prevention reset at')),
                ('last_used', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last used')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
