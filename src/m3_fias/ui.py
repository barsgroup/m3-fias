# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from m3_ext.ui.base import BaseExtComponent
from m3_ext.ui.containers.containers import ExtContainer
from m3_ext.ui.fields.simple import ExtComboBox
from m3_ext.ui.fields.simple import ExtHiddenField
from m3_ext.ui.fields.simple import ExtStringField
from m3_ext.ui.fields.simple import ExtTextArea
from m3_ext.ui.misc.store import ExtJsonStore

from m3_fias.data import ObjectDictAdapter
from m3_fias.utils import get_address_object
from m3_fias.utils import get_house
import m3_fias

from .constants import UI_LEVEL_FLAT
from .constants import UI_LEVEL_HOUSE
from .constants import UI_LEVEL_PLACE
from .constants import UI_LEVEL_STREET
from .constants import UI_LEVELS
from .data import ObjectMapper
from .utils import cached_property


class UIAddressObjectMapper(ObjectMapper):

    """Обертка над адресным объектом для передачи данных в UI.

    Преобразует наименования полей адресного объекта в наименования полей в
    компонентах ExtJS.
    """

    fields_map = {
        'guid': 'guid',
        'level': 'level',
        'shortName': 'short_name',
        'formalName': 'formal_name',
        'postalCode': 'postal_code',
        'fullName': 'full_name',
    }


class UIHouseMapper(ObjectMapper):

    """Обертка над домом для передачи данных в UI.

    Преобразует наименования полей дома в наименования полей в компонентах
    ExtJS.
    """

    fields_map = {
        'guid': 'guid',
        'houseNumber': 'house_number',
        'buildingNumber': 'building_number',
        'structureNumber': 'structure_number',
        'postalCode': 'postal_code',
    }


