from os import path
import tempfile
import zipfile
import io
from collections import OrderedDict
import requests
from django.core import management
from django.test import TestCase


class TestParseCommand(TestCase):
    url_tmpl = 'http://www.stat.gov.pl/broker/access/prefile/'\
               'downloadPreFile.jspa?id={}'

    files = OrderedDict([
        ('TERC.xml', '1110'),
    ])

    def _save_file(self, filename, url):
        request = requests.get(url)
        zfile = zipfile.ZipFile(io.BytesIO(request.content))
        zfile.extract(filename, self.tempdir)

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        for filename, file_id in self.files.items():
            self._save_file(filename, self.url_tmpl.format(file_id))

    def test_command(self):
        for filename in self.files.keys():
            management.call_command('load_teryt', '--limit 50 ' +
                                    path.join(self.tempdir, filename))
