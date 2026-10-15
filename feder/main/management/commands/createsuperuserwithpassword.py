# credit: https://stackoverflow.com/a/42491469
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError


# NOTE: required only for django <3
# With Django 3, you can use the default `createsuperuser` command by setting
# `DJANGO_SUPERUSER_PASSWORD`.
# https://docs.djangoproject.com/en/3.0/ref/django-admin/#createsuperuser
class Command(createsuperuser.Command):
    help = "Create a superuser, and allow password to be provided"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--password",
            dest="password",
            default=None,
            help="Specifies the password for the superuser.",
        )

    def handle(self, *args, **options):
        password = options.get("password")
        username = options.get("username")
        database = options.get("database")

        if password and not username:
            raise CommandError("--username is required if specifying --password")

        manager = self.UserModel._default_manager.db_manager(database)
        user = manager.filter(username=username).first() if username else None

        if user is None:
            super().handle(*args, **options)
            user = manager.get(username=username)
        else:
            user.is_superuser = True
            user.is_staff = True

        if password:
            user.set_password(password)
            user.save()
