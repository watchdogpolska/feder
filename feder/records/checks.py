from django.core.checks import Error, register

from feder.records.models import Record, AbstractRecord
from feder.records.registry import record_type_registry


@register()
def record_type_registry_fill_check(app_configs, **kwargs):
    errors = []

    for field in Record._meta.related_objects:
        if issubclass(field.related_model, AbstractRecord) and field.related_model not in record_type_registry:
            errors.append(
                Error(
                    'Missing required record type definition.',
                    hint='Add missing required data type and load in AppConfig.',
                    obj=field.related_model,
                    id='records.E001',
                )
            )
    return errors
