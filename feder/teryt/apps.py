from django.apps import AppConfig


class TerytConfig(AppConfig):
    name = "feder.teryt"

    def ready(self):
        patch_load_terc_command()


def patch_load_terc_command():
    """teryt_tree's load_terc command crashes with a bare TypeError from
    lxml when --input is omitted. Patch it to raise a clear CommandError
    instead."""
    from django.core.management.base import CommandError
    from teryt_tree.management.commands.load_terc import Command

    original_handle = Command.handle

    def handle(self, no_progress, input, old_format, limit, *args, **options):
        if input is None:
            raise CommandError(
                "Missing required argument: --input. "
                "Provide a path to the TERC XML file, e.g.:\n"
                "  python manage.py load_terc --input /tmp/TERC.xml"
            )
        return original_handle(
            self,
            no_progress=no_progress,
            input=input,
            old_format=old_format,
            limit=limit,
            *args,
            **options,
        )

    Command.handle = handle
