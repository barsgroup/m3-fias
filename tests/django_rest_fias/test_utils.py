# coding: utf-8
from __future__ import unicode_literals

from unittest import skipUnless
from uuid import uuid4

from django import test
from django.conf import settings

from m3_fias.backends.django_rest_fias.proxy.utils import _guid2str
from m3_fias.backends.django_rest_fias.proxy.utils import find_address_objects
from m3_fias.backends.django_rest_fias.proxy.utils import find_house
from m3_fias.backends.django_rest_fias.proxy.utils import get_address_object
from m3_fias.backends.django_rest_fias.proxy.utils import get_house
from m3_fias.data import House


@skipUnless(
    settings.FIAS['BACKEND'] == 'm3_fias.backends.django_rest_fias.proxy',
    'Another backend used'
)
class TestCase(test.SimpleTestCase):

    """Проверка утилит бэкенда для django-rest-fias."""

    def test__guid2str(self):
        self.assertIsInstance(
            _guid2str('e2e21636-929a-4c51-b7b5-06ac067ce3f5'),
            unicode
        )
        self.assertIsInstance(
            _guid2str(uuid4()),
            unicode
        )
        self.assertRaises(ValueError, _guid2str, '23458976')
        self.assertRaises(ValueError, _guid2str, 23458976)

    def test__get_address_object(self):
        """Проверка функции get_address_object."""
        # Новосибирск, ул. Вокзальная магистраль
        guid = 'e2e21636-929a-4c51-b7b5-06ac067ce3f5'
        ao = get_address_object(guid)

        self.assertEqual(ao.guid, guid)
        self.assertEqual(ao.id, '38b94ebc-7ced-47a8-9365-b33548e67cf4')
        self.assertEqual(
            ao.parent_guid, '8dea00e3-9aab-4d8e-887c-ef2aaa546456'
        )
        self.assertEqual(ao.formal_name, 'Вокзальная магистраль')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        guid = 'e2e21636-929a-4c51-b7b5-06ac067ce3f4'
        self.assertIsNone(get_address_object(guid))

    def test__find_address_object(self):
        """Проверка функции find_address_object."""
        result = tuple(
            find_address_objects('Вокзальная магистраль')
        )

        def get_param_values(name):
            return tuple(
                ao_params[name]
                for ao_params in result
            )

        self.assertEqual(len(result), 2)
        self.assertItemsEqual(get_param_values('guid'), (
            'c4b23ba4-e4ba-47d6-9000-4d502ef7bd5a',
            'e2e21636-929a-4c51-b7b5-06ac067ce3f5',
        ))
        self.assertItemsEqual(get_param_values('formal_name'), (
            'Вокзальная',
            'Вокзальная магистраль',
        ))

        result = tuple(find_address_objects(
            filter_string='Вокзальная магистраль',
            parent_guid='8dea00e3-9aab-4d8e-887c-ef2aaa546456',
        ))
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]['guid'], 'e2e21636-929a-4c51-b7b5-06ac067ce3f5'
        )
        self.assertEqual(
            result[0]['parent_guid'], '8dea00e3-9aab-4d8e-887c-ef2aaa546456'
        )

    def test__get_house(self):
        """Проверка функции get_house."""
        # Новосибирск, ул. Вокзальная магистраль
        street_guid = 'e2e21636-929a-4c51-b7b5-06ac067ce3f5'
        # Новосибирск, ул. Вокзальная магистраль, д. 1/1
        house_guid = '1379911c-bea5-43e4-93ec-666d9381fc9c'

        house = get_house(house_guid, street_guid)

        self.assertIsInstance(house, House)
        self.assertEqual(house.guid, house_guid)
        self.assertEqual(house.parent_guid, street_guid)
        self.assertEqual(house.house_number, '1/1')
        self.assertFalse(house.building_number)
        self.assertFalse(house.structure_number)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        house_guid = '1379911c-bea5-43e4-93ec-666d9381fc9d'
        self.assertIsNone(get_house(house_guid, street_guid))

    def test__find_house(self):
        """Проверка функции find_house."""
        # Новосибирск, ул. Вокзальная магистраль
        street_guid = 'e2e21636-929a-4c51-b7b5-06ac067ce3f5'
        # Новосибирск, ул. Вокзальная магистраль, д. 1/1
        house_guid = '1379911c-bea5-43e4-93ec-666d9381fc9c'

        house = find_house(street_guid, '1/1')

        self.assertIsInstance(house, House)
        self.assertEqual(house.guid, house_guid)
        self.assertEqual(house.parent_guid, street_guid)
        self.assertEqual(house.house_number, '1/1')
        self.assertFalse(house.building_number)
        self.assertFalse(house.structure_number)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        house_guid = '1379911c-bea5-43e4-93ec-666d9381fc9d'
        self.assertIsNone(find_house(street_guid, '1/10'))