class AddressFields(BaseExtComponent):

    """Контейнер для полей редактирования составных элементов адреса.

    В зависимости от указанного уровня точности создает необходимые поля.

    Также реализует настройку поведения полей в зависимости от их заполнения.
    Например, если не заполнено поле "Населенный пункт", то поля "Улица",
    "Дом", "Корпус", "Строение", "Квартира" становятся недоступными для
    редактирования.

    Предназначен для использования в представлении адресной панели.
    """

    def __init__(self, *args, **kwargs):
        assert m3_fias.config.backend is not None
        self.backend = None

        # Флаг, определяющий обязательность заполнения адреса.
        self.allow_blank = True

        # Флаг, определяющий возможность редактирования адреса.
        self.read_only = False

        # Уровень точности адреса.
        self.level = UI_LEVEL_FLAT

        # Имена полей.
        self._names_of_fields = {
            'place_name': 'place_name',
            'place_guid': 'place_guid',
            'zip_code': 'zip_code',
            'street_name': 'street_name',
            'street_guid': 'street_guid',
            'house_number': 'house_number',
            'building_number': 'building_number',
            'structure_number': 'structure_number',
            'house_guid': 'house_guid',
            'flat_number': 'flat_number',
            'full_address': 'full_address',
        }

        # Подписи полей ввода.
        self._labels_text = {
            'place_name': 'Населенный пункт',
            'zip_code': 'Индекс',
            'street_name': 'Улица',
            'house_number': 'Дом',
            'building_number': 'Корпус',
            'structure_number': 'Строение',
            'flat_number': 'Квартира',
            'full_address': 'Полный адрес',
        }

        # Флаг, определяющий возможность ввода адресов, отсутствующих в ФИАС.
        self.fias_only = True

        # Флаг, определяющий отображение поля с полным адресом.
        self.with_full_address = None

        # Timeout запросов к серверу ФИАС.
        self.timeout = None

        super(AddressFields, self).__init__(*args, **kwargs)
        self.init_component(*args, **kwargs)

        self.backend = m3_fias.config.backend

        assert self.level in UI_LEVELS, self.level

        if self.with_full_address is None:
            self.with_full_address = self.level != UI_LEVEL_PLACE

    @property
    def names_of_fields(self):
        return self._names_of_fields

    @names_of_fields.setter
    def names_of_fields(self, value):
        self._names_of_fields.update(value)

    @property
    def labels_text(self):
        return self._labels_text

    @labels_text.setter
    def labels_text(self, value):
        self._labels_text.update(value)

    @cached_property
    def field__place_name(self):
        """Поле для ввода названия населенного пункта.

        :rtype: m3_ext.ui.fields.simple.ExtComboBox
        """
        result = ExtComboBox(
            name=self._names_of_fields['place_name'],
            label=self._labels_text['place_name'],
            display_field='fullName',
            value_field='fullName',
            query_param='filter',
            hide_trigger=True,
            force_selection=self.fias_only,
            min_chars=2,
            empty_text='Название субъекта/города/населенного пункта',
            read_only=self.read_only,
            allow_blank=self.allow_blank,
            fields=[
                'guid',
                'level',
                'fullName',
                'postalCode',
            ],
            store=ExtJsonStore(
                url=self.backend.place_search_url,
                id_property='guid',
                root='rows',
                total_property='total',
            ),
        )

        self.backend.configure_place_field(result)

        return result

    @cached_property
    def field__place_guid(self):
        """Поле для хранения GUID'а населенного пункта.

        :rtype: m3_ext.ui.fields.simple.ExtHiddenField
        """
        return ExtHiddenField(
            type=ExtHiddenField.STRING,
            name=self._names_of_fields['place_guid'],
        )

    @cached_property
    def field__zip_code(self):
        """Поле для отображения/ввода почтового индекса.

        Если параметр ``fias_only`` равен ``True``, то редактирование значения
        поля будет недоступно.

        :rtype: m3_ext.ui.fields.simple.ExtStringField
        """
        return ExtStringField(
            name=self._names_of_fields['zip_code'],
            label=self._labels_text['zip_code'],
            read_only=self.fias_only or self.read_only,
            width=50,
        )

    @cached_property
    def field__street_name(self):
        """Поле для ввода названия улицы.

        :rtype: m3_ext.ui.fields.simple.ExtComboBox
        """
        result = ExtComboBox(
            name=self._names_of_fields['street_name'],
            label=self._labels_text['street_name'],
            display_field='name',
            value_field='name',
            query_param='filter',
            hide_trigger=True,
            force_selection=self.fias_only,
            min_chars=2,
            empty_text='Название улицы/микрорайона',
            read_only=self.read_only,
            fields=[
                'guid',
                'level',
                'shortName',
                'postalCode',
                'formalName',
                'name',  # значение поля формируется как shortName + formalName
            ],
            store=ExtJsonStore(
                url=self.backend.street_search_url,
                id_property='guid',
                root='rows',
                total_property='total',
            ),
        )

        self.backend.configure_street_field(result)

        return result

    @cached_property
    def field__street_guid(self):
        """Поле для хранения GUID'а улицы.

        :rtype: m3_ext.ui.fields.simple.ExtHiddenField
        """
        return ExtHiddenField(
            type=ExtHiddenField.STRING,
            name=self._names_of_fields['street_guid'],
        )

    @cached_property
    def field__house_number(self):
        """Поле для ввода номера дома.

        :rtype: m3_ext.ui.fields.simple.ExtComboBox
        """
        result = ExtComboBox(
            name=self._names_of_fields['house_number'],
            label=self._labels_text['house_number'],
            display_field='houseNumber',
            value_field='houseNumber',
            query_param='filter',
            hide_trigger=True,
            force_selection=self.fias_only,
            min_chars=1,
            width=40,
            list_width=150,
            read_only=self.read_only,
            fields=[
                'guid',
                'houseNumber',
                'buildingNumber',
                'structureNumber',
                'postalCode',
            ],
            store=ExtJsonStore(
                url=self.backend.house_search_url,
                id_property='guid',
                root='rows',
                total_property='total',
            ),
        )

        self.backend.configure_house_field(result)

        return result

    @cached_property
    def field__building_number(self):
        """Поле для ввода номера корпуса.

        :rtype: m3_ext.ui.fields.simple.ExtComboBox
        """
        result = ExtStringField(
            name=self._names_of_fields['building_number'],
            label=self._labels_text['building_number'],
            read_only=self.fias_only or self.read_only,
            width=40,
        )

        return result

    @cached_property
    def field__structure_number(self):
        """Поле для ввода номера строения.

        :rtype: m3_ext.ui.fields.simple.ExtComboBox
        """
        result = ExtStringField(
            name=self._names_of_fields['structure_number'],
            label=self._labels_text['structure_number'],
            read_only=self.fias_only or self.read_only,
            width=40,
        )

        return result

    @cached_property
    def field__house_guid(self):
        """Поле для хранения GUID'а дома.

        :rtype: m3_ext.ui.fields.simple.ExtHiddenField
        """
        return ExtHiddenField(
            type=ExtHiddenField.STRING,
            name=self._names_of_fields['house_guid'],
        )

    @cached_property
    def field__flat_number(self):
        """Поле для ввода номера квартиры.

        :rtype: m3_ext.ui.fields.simple.ExtStringField
        """
        return ExtStringField(
            name=self._names_of_fields['flat_number'],
            label=self._labels_text['flat_number'],
            width=40,
            read_only=self.read_only
        )

    @cached_property
    def field__full_address(self):
        """Поле для отображения/ввода полного адреса.

        Если параметр ``fias_only`` равен ``True``, то редактирование значения
        поля будет недоступно.

        :rtype: m3_ext.ui.fields.simple.ExtTextArea
        """
        return ExtTextArea(
            name=self._names_of_fields['full_address'],
            label=self._labels_text['full_address'],
            height=36,
            read_only=self.fias_only or self.read_only,
        )

    @property
    def items(self):
        """Возвращает все поля.

        Т.к. это не контейнер, в коде JavaScript этого параметра не будет, но
        он используется для биндинга формы с объектами.
        """
        result = [
            self.field__place_guid,
            self.field__place_name,
            self.field__zip_code,
        ]
        if self.level in (UI_LEVEL_STREET, UI_LEVEL_HOUSE, UI_LEVEL_FLAT):
            result.extend((
                self.field__street_guid,
                self.field__street_name,
            ))
        if self.level in (UI_LEVEL_HOUSE, UI_LEVEL_FLAT):
            result.extend((
                self.field__house_guid,
                self.field__house_number,
                self.field__building_number,
                self.field__structure_number,
            ))
        if self.level == UI_LEVEL_FLAT:
            result.append(
                self.field__flat_number
            )
        if self.with_full_address:
            result.append(
                self.field__full_address
            )
        return result

    @cached_property
    def place(self):
        """Населенный пункт.

        :rtype: m3_fias.data.AddressObject
        """
        if self.field__place_guid.value:
            return get_address_object(
                self.field__place_guid.value,
                self.timeout,
            )

    @cached_property
    def street(self):
        """Улица.

        :rtype: m3_fias.data.AddressObject
        """
        assert self.level in (UI_LEVEL_STREET, UI_LEVEL_HOUSE, UI_LEVEL_FLAT)

        if self.field__street_guid.value:
            return get_address_object(
                self.field__street_guid.value,
                self.timeout,
            )

    @cached_property
    def house(self):
        """Дом.

        :rtype: m3_fias.data.House
        """
        assert self.level in (UI_LEVEL_HOUSE, UI_LEVEL_FLAT)

        if (
            self.field__house_guid.value and
            (
                self.field__street_guid.value or
                self.field__place_guid.value
            )
        ):
            return get_house(
                guid=self.field__house_guid.value,
                ao_guid=(
                    self.field__street_guid.value or
                    self.field__place_guid.value
                ),
                timeout=self.timeout,
            )

    def find_by_name(self, name):
        """Поиск экземпляра поля по имени.

        Метод Ext-контейнеров, позволяющий рекурсивно искать вложенные элементы
        """
        for item in self.items:
            if hasattr(item, 'name') and name == getattr(item, 'name'):
                return item

    def render_base_config(self):
        super(AddressFields, self).render_base_config()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Поля ввода элементов адреса.

        put = self._put_config_value

        put('level', self.level)
        put('fiasOnly', self.fias_only)

        put('placeNameField', self.field__place_name.render)
        put('placeGUIDField', self.field__place_guid.render)
        if self.place:
            place_dict = ObjectDictAdapter(self.place)
            put('place', dict(UIAddressObjectMapper(place_dict)))

        put('zipCodeField', self.field__zip_code.render)

        if self.level in (UI_LEVEL_STREET, UI_LEVEL_HOUSE, UI_LEVEL_FLAT):
            put('streetNameField', self.field__street_name.render)
            put('streetGUIDField', self.field__street_guid.render)
            if self.street:
                street_dict = ObjectDictAdapter(self.street)
                put('street', dict(UIAddressObjectMapper(street_dict)))

        if self.level in (UI_LEVEL_HOUSE, UI_LEVEL_FLAT):
            put('houseNumberField', self.field__house_number.render)
            put('buildingNumberField', self.field__building_number.render)
            put('structureNumberField', self.field__structure_number.render)
            put('houseGUIDField', self.field__house_guid.render)
            if self.house:
                house_dict = ObjectDictAdapter(self.house)
                put('house', dict(UIHouseMapper(house_dict)))

        if self.level == UI_LEVEL_FLAT:
            put('flatNumberField', self.field__flat_number.render)

        if self.with_full_address:
            put('withFullAddress', self.with_full_address)
            put('fullAddressField', self.field__full_address.render)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def render(self):
        self.pre_render()
        self.render_base_config()

        return 'new Ext.m3.fias.AddressFields({%s})' % self._get_config_str()


