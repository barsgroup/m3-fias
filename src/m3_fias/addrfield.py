#coding:utf-8

from django.conf import settings
from django.core.urlresolvers import reverse

from m3_ext.ui.containers.base import BaseExtContainer
from m3_ext.ui.fields.simple import ExtHiddenField

from m3_fias import helpers
from m3.core.json import M3JSONEncoder

class ExtFiasAddrComponent(BaseExtContainer):
    '''
    Блок указания адреса
    '''
    PLACE = 1 # Уровнь населенного пункта
    STREET = 2 # Уровнь улицы
    HOUSE = 3 # Уровень дома
    FLAT = 4 # Уровень квартиры

    VIEW_0 = 0 # хитрый режим (пока не будем делать), когда отображается только адрес, а его редактирование отдельным окном
    VIEW_1 = 1 # в одну строку + адрес
    VIEW_2 = 2 # в две строки + адрес, только для level > PLACE
    VIEW_3 = 3 # в три строки + адрес, только для level > STREET

    INVALID_CLASS = 'm3-form-invalid' #Название хтмл-класса м3,
    # который отвечает за стиль отображения неверно заполненных полей
    INVALID_COMPOSITE_FIELD_CLASS = 'm3-composite-field-invalid' #Название класса,
    # отвечающего за прорисовку неверно заполненных композитных полей

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

        # Атрибуты, определяющие необходимость заполнения полей
        self.place_allow_blank = True
        self.street_allow_blank = True
        self.house_allow_blank = True
        self.corps_allow_blank = True
        self.flat_allow_blank = True

        #Названия инвалидных классов
        self.invalid_class = ExtFiasAddrComponent.INVALID_CLASS
        self.invalid_composite_field_class = ExtFiasAddrComponent\
        .INVALID_COMPOSITE_FIELD_CLASS

        self.addr_visible = True
        self.read_only = False
        self.level = ExtFiasAddrComponent.FLAT
        self.view_mode = ExtFiasAddrComponent.VIEW_2

        # Если True — показывает поле корпуса в режиме >=3
        self.use_corps = False

        self.layout = 'form'
        self.template = 'ext-fields/ext-fias-addrfield.js'
        self.addr = ExtHiddenField(name = self._addr_field_name, type = ExtHiddenField.STRING)
        self.place = ExtHiddenField(name = self._place_field_name, type = ExtHiddenField.STRING)
        self.street = ExtHiddenField(name = self._street_field_name, type = ExtHiddenField.STRING)
        self.house = ExtHiddenField(name = self._house_field_name, type = ExtHiddenField.STRING)
        self.corps = ExtHiddenField(name = self._corps_field_name, type = ExtHiddenField.STRING)
        self.flat = ExtHiddenField(name = self._flat_field_name, type = ExtHiddenField.STRING)
        self.zipcode = ExtHiddenField(name = self._zipcode_field_name, type = ExtHiddenField.STRING)
        self._items.append(self.addr)
        self._items.append(self.place)
        self._items.append(self.street)
        self._items.append(self.house)
        self._items.append(self.corps)
        self._items.append(self.flat)
        self._items.append(self.zipcode)

        # Установка высоты - самый главный хак в этом коде!
        if self.view_mode == ExtFiasAddrComponent.VIEW_1:
            self.height = 25
        elif self.view_mode == ExtFiasAddrComponent.VIEW_2:
            if self.level >= ExtFiasAddrComponent.STREET:
                self.height = 25*2
            else:
                self.height = 25
        elif self.view_mode == ExtFiasAddrComponent.VIEW_3:
            if self.level > ExtFiasAddrComponent.HOUSE:
                self.height = 25*3
            else:
                if self.level > ExtFiasAddrComponent.STREET:
                    self.height = 25*2
                else:
                    self.height = 25
        if self.addr_visible:
            self.height += 36+7

        self.init_component(*args, **kwargs)

    def render_params(self):
        def escape_str(in_str):
            '''
            Экранирует в строке спец. символы, такие как \ ' "
            '''

            return in_str.replace('"','\"').replace("'","\'").replace('\\', '\\\\')

        super(ExtFiasAddrComponent, self).render_params()
        self._put_params_value('place_field_name', self.place_field_name)
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
        self._put_params_value('addr_visible', (True if self.addr_visible else False ))
        self._put_params_value('level', self.level)
        self._put_params_value('view_mode', self.view_mode)
        self._put_params_value('read_only', self.read_only)
        self._put_params_value('place_value', (self.place.value if self.place and self.place.value else ''))
        
        place = None
        if self.place and self.place.value:
            place = helpers.get_ao_object(self.place.value)
            self._put_params_value('place_record',  M3JSONEncoder().encode(place))
        else:
            self._put_params_value('place_record',  '')

        street = None
        if self.street and self.street.value:
            street = helpers.get_ao_object(self.street.value)
            self._put_params_value('street_record',  M3JSONEncoder().encode(street))
        else:
            self._put_params_value('place_record',  '')

        self._put_params_value('place_allow_blank', (True if self.place_allow_blank else False))
        self._put_params_value('street_value', (self.street.value if self.street and self.street.value else ''))
        self._put_params_value('street_allow_blank', (True if self.street_allow_blank else False))
        self._put_params_value('house_value', (escape_str(self.house.value) if self.house and self.house.value else ''))
        self._put_params_value('house_allow_blank', self.house_allow_blank)
        self._put_params_value('corps_value', (escape_str(self.corps.value) if self.corps and self.corps.value else ''))
        self._put_params_value('corps_allow_blank', self.corps_allow_blank)
        self._put_params_value('flat_value', (escape_str(self.flat.value) if self.flat and self.flat.value else ''))
        self._put_params_value('flat_allow_blank', self.flat_allow_blank)
        self._put_params_value('zipcode_value', self.get_zipcode())
        self._put_params_value('addr_value', (escape_str(self.addr.value) if self.addr and self.addr.value else ''))

        self._put_params_value('fias_api_url', '/fias/remote')
        self._put_params_value('invalid_class', self.invalid_class)
        self._put_params_value('invalid_composite_field_class', self.invalid_composite_field_class)
        self._put_params_value('use_corps', self.use_corps)

    def make_read_only(self, access_off=True, exclude_list=(), *args, **kwargs):
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
            if len(addr)>6:
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
