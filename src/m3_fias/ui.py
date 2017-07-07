# coding: utf-8
from __future__ import unicode_literals

from m3_ext.ui.containers.forms import ExtPanel
from m3_ext.ui.fields.simple import ExtStringField
from m3_ext.ui.fields.simple import ExtTextArea

from m3_fias.constants import LEVEL_FLAT
from m3_fias.utils import cached_property


class AddressPanel(ExtPanel):

    """Базовый класс для панели ввода адреса."""

    def __init__(self, *args, **kwargs):
        # Флаг, определяющий обязательность заполнения адреса.
        self.allow_blank = True

        # Флаг, определяющий возможность редактирования адреса.
        self.read_only = False

        # Уровень точности адреса.
        self.level = LEVEL_FLAT

        # Подписи полей ввода.
        self.label__place = 'Населенный пункт'
        self.label__street = 'Улица'
        self.label__house = 'Дом'
        self.label__zip = 'Индекс'
        self.label__flat = 'Квартира'
        self.label__address = 'Полный адрес'

        # Флаг, определяющий возможность ввода адресов, отсутствующих в ФИАС.
        self.fias_only = True

        # Поля ввода.
        self.field__place = ExtStringField(
            name='place',
        )
        self.field__street = ExtStringField(
            name='street',
        )
        self.field__house = ExtStringField(
            name='house',
        )
        self.field__zip = ExtStringField(
            name='zipcode',
            read_only=self.fias_only,
        )
        self.field__flat = ExtStringField(
            name='flat',
        )
        self.field__address = ExtTextArea(
            name='address',
            read_only=self.fias_only,
        )

        super(AddressPanel, self).__init__(*args, **kwargs)

    @cached_property
    def field__place(self):
        return ExtStringField(
            name='place',
        )

    @cached_property
    def field__street(self):
        return ExtStringField(
            name='street',
        )

    @cached_property
    def field__house(self):
        return ExtStringField(
            name='house',
        )

    def render(self):
        self.pre_render()
        self.render_base_config()
        self.render_params()

        base_config = self._get_config_str()

        return 'new Ext.m3.fias.AddressPanel({%s})' % base_config
