from .local import *  # noqa


class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


MIGRATION_MODULES = DisableMigrations()

DATABASES['default']['TEST_CHARSET'] = "utf8"
DATABASES['default']['TEST_COLLATION'] = "utf8_general_ci"

