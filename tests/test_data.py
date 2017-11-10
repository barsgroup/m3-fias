# coding: utf-8
from __future__ import unicode_literals

from datetime import date

from django.test import SimpleTestCase

from m3_fias.constants import FIAS_LEVEL_CITY
from m3_fias.data import AddressObject
from m3_fias.data import ObjectDictAdapter
from m3_fias.data import ObjectMapper
from m3_fias.utils import get_address_object


class change(object):

    def __init__(self, dictionary, key, new_value):
        self._dictionary = dictionary
        self._key = key
        self._old_value = dictionary[key]
        self._new_value = new_value

    def __enter__(self):
        self._dictionary[self._key] = self._new_value

    def __exit__(self, *_, **__):
        self._dictionary[self._key] = self._old_value


class TestCase(SimpleTestCase):

    def test__object_mapper(self):
        """Проверка ObjectMapper."""
        class DataMapper(ObjectMapper):
            fields_map = dict(
                qwe=123,
                asd=456,
                zxc=789,
            )

        test_data = {
            123: 'Иванов',
            456: 'Петров',
        }

        mapped_data = DataMapper(test_data)

        self.assertFalse(DataMapper({}))
        self.assertTrue(mapped_data)
        self.assertEqual(len(mapped_data), 2)
        self.assertItemsEqual(mapped_data, test_data.keys())
        self.assertItemsEqual(mapped_data.keys(), ('qwe', 'asd'))
        self.assertItemsEqual(mapped_data.values(), ('Иванов', 'Петров'))
        self.assertItemsEqual(mapped_data.items(), (
            ('qwe', 'Иванов'), ('asd', 'Петров'))
        )
        self.assertItemsEqual(mapped_data.iterkeys(), ('qwe', 'asd'))
        self.assertItemsEqual(mapped_data.itervalues(), ('Иванов', 'Петров'))
        self.assertItemsEqual(mapped_data.iteritems(), (
            ('qwe', 'Иванов'), ('asd', 'Петров')
        ))
        self.assertTrue('qwe' in mapped_data)
        self.assertTrue('asd' in mapped_data)
        self.assertFalse('zxc' in mapped_data)

        del mapped_data['qwe']
        self.assertEqual(len(mapped_data), 1)
        self.assertIn('asd', mapped_data)

    def test__object_data_adapter(self):
        """Проверка ObjectDictAdapter."""
        address_object = get_address_object(
            'd66e5325-3a25-4d29-ba86-4ca351d9704b'
        )
        data = ObjectDictAdapter(address_object)
        self.assertEqual(len(data), len(AddressObject.fields))
        for key in AddressObject.fields:
            self.assertEqual(getattr(address_object, key), data[key])
        for key in data:
            self.assertEqual(getattr(address_object, key), data[key])

        self.assertRaises(TypeError, data.__setitem__, 'guid', None)
        self.assertRaises(TypeError, data.__delitem__, 'guid')
        self.assertRaises(TypeError, data.pop, 'guid')
        self.assertRaises(TypeError, data.popitem)
        self.assertRaises(TypeError, data.clear)
        self.assertRaises(TypeError, data.update)
        self.assertRaises(TypeError, data.setdefault, 'guid', None)

    def test__address_object(self):
        """Проверка AddressObject."""
        test_data = dict(
            id='38b94ebc-7ced-47a8-9365-b33548e67cf4',
            guid='e2e21636-929a-4c51-b7b5-06ac067ce3f5',
            level=FIAS_LEVEL_CITY,
            kladr_status=0,
            actual=True,
            centre=0,
            operation=20,
            region_code='54',
            autonomy_code='0',
            area_code='000',
            city_code='001',
            city_area_code='000',
            place_code='000',
            street_code='0233',
            extra_code='0000',
            secondary_extra_code='000',
            short_name='ул',
            formal_name='Вокзальная магистраль',
            date_of_creation='1900-01-01',
            date_of_update='2014-03-01',
            date_of_expiration='2079-06-06',
            live_status=True,
        )
        ao = AddressObject(**test_data)

        # pylint: disable=no-member
        self.assertEqual(ao.id, '38b94ebc-7ced-47a8-9365-b33548e67cf4')
        self.assertEqual(ao.guid, 'e2e21636-929a-4c51-b7b5-06ac067ce3f5')
        self.assertEqual(ao.level, FIAS_LEVEL_CITY)
        self.assertEqual(ao.short_name, 'ул')
        self.assertEqual(ao.formal_name, 'Вокзальная магистраль')
        self.assertEqual(ao.date_of_creation, date(1900, 01, 01))
        self.assertEqual(ao.date_of_update, date(2014, 3, 1))
        self.assertEqual(ao.date_of_expiration, date(2079, 6, 6))
        self.assertIs(ao.live_status, 1)
        # pylint: enable=no-member

        self.assertRaises(AttributeError, setattr, ao, 'formal_name', 'Ленина')
        self.assertRaises(AttributeError, delattr, ao, 'formal_name')
        hash(ao)

        self.assertRaises(TypeError, AddressObject)

        with change(test_data, 'id', 'qweasdzxc'):
            self.assertRaises(ValueError, lambda: AddressObject(**test_data))

        with change(test_data, 'level', 100):
            self.assertRaises(ValueError, lambda: AddressObject(**test_data))
        with change(test_data, 'level', 'city'):
            self.assertRaises(ValueError, lambda: AddressObject(**test_data))

        with change(test_data, 'date_of_creation', date.today()):
            AddressObject(**test_data)
        with change(test_data, 'date_of_creation', '2349087'):
            self.assertRaises(ValueError, lambda: AddressObject(**test_data))
