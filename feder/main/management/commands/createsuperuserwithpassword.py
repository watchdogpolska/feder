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

        super().handle(*args, **options)

        if password:
            user = self.UserModel._default_manager.db_manager(database).get(
                username=username
            )
            user.set_password(password)
            user.save()
