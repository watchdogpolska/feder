# Generated by Django 3.2.20 on 2023-08-22 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitorings', '0025_monitoring_results'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitoring',
            name='results',
            field=models.TextField(default='', help_text='Resulrs of monitoring and received responses', verbose_name='Results'),
        ),
    ]
