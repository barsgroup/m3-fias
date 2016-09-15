# coding:utf-8
from m3_ext.ui.containers.base import BaseExtContainer
from m3_ext.ui.fields.simple import ExtHiddenField

from m3_fias import helpers
from m3 import M3JSONEncoder


class ExtFiasAddrComponent(BaseExtContainer):
    '''
    Блок указания адреса
    '''
    PLACE = 1  # Уровнь населенного пункта
    STREET = 2  # Уровнь улицы
    HOUSE = 3  # Уровень дома
    FLAT = 4  # Уровень квартиры

    # VIEW_0 - хитрый режим (пока не будем делать), когда отображается только
    # адрес, а его редактирование отдельным окном
    VIEW_0 = 0
    VIEW_1 = 1  # в одну строку + адрес
    VIEW_2 = 2  # в две строки + адрес, только для level > PLACE
    VIEW_3 = 3  # в три строки + адрес, только для level > STREET

    # Название хтмл-класса м3, который отвечает за стиль отображения неверно
    # заполненных полей
    INVALID_CLASS = 'm3-form-invalid'

    # Название класса, отвечающего за прорисовку неверно заполненных
    # композитных полей
    INVALID_COMPOSITE_FIELD_CLASS = 'm3-composite-field-invalid'

    def __init__(self, *args, **kwargs):
        super(ExtFiasAddrComponent, self).__init__(*args, **kwargs)
        # Названия полей к которым биндится КЛАДР
        self._place_field_name = 'place'
        self._street_field_name = 'street'
        self._house_field_name = 'house'
        self._corps_field_name = 'corps'
        self._flat_field_name = 'flat'
        self._zipcode_field_name = 'zipcode'
        self._addr_field_name = 'addr'

        # Названия меток
        self.place_label = u'Населенный пункт'
        self.street_label = u'Улица'
        self.house_label = u'Дом'
        self.corps_label = u'Корпус'
        self.flat_label = u'Квартира'
        self.addr_label = u'Адрес'

        # Ширина меток
        self.zipcode_label_width = 1
        self.street_label_width = 45
        self.house_label_width = 27
        self.corps_label_width = 45
        self.flat_label_width = 55

        # Атрибуты, определяющие необходимость заполнения полей
        self.place_allow_blank = kwargs.get('place_allow_blank', True)
        self.street_allow_blank = kwargs.get('street_allow_blank', True)
        self.house_allow_blank = kwargs.get('house_allow_blank', True)
        self.corps_allow_blank = kwargs.get('corps_allow_blank', True)
        self.flat_allow_blank = kwargs.get('flat_allow_blank', True)

        # Указывает на возможность редактирования полей индекса и
        # полного адреса
        self.can_edit_addr = kwargs.get('can_edit_addr', True)

        # Названия инвалидных классов
        self.invalid_class = self.INVALID_CLASS
        self.invalid_composite_field_class = self.INVALID_COMPOSITE_FIELD_CLASS

        self.addr_visible = True
        self.read_only = False
        self.level = kwargs.get('level', self.FLAT)
        self.view_mode = kwargs.get('view_mode', self.VIEW_2)

        # Если True — показывает поле корпуса в режиме >=3
        self.use_corps = False

        self.layout = 'form'
        self.template = 'ext-fields/ext-fias-addrfield.js'

        ExtHF = lambda s: ExtHiddenField(name=s, type=ExtHiddenField.STRING)
        self.addr = ExtHF(self._addr_field_name)
        self.place = ExtHF(self._place_field_name)
        self.street = ExtHF(self._street_field_name)
        self.house = ExtHF(self._house_field_name)
        self.corps = ExtHF(self._corps_field_name)
        self.flat = ExtHF(self._flat_field_name)
        self.zipcode = ExtHF(self._zipcode_field_name)
        self.house_guid = ExtHF(self._house_field_name + '_guid')

        self._items.append(self.addr)
        self._items.append(self.place)
        self._items.append(self.street)
        self._items.append(self.house)
        self._items.append(self.corps)
        self._items.append(self.flat)
        self._items.append(self.zipcode)
        self._items.append(self.house_guid)

        # Установка высоты - самый главный хак в этом коде!
        row_height = 29

        self.height = row_height
        if self.view_mode == self.VIEW_2:
            if self.level >= self.STREET:
                self.height += row_height
        elif self.view_mode == self.VIEW_3:
            if self.level >= self.STREET:
                self.height += row_height
            if self.level >= self.HOUSE:
                self.height += row_height

        if self.addr_visible:
            self.height += 36+7

        self.init_component(*args, **kwargs)

    def render_params(self):
        def escape_str(in_str):
            '''
            Экранирует в строке спец. символы, такие как \ ' "
            '''

            return in_str.replace('"', '\"').replace("'", "\'").replace(
                '\\', '\\\\')

        super(ExtFiasAddrComponent, self).render_params()
        self._put_params_value('place_field_name', self.place_field_name)
        self._put_params_value('can_edit_addr', bool(self.can_edit_addr))
        self._put_params_value('street_field_name', self.street_field_name)
        self._put_params_value('house_field_name', self.house_field_name)
        self._put_params_value('corps_field_name', self.corps_field_name)
        self._put_params_value('flat_field_name', self.flat_field_name)
        self._put_params_value('zipcode_field_name', self.zipcode_field_name)
        self._put_params_value('addr_field_name', self.addr_field_name)
        self._put_params_value('place_label', self.place_label)
        self._put_params_value('street_label', self.street_label)
        self._put_params_value('house_label', self.house_label)
        self._put_params_value('corps_label', self.corps_label)
        self._put_params_value('flat_label', self.flat_label)
        self._put_params_value('addr_label', self.addr_label)
        self._put_params_value('zipcode_label_width',
                               self.zipcode_label_width)
        self._put_params_value('street_label_width', self.street_label_width)
        self._put_params_value('house_label_width', self.house_label_width)
        self._put_params_value('corps_label_width', self.corps_label_width)
        self._put_params_value('flat_label_width', self.flat_label_width)
        self._put_params_value('addr_visible', bool(self.addr_visible))
        self._put_params_value('level', self.level)
        self._put_params_value('view_mode', self.view_mode)
        self._put_params_value('read_only', self.read_only)
        self._put_params_value('place_value', self.place.value)

        place = None
        if self.place and self.place.value:
            place = helpers.get_ao_object(self.place.value)
            self._put_params_value(
                'place_record',  M3JSONEncoder().encode(place))
        else:
            self._put_params_value('place_record',  '')

        street = None
        if self.street and self.street.value:
            street = helpers.get_ao_object(self.street.value)
            self._put_params_value(
                'street_record',  M3JSONEncoder().encode(street))
        else:
            self._put_params_value('street_record',  '')

        self._put_params_value('house_guid_value', self.house_guid.value)

        self._put_params_value('place_allow_blank',
                               bool(self.place_allow_blank))
        self._put_params_value('street_value', self.street.value)
        self._put_params_value('street_allow_blank',
                               bool(self.street_allow_blank))
        self._put_params_value('house_value', escape_str(self.house.value))
        self._put_params_value('house_allow_blank', self.house_allow_blank)
        self._put_params_value('corps_value', escape_str(self.corps.value))
        self._put_params_value('corps_allow_blank', self.corps_allow_blank)
        self._put_params_value('flat_value', escape_str(self.flat.value))
        self._put_params_value('flat_allow_blank', self.flat_allow_blank)
        self._put_params_value('zipcode_value', self.get_zipcode())
        self._put_params_value('addr_value', escape_str(self.addr.value))

        self._put_params_value('fias_api_url', '/fias/remote')
        self._put_params_value('invalid_class', self.invalid_class)
        self._put_params_value('invalid_composite_field_class',
                               self.invalid_composite_field_class)
        self._put_params_value('use_corps', self.use_corps)

    def make_read_only(self, access_off=True, exclude_list=(), *args, **kw):
        self.read_only = access_off

    def get_zipcode(self):
        '''
        Получаем значение почтового индекса. Если он явно не указан, то берем
        первые 6 символов текстового представления адреса и пытаемся проверить,
        являются ли они числами. В случае успеха, возвращаем их.
        '''
        if self.zipcode and self.zipcode.value:
            return self.zipcode.value
        if self.addr:
            addr = self.addr.value
            if len(addr) > 6:
                try:
                    return unicode(int(addr[:6]))
                except ValueError:
                    pass
        return ''

    def render_base_config(self):
        res = super(ExtFiasAddrComponent, self).render_base_config()
        return res

    def render(self):
        self.render_base_config()
        self.render_params()

        config = self._get_config_str()
        params = self._get_params_str()
        return 'new Ext.fias.AddrField({%s},{%s})' % (config, params)

    @property
    def items(self):
        return self._items

    @property
    def place_field_name(self):
        return self._place_field_name

    @place_field_name.setter
    def place_field_name(self, value):
        self._place_field_name = value
        self.place.name = value

    @property
    def street_field_name(self):
        return self._street_field_name

    @street_field_name.setter
    def street_field_name(self, value):
        self._street_field_name = value
        self.street.name = value

    @property
    def house_field_name(self):
        return self._house_field_name

    @house_field_name.setter
    def house_field_name(self, value):
        self._house_field_name = value
        self.house.name = value
        self.house_guid.name = '_'.join((value, 'guid'))

    @property
    def corps_field_name(self):
        return self._corps_field_name

    @corps_field_name.setter
    def corps_field_name(self, value):
        self._corps_field_name = value
        self.corps.name = value

    @property
    def flat_field_name(self):
        return self._flat_field_name

    @flat_field_name.setter
    def flat_field_name(self, value):
        self._flat_field_name = value
        self.flat.name = value

    @property
    def zipcode_field_name(self):
        return self._zipcode_field_name

    @zipcode_field_name.setter
    def zipcode_field_name(self, value):
        self._zipcode_field_name = value
        self.zipcode.name = value

    @property
    def addr_field_name(self):
        return self._addr_field_name

    @addr_field_name.setter
    def addr_field_name(self, value):
        self._addr_field_name = value
        self.addr.name = value
