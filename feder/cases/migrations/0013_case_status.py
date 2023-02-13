# Generated by Django 2.2.17 on 2021-02-18 12:20

from django.db import migrations


def get_confirmation_received(case, Letter):
    return (
        Letter.objects.filter(record__case=case, author_user_id__isnull=True)
        .filter(message_type__in=[2, 3])
        .exists()
    )


def get_response_received(case, Letter):
    return (
        Letter.objects.filter(record__case=case, author_user_id__isnull=True)
        .exclude(message_type__in=[2, 3])
        .exists()
    )


def forwards(apps, schema_editor):
    Case = apps.get_model("cases", "Case")
    Letter = apps.get_model("letters", "Letter")

    count = 0
    for case in Case.objects.all().iterator():
        case.confirmation_received = get_confirmation_received(case, Letter)
        case.response_received = get_response_received(case, Letter)
        case.save()
        count += 1

    print(f"\nUpdated status of {count} cases.")


def backwards(apps, schema_editor):
    Case = apps.get_model("cases", "Case")

    count = 0
    for case in Case.objects.all().iterator():
        case.confirmation_received = False
        case.response_received = False
        case.save()
        count += 1

    print(f"\nRestored initial status of {count} cases.")


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0012_auto_20210218_1043"),
        ("letters", "0024_letter_message_type"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
