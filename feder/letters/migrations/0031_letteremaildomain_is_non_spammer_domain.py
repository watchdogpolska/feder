# Generated by Django 3.2.16 on 2023-02-15 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0030_letteremaildomain_is_trusted_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='letteremaildomain',
            name='is_non_spammer_domain',
            field=models.BooleanField(default=False, verbose_name='Is non spammer domain?'),
        ),
    ]
