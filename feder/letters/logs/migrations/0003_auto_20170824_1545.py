# Generated by Django 1.10.7 on 2017-08-24 15:45

from collections import OrderedDict

from django.db import migrations

from feder.letters.logs.models import STATUS


def get_status(data):
    status_list = OrderedDict(STATUS).keys()
    for status in status_list:
        time_name = f"{status}_time"
        desc_name = f"{status}_desc"
        if data.get(time_name, False) or data.get(desc_name, False):
            return status
    return STATUS.unknown


def forwards_func(apps, schema_editor):
    EmailLog = apps.get_model("logs", "EmailLog")
    db_alias = schema_editor.connection.alias
    for log in EmailLog.objects.using(db_alias).prefetch_related("logrecord_set").all():
        for record in log.logrecord_set.all():
            log.status = get_status(record.data)
        log.save(update_fields=["status"])


class Migration(migrations.Migration):

    dependencies = [("logs", "0002_auto_20170820_1447")]

    operations = [migrations.RunPython(forwards_func)]
