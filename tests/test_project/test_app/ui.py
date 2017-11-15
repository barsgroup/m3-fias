# coding: utf-8
from __future__ import unicode_literals

from m3_ext.ui.containers.containers import ExtContainer
from m3_ext.ui.containers.forms import ExtForm
from m3_ext.ui.containers.forms import ExtPanel
from m3_ext.ui.windows.edit_window import ExtEditWindow
from m3_ext.ui.windows.window import ExtWindow

from m3_fias.constants import UI_LEVEL_FLAT
from m3_fias.constants import UI_LEVEL_HOUSE
from m3_fias.constants import UI_LEVEL_PLACE
from m3_fias.constants import UI_LEVEL_STREET
from m3_fias.ui import AddressFields
from m3_fias.ui import CompactAddressView
import m3_fias


class AddressWindow(ExtWindow):

    """Окно с адресными панелями."""

    def _get_address_panels(self, fields_config=None, view_config=None):
        def get_panel(level, title):
            panel = ExtPanel(
                title=title,
                header=True,
                body_cls='x-window-mc',
                padding=5,
            )
            panel.items.append(
                CompactAddressView(
                    fields=AddressFields(
                        level=level,
                        backend=m3_fias.config.backend,
                        **(fields_config or {})
                    ),
                    **(view_config or {})
                ),
            )
            return panel

        return (
            get_panel(UI_LEVEL_PLACE, 'UI_LEVEL_PLACE'),
            get_panel(UI_LEVEL_STREET, 'UI_LEVEL_STREET'),
            get_panel(UI_LEVEL_HOUSE, 'UI_LEVEL_HOUSE'),
            get_panel(UI_LEVEL_FLAT, 'UI_LEVEL_FLAT'),
        )

    def _getLeftPanel(self):
        result = ExtContainer(
            flex=1,
            layout='vbox',
            layout_config={
                'align': 'stretch',
            },
            style={
                'padding-right': '5px',
            },
        )

        result.items[:] = self._get_address_panels(
            fields_config=dict(
                with_full_address=False,
            )
        )

        return result

    def _getRightPanel(self):
        result = ExtContainer(
            flex=1,
            layout='vbox',
            layout_config={
                'align': 'stretch',
            },
            style={
                'padding-left': '5px',
            },
        )

        result.items[:] = self._get_address_panels(
            fields_config=dict(
                with_full_address=True,
                fias_only=False,
            )
        )

        return result

    def __init__(self, *args, **kwargs):
        super(AddressWindow, self).__init__(*args, **kwargs)

        self.items.extend((
            self._getLeftPanel(),
            self._getRightPanel(),
        ))

        self.maximized = True
        self.layout = 'hbox'
        self.layout_config = {
            'align': 'stretch',
        }


class EditWindow(ExtEditWindow):

    def __init__(self, *args, **kwargs):
        super(EditWindow, self).__init__(*args, **kwargs)

        self.address_fields = AddressFields(
            level=UI_LEVEL_FLAT,
            backend=m3_fias.config.backend,
            names_of_fields=dict(
                place_guid='place',
                street_guid='street',
                house_guid='house',
                flat_number='flat',
            ),
        )
        self.address_view = CompactAddressView(fields=self.address_fields)
        self.form = ExtForm()
        self.form.items.append(self.address_view)

        obj = type(str(), (object,), {})
        obj.level = UI_LEVEL_FLAT
        obj.place = '2d9abaa6-85a6-4f1f-a1bd-14b76ec17d9c'
        obj.street = '0d5c91c9-433f-43be-bc20-e7ebf352ccad'
        obj.house = 'a18032c1-72ac-4a0d-a528-07a611f551e9'
        obj.flat = '111'

        self.form.from_object(obj)
        assert self.address_fields.field__place_guid.value == obj.place
        assert self.address_fields.field__street_guid.value == obj.street
        assert self.address_fields.field__house_guid.value == obj.house
        assert self.address_fields.field__flat_number.value == obj.flat

        self.width = 800
        self.height = 300
