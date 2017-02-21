from django.utils.module_loading import import_string

from .settings import MODULATORS_LIST


def get_modulators():
    """Returns a sets of modulators

    Returns:
        dict(name, modulator_cls): A sets of modulators
    """
    return {x.name: x for x in map(import_string, MODULATORS_LIST)}
