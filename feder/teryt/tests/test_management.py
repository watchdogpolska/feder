from django.core.management import CommandError, call_command
from django.test import TestCase


class LoadTercTestCase(TestCase):
    def test_missing_input_raises_command_error(self):
        with self.assertRaisesMessage(CommandError, "--input"):
            call_command("load_terc")
