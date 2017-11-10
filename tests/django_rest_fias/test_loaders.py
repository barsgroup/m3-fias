# coding: utf-8
# pylint: disable=protected-access
from __future__ import unicode_literals

from collections import Iterable
from unittest import skipUnless
from uuid import UUID

from django import test
from django.conf import settings

from m3_fias.backends.django_rest_fias.proxy.utils import HouseLoader
from m3_fias.backends.django_rest_fias.proxy.utils import PlaceLoader
from m3_fias.backends.django_rest_fias.proxy.utils import StreetLoader


@skipUnless(
    settings.FIAS['BACKEND'] == 'm3_fias.backends.django_rest_fias.proxy',
    'Another backend used'
)
class TestCase(test.SimpleTestCase):

    """Тесты для загрузчиков."""

    def test__place_loader(self):
        """Проверка загрузчика сведений о населенных пунктах."""
        place_name = 'Полярные Зори'

        loader = PlaceLoader(place_name)
        data = loader.load()

        self.assertIsInstance(data, Iterable)
        self.assertEqual(len(data), 9)
        for ao_data in data:
            self.assertIn(ao_data['level'], loader._levels)
            self.assertItemsEqual(ao_data, loader._fields)

        data = PlaceLoader('лени').load(page=1)
        self.assertEqual(len(data), 100)

        self.assertFalse(PlaceLoader('adfkljbadfb').load())

    def test__street_loader(self):
        """Проверка загрузчика сведений об улицах."""
        # Мурманская обл, г Полярные Зори
        parent_guid = 'd70b2917-8cea-4555-a9fe-6d2c72d8d9cc'
        street_name = 'Строителей'

        loader = StreetLoader(street_name, parent_guid)
        data = loader.load()

        self.assertIsInstance(data, Iterable)
        self.assertEqual(len(data), 1)
        for ao_data in data:
            self.assertIn(ao_data['level'], loader._levels)
            self.assertItemsEqual(ao_data, loader._fields)
            self.assertTrue(ao_data['formalName'].startswith(street_name))

    def test__house_loader1(self):
        """Проверка загрузчика сведений об домах."""
        address_object_guid = UUID('96c3bde4-c5c6-495a-9774-e7d21ee488c8')
        house_filter = '8'

        loader = HouseLoader(address_object_guid, house_filter)
        data = loader.load()

        self.assertIsInstance(data, Iterable)
        self.assertEqual(len(data), 5)
        for ao_data in data:
            house = ao_data['houseNumber']

            self.assertItemsEqual(ao_data, loader._fields)
            self.assertTrue(house.startswith(house_filter), house)
