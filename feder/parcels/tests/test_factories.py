from django.test import TestCase

from feder.parcels.factories import IncomingParcelPostFactory, OutgoingParcelPostFactory


class IncomingParcelPostFactoryTestCase(TestCase):
    def test_basic_create(self):
        IncomingParcelPostFactory()


class OutgoingParcelPostFactoryTestCase(TestCase):
    def test_basic_create(self):
        OutgoingParcelPostFactory()

