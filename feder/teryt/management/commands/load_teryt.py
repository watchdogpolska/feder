# -*- coding: utf-8 -*-
from lxml import etree
from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils.lru_cache import lru_cache
from feder.teryt.models import JednostkaAdministracyjna, Category


@lru_cache()
def get_genre(name, level):
    obj, _ = Category.objects.get_or_create(name=name, defaults={'level': level})
    return obj


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = ('Creates a data in database base on Teryt.xml file.')
    PARENT_REDUCE = {2: 0,
        4: 2,
        7: 4}
    LEVEL_REDUCE = {2: 1,
        4: 2,
        7: 3}

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    @classmethod
    def to_object(cls, row, commit=True):
        data = {x.get('name').lower(): x.text for x in row}
        obj = JednostkaAdministracyjna()
        obj.active = True
        obj.id = "".join(data.get(x, '') or '' for x in ('woj', 'pow', 'gmi', 'rodz'))
        index = len(obj.pk)
        if len(obj.id) > 2:
            obj.parent = JednostkaAdministracyjna.objects.get(pk=obj.id[:cls.PARENT_REDUCE[index]])
        obj.name = data['nazwa'].title()
        obj.updated_on = data['stan_na']
        obj.category = get_genre(data['nazdod'], cls.LEVEL_REDUCE[index])
        return obj

    def handle(self, *args, **options):
        root = etree.parse(options['filename'])
        self.stdout.write(("Importing started. "
                           "This may take a few seconds. Please wait a moment.\n"))
        rows_count = 0
        with transaction.atomic():
            with JednostkaAdministracyjna.objects.delay_mptt_updates():
                for row in root.iter('row'):
                    obj = Command.to_object(row)
                    obj.save()
                    rows_count += 1
        self.stdout.write("%s rows imported.\n" % rows_count)