class AddressViewBase(ExtContainer):

    """Базовый класс для представлений панели ввода адреса."""

    def _get_labels_width(self):  # pylint: disable=no-self-use
        return {}

    def __init__(self, *args, **kwargs):
        self._labels_width = self._get_labels_width()

        self.fields = None

        super(AddressViewBase, self).__init__(*args, **kwargs)

        assert isinstance(self.fields, AddressFields), type(self.fields)

    @property
    def labels_width(self):
        return self._labels_width

    @labels_width.setter
    def labels_width(self, value):
        self._labels_width.update(value)

    def render_base_config(self):
        super(AddressViewBase, self).render_base_config()

        put = self._put_config_value
        put('labelsWidth', self._labels_width)

    def render(self):
        self.pre_render()
        self.render_base_config()

        return 'new %s({%s})' % (self._ext_name, self._get_config_str())


class RowsAddressView(AddressViewBase):

    """Представление адресной панели с размещением элементов на трех строках.

    Каждая из строк содержит следующие поля:

        1. Населенный пункт, Индекс
        2. Улица, Дом, Корпус, Строение, Квартира
        3. Полный адрес

    Поля "Населенный пункт", "Улица" и "Полный адрес" выровнены слева.
    """

    def _get_labels_width(self):
        result = super(RowsAddressView, self)._get_labels_width()
        result.update({
            'place': 110,
            'zipCode': 44,
            'street': 110,
            'house': 28,
            'building': 44,
            'structure': 58,
            'flat': 55,
            'fullAddress': 110,
        })
        return result

    def __init__(self, *args, **kwargs):
        super(RowsAddressView, self).__init__(*args, **kwargs)

        self._ext_name = 'Ext.m3.fias.RowsAddressView'

    def init_component(self, *args, **kwargs):
        super(RowsAddressView, self).init_component(*args, **kwargs)

        # Контейнер полей добавляется в items для того, чтобы была возможность
        # биндинга объекта с полями формы. В JavaScript этот объект будет
        # удален из items.
        self.items.append(self.fields)


class CompactAddressView(RowsAddressView):

    def _get_labels_width(self):
        result = super(CompactAddressView, self)._get_labels_width()
        result.update({
            'place': 110,
            'street': 38,
            'fullAddress': 87,
        })
        return result
