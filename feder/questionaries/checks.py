from django.core.checks import Error
from django.utils.module_loading import import_string

from .settings import MODULATORS_LIST


def test_modulators_list_settings(app_configs, **kwargs):
    errors = []
    modulators = []
    for path in MODULATORS_LIST:
        try:
            modulators.append((import_string(path), path))
        except ImportError:
            errors.append(
                Error(
                    "Unable to import %s modulator" % (path),
                    hint="Verify QUESTIONARIES_MODULATOR settings.",
                    obj=path,
                    id="questionaries.E001",
                )
            )
    key = {}
    for module, path in modulators:
        if module.name in key:
            errors.append(
                Error(
                    "Duplicate use name %s of %s modulator. Last used for module %s"
                    % (module.name, path, key[module.name]),
                    hint="Verify QUESTIONARIES_MODULATOR settings.",
                    obj=path,
                    id="questionaries.E002",
                )
            )
        key[module.name] = path
    return errors
