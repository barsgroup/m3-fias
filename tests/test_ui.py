# coding: utf-8
from __future__ import unicode_literals

from django import test
from m3.actions import ControllerCache
from m3_ext.ui.containers.forms import ExtForm

from m3_fias import config
from m3_fias.constants import UI_LEVEL_FLAT
from m3_fias.ui import AddressFields
from m3_fias.ui import CompactAddressView
from m3_fias.ui import RowsAddressView


class TestCase(test.SimpleTestCase):

    """Проверка компонент пользовательского интерфейса."""

    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()

        ControllerCache.populate()

    def test__address_fields__default(self):
        """Проверка AddressFields."""
        address_fields = AddressFields(
            backend=config.backend,
        )
        address_fields.render()

    def test__address_fields__rename_fields(self):
        """Проверка AddressFields с измененными именами полей."""
        address_fields = AddressFields(
            backend=config.backend,
            names_of_fields=dict(
                place_name='prefix.place_name',
                place_guid='prefix.place_guid',
                zip_code='prefix.zip_code',
                street_name='prefix.street_name',
                street_guid='prefix.street_guid',
                house_number='prefix.house_number',
                building_number='prefix.building_number',
                structure_number='prefix.structure_number',
                house_guid='prefix.house_guid',
                flat_number='prefix.flat_number',
                full_address='prefix.full_address',
            ),
        )
        address_fields.render()

        for field_name, test_name in (
            (address_fields.field__place_name.name, 'place_name'),
            (address_fields.field__place_guid.name, 'place_guid'),
            (address_fields.field__zip_code.name, 'zip_code'),
            (address_fields.field__street_name.name, 'street_name'),
            (address_fields.field__street_guid.name, 'street_guid'),
            (address_fields.field__house_number.name, 'house_number'),
            (address_fields.field__building_number.name, 'building_number'),
            (address_fields.field__structure_number.name, 'structure_number'),
            (address_fields.field__house_guid.name, 'house_guid'),
            (address_fields.field__flat_number.name, 'flat_number'),
            (address_fields.field__full_address.name, 'full_address'),
        ):
            self.assertEqual(field_name, 'prefix.' + test_name)

    def test__address_fields__change_labels(self):
        """Проверка AddressFields с имененными подписями полей."""
        address_fields = AddressFields(
            backend=config.backend,
            labels_text=dict(
                place_name='PLACE',
                zip_code='POSTAL_CODE',
                street_name='STREET',
                house_number='HOUSE',
                building_number='BUILDING',
                structure_number='STRUCTURE',
                flat_number='FLAT',
                full_address='FULL_ADDRESS',
            )
        )
        address_fields.render()

        for field_label, test_label in (
            (address_fields.field__place_name.label, 'PLACE'),
            (address_fields.field__zip_code.label, 'POSTAL_CODE'),
            (address_fields.field__street_name.label, 'STREET'),
            (address_fields.field__house_number.label, 'HOUSE'),
            (address_fields.field__building_number.label, 'BUILDING'),
            (address_fields.field__structure_number.label, 'STRUCTURE'),
            (address_fields.field__flat_number.label, 'FLAT'),
            (address_fields.field__full_address.label, 'FULL_ADDRESS'),
        ):
            self.assertEqual(field_label, test_label)

    def test__compact_address_view__default(self):
        """Проверка CompactAddressView."""
        compact_view = CompactAddressView(
            fields=AddressFields(
                backend=config.backend,
            ),
        )
        compact_view.render()

    def test__compact_address_view__change_labels_width(self):
        """Проверка CompactAddressView с измененной шириной меток полей."""
        compact_view = CompactAddressView(
            fields=AddressFields(
                backend=config.backend,
            ),
            labels_width=dict(
                place=200,
                zipCode=200,
                street=200,
                house=200,
                building=200,
                structure=200,
                flat=200,
                fullAddress=200,
            ),
        )
        compact_view.render()

        self.assertTrue(
            width == 200
            for width in compact_view.labels_width
        )

    def test__form_binding(self):
        """Проверка биндинга форм с адресными панелями."""
        address = type(str(), (object,), {})
        address.place = '2d9abaa6-85a6-4f1f-a1bd-14b76ec17d9c'
        address.street = '0d5c91c9-433f-43be-bc20-e7ebf352ccad'
        address.house = '0d1ad06b-0f7f-493f-9076-0a05225af36c'

        address_fields = AddressFields(
            level=UI_LEVEL_FLAT,
            names_of_fields={
                'place_guid': 'place',
                'street_guid': 'street',
                'house_guid': 'house',
            },
        )

        view = RowsAddressView(
            fields=address_fields,
        )

        form = ExtForm()
        form.items.append(view)

        form.from_object(address)

        js = form.render()
        # pylint: disable=no-member
        self.assertIn(address.place, js)
        self.assertIn(address.street, js)
        self.assertIn(address.house, js)
