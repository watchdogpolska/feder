from unittest import TestCase

from feder.letters.utils import normalize_msg_id


class normalize_msg_idTestCase(TestCase):
    RESULT = {
        "xxxxxx": "xxxxxx",
        "xxxxxx>": "xxxxxx",
        "xxxxxx>>": "xxxxxx>",
        "<xxxxxx": "xxxxxx",
        "<<xxxxxx": "<xxxxxx",
    }

    def test_various_results_compare(self):
        for input, result in self.RESULT.items():
            self.assertEqual(normalize_msg_id(input), result)
