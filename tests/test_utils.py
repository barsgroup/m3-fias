# coding: utf-8
from __future__ import unicode_literals

from django.test import SimpleTestCase

from m3_fias.data import House
from m3_fias.utils import correct_keyboard_layout
from m3_fias.utils import find_address_objects
from m3_fias.utils import find_house
from m3_fias.utils import get_address_object
from m3_fias.utils import get_address_object_name
from m3_fias.utils import get_full_name
from m3_fias.utils import get_house
from m3_fias.utils import get_house_name


class UtilsTestCase(SimpleTestCase):

    """Тесты для модуля m3_fias.utils."""

    def test__correct_keyboard_layout(self):
        test_data = (
            ('', ''),
            ('Привет!', 'Привет!'),
            ('Ghbdtn!', 'Привет!'),
            ('Ghbdtn всем!', 'Ghbdtn всем!'),
        )

        for text, result in test_data:
            self.assertEqual(correct_keyboard_layout(text), result)

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

    def test__find_house(self):
        """Проверка функции find_house."""
        # ---------------------------------------------------------------------
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
        # ---------------------------------------------------------------------
        # Московская обл., г. Звенигород, мкр. Супонево
        street_guid = '2b03a2a5-7635-4318-bc65-0660c037524d'
        # Московская обл., г. Звенигород, мкр. Супонево, стр. 18
        house_guid = '45600c3e-7b68-413b-8d7c-1b1d644d76bc'

        house = find_house(street_guid, None, None, '18')
        self.assertIsInstance(house, House)
        self.assertEqual(house.guid, house_guid)
        self.assertEqual(house.parent_guid, street_guid)
        self.assertFalse(house.house_number)
        self.assertFalse(house.building_number)
        self.assertEqual(house.structure_number, '18')
        # ---------------------------------------------------------------------

    def test__get_address_object_name(self):
        """Проверка функции get_address_object_name."""
        self.assertEqual(
            get_address_object_name(
                get_address_object('e2e21636-929a-4c51-b7b5-06ac067ce3f5')
            ),
            'ул. Вокзальная магистраль'
        )
        self.assertEqual(
            get_address_object_name(
                get_address_object('d66e5325-3a25-4d29-ba86-4ca351d9704b')
            ),
            'Ханты-Мансийский Автономный округ - Югра'
        )
        self.assertEqual(
            get_address_object_name(
                get_address_object('b6ba5716-eb48-401b-8443-b197c9578734')
            ),
            'Забайкальский край'
        )

    def test__get_house_name(self):
        """Проверка функции get_house_name."""
        self.assertEqual(
            get_house_name(
                get_house(
                    guid='0d1ad06b-0f7f-493f-9076-0a05225af36c',
                    ao_guid='0d5c91c9-433f-43be-bc20-e7ebf352ccad'
                )
            ),
            'д. 159'
        )
        self.assertEqual(
            get_house_name(
                get_house(
                    guid='a18032c1-72ac-4a0d-a528-07a611f551e9',
                    ao_guid='0d5c91c9-433f-43be-bc20-e7ebf352ccad'
                )
            ),
            'д. 1, корп. Д, стр. 11'
        )
        self.assertEqual(
            get_house_name(
                # Московская обл., г. Звенигород, мкр. Супонево, стр. 18
                get_house(
                    guid='45600c3e-7b68-413b-8d7c-1b1d644d76bc',
                    ao_guid='2b03a2a5-7635-4318-bc65-0660c037524d',
                )
            ),
            'стр. 18'
        )

    def test__get_full_name(self):
        """Проверка функции get_full_name."""
        self.assertRaises(TypeError, get_full_name, None)
        self.assertEqual(
            get_full_name(
                get_address_object('e2e21636-929a-4c51-b7b5-06ac067ce3f5')
            ),
            'Новосибирская обл, г. Новосибирск, ул. Вокзальная магистраль'
        )
        self.assertEqual(
            get_full_name(
                get_address_object('4792cbff-20ee-4d4a-9c35-f6fa75e1bf9a')
            ),
            '630124, Новосибирская обл, г. Новосибирск, ул. Толбухина'
        )
        self.assertEqual(
            get_full_name(
                get_house(
                    guid='a18032c1-72ac-4a0d-a528-07a611f551e9',
                    ao_guid='0d5c91c9-433f-43be-bc20-e7ebf352ccad'
                )
            ),
            '672010, Забайкальский край, г. Чита, ул. Ленина, д. 1, корп. Д, '
            'стр. 11'
        )
