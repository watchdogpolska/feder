# Generated by Django 3.2.24 on 2024-02-09 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0018_institution_archival'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(blank=True, to='institutions.Tag', verbose_name='Tags'),
        ),
    ]