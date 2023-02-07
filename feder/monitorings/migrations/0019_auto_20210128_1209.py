# Generated by Django 2.2.17 on 2021-01-28 12:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("monitorings", "0018_auto_20200711_2201"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="monitoring",
            options={
                "ordering": ["created"],
                "permissions": (
                    ("add_case", "Can add case"),
                    ("change_case", "Can change case"),
                    ("delete_case", "Can delete case"),
                    ("add_letter", "Can add letter"),
                    ("reply", "Can reply"),
                    ("add_draft", "Add reply draft"),
                    ("change_letter", "Can change letter"),
                    ("delete_letter", "Can delete letter"),
                    ("view_alert", "Can view alert"),
                    ("change_alert", "Can change alert"),
                    ("delete_alert", "Can delete alert"),
                    ("manage_perm", "Can manage perms"),
                    ("view_log", "Can view logs"),
                    ("spam_mark", "Can mark spam"),
                    ("add_parcelpost", "Can add parcel post"),
                    ("change_parcelpost", "Can change parcel post"),
                    ("delete_parcelpost", "Can delete parcel post"),
                    ("view_email_address", "Can view e-mail address"),
                    ("view_report", "Can view report"),
                ),
                "verbose_name": "Monitoring",
                "verbose_name_plural": "Monitoring",
            },
        ),
    ]
