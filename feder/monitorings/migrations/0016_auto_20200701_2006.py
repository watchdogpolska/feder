# Generated by Django 2.2.14 on 2020-07-01 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("monitorings", "0015_auto_20200327_0040"),
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
                    ("add_task", "Can add task"),
                    ("change_task", "Can change task"),
                    ("delete_task", "Can delete task"),
                    ("add_letter", "Can add letter"),
                    ("reply", "Can reply"),
                    ("add_draft", "Add reply draft"),
                    ("change_letter", "Can change task"),
                    ("delete_letter", "Can delete letter"),
                    ("view_alert", "Can view alert"),
                    ("change_alert", "Can change alert"),
                    ("delete_alert", "Can delete alert"),
                    ("manage_perm", "Can manage perms"),
                    ("select_survey", "Can select answer"),
                    ("view_log", "Can view logs"),
                    ("spam_mark", "Can mark spam"),
                    ("add_parcelpost", "Can add parcel post"),
                    ("change_parcelpost", "Can change parcel post"),
                    ("delete_parcelpost", "Can delete parcel post"),
                    ("view_email_address", "Can view e-mail address"),
                ),
                "verbose_name": "Monitoring",
                "verbose_name_plural": "Monitoring",
            },
        ),
    ]
