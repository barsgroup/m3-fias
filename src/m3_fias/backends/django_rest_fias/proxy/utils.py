# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from importlib import import_module
from itertools import chain
from itertools import count
from uuid import UUID

from six import text_type
from six import with_metaclass
from six.moves import http_client
from six.moves import map
from six.moves import range

from m3_fias.constants import FIAS_LEVELS_PLACE
from m3_fias.constants import FIAS_LEVELS_STREET
from m3_fias.data import AddressObject
from m3_fias.data import House
from m3_fias.data import ObjectMapper
from m3_fias.utils import cached_property

from .server import server


def _guid2str(guid):
    if guid:
        try:
            return text_type(guid if isinstance(guid, UUID) else UUID(guid))
        except (AttributeError, TypeError, ValueError):
            raise ValueError(guid)
# -----------------------------------------------------------------------------
# Обёртки над данными, поступающими с сервера django-rest-fias.


class AddressObjectMapper(ObjectMapper):

    """Обертка над данными сервера django-rest-fias об адресных объектах.

    Предназначена для использования при создании экземпляров
    :class:`m3_fias.data.AddressObject`.
    """

    fields_map = dict(
        id='aoid',
        parent_guid='parentguid',
        guid='aoguid',
        previous_id='previd',
        next_id='nextid',
        ifns_fl_code='ifnsfl',
        ifns_fl_territorial_district_code='terrifnsfl',
        ifns_ul_code='ifnsul',
        ifns_ul_territorial_district_code='terrifnsul',
        okato='okato',
        oktmo='oktmo',
        postal_code='postalcode',
        formal_name='formalname',
        official_name='offname',
        short_name='shortname',
        level='aolevel',
        region_code='regioncode',
        autonomy_code='autocode',
        area_code='areacode',
        city_code='citycode',
        city_area_code='ctarcode',
        place_code='placecode',
        street_code='streetcode',
        extra_code='extrcode',
        secondary_extra_code='sextcode',
        kladr_code='code',
        kladr_plain_code='plaincode',
        actual='actstatus',
        centre='centstatus',
        operation='operstatus',
        kladr_status='currstatus',
        date_of_update='updatedate',
        date_of_creation='startdate',
        date_of_expiration='enddate',
        normative_document_guid='normdoc',
        live_status='livestatus',
        full_name='fullname',
    )
    assert set(
        fields_map
    ) == set(
        import_module('m3_fias.data').AddressObject.fields
    )


class HouseMapper(ObjectMapper):

    """Обертка над данными сервера django-rest-fias об адресных объектах.

    Предназначена для использования при создании экземпляров
    :class:`m3_fias.data.House`.
    """

    fields_map = dict(
        guid='houseguid',
        id='houseid',
        parent_guid='aoguid',
        ifns_fl_code='ifnsfl',
        ifns_fl_territorial_district_code='terrifnsfl',
        ifns_ul_code='ifnsul',
        ifns_ul_territorial_district_code='terrifnsul',
        okato='okato',
        oktmo='oktmo',
        postal_code='postalcode',
        house_number='housenum',
        estate_status='eststatus',
        building_number='buildnum',
        structure_number='strucnum',
        structure_status='strstatus',
        state_status='statstatus',
        kladr_counter='counter',
        date_of_update='updatedate',
        date_of_creation='startdate',
        date_of_end='enddate',
        normative_document_guid='normdoc',
    )
    assert set(
        fields_map
    ) == set(
        import_module('m3_fias.data').House.fields
    )


class UIAddressObjectMapper(ObjectMapper):

    """Обертка над данными сервера django-rest-fias об адресных объектах.

    Предназначена для использования в UI.
    """

    fields_map = dict(
        guid='aoguid',
        level='aolevel',
        shortName='shortname',
        formalName='formalname',
        postalCode='postalcode',
        fullName='fullname',
    )


class UIHouseMapper(ObjectMapper):

    """Обертка над данными сервера django-rest-fias о зданиях.

    Предназначена для использования в UI.
    """

    fields_map = dict(
        guid='houseguid',
        houseNumber='housenum',
        buildingNumber='buildnum',
        structureNumber='strucnum',
        postalCode='postalcode',
    )
# -----------------------------------------------------------------------------
# Загрузчики данных с сервера django-rest-fias.


class LoaderBase(with_metaclass(ABCMeta, object)):

    """Базовый класс для загрузчиков объектов ФИАС."""

    def __init__(self, filter_string, **kwargs):
        """Инициализация экземпляра класса.

        :param unicode filter_string: Строка для фильтрации объектов.
        :param float timeout: Timeout запросов к серверу ФИАС в секундах.
        """
        self.filter_string = filter_string
        self.timeout = kwargs.get('timeout')

    @abstractproperty
    def _path(self):
        """Путь к ресурсу API сервера ФИАС.

        :rtype: str
        """

    @abstractproperty
    def _fields(self):
        """Имена полей, подлежащих загрузке.

        :rtype: tuple
        """

    @abstractproperty
    def _mapper_class(self):
        """Класс, преобразующий имена полей.

        ::rtype: m3_fias.data.ObjectMapper
        """

    def _load_page(self, params, page):
        params = params.copy()
        params['page'] = page

        drf_response = server.get(self._path, params, timeout=self.timeout)
        if drf_response.status_code == http_client.OK:
            result = drf_response.json()
        else:
            result = None

        return result

    def _process_object_data(self, drf_object_data):
        """Выполняет дополнительную обработку данных объекта ФИАС.

        :param dict drf_object_data: Данные объекта ФИАС, полученные с сервера
            django-rest-fias.
        """
        object_data = self._mapper_class(drf_object_data)
        return object_data

    def _build_result(self, object_data):
        """Формирует данные результирующего объекта ФИАС.

        Полученные данные включаются в результат загрузки.

        :param dict object_data: Данные объекта, полученные с сервера ФИАС и
            прошедшие обработку в методе ``_process_object_data``.

        :rtype: dict
        """
        return {
            field: object_data[field]
            for field in self._fields
        }

    @abstractmethod
    def _filter(self, object_data):
        """Возвращает True, если объект ФИАС должен попасть в загрузку.

        :rtype: bool
        """

    def _get_params(self):  # pylint: disable=no-self-use
        """Возвращает параметры запроса к серверу ФИАС.

        :rtype: dict
        """
        return {}

    def load_raw(self, page=None):
        """Возвращает данные адресных объектов в исходном виде.

        :param int page: Номера страницы для загрузки данных. Значение ``None``
            указывает на необходимость загрузки всех страниц.

        :rtype: generator
        """
        if page is None:
            pages = count(start=1)
        else:
            pages = range(page, page + 1)

        params = self._get_params()

        for page_number in pages:
            drf_data = self._load_page(params, page_number)
            if drf_data:
                for drf_object_data in drf_data['results']:
                    object_data = self._process_object_data(drf_object_data)
                    if self._filter(object_data):
                        yield object_data

                if not drf_data['next']:
                    break
            else:
                break

    def load_results(self, page=None):
        """Возвращает данные в соответствии с параметрами загрузчика.

        :param int page: Номера страницы для загрузки данных. Значение ``None``
            указывает на необходимость загрузки всех страниц.

        :rtype: itertools.imap
        """
        return map(self._build_result, self.load_raw(page))

    @abstractmethod
    def _sort_key(self, object_data):
        """Возвращает значение ключа для сортировки результатов загрузки.

        :param dict object_data: Данные загруженного объекта ФИАС.
        """

    def _process_result(self, data):
        """Обработка полученных после загрузки данных.

        :param tuple data: Кортеж словарей с данными загруженных объектов ФИАС.
        """
        return sorted(data, key=self._sort_key)

    def load(self, page=None):
        """Загружает данные с сервера ФИАС.

        :param int page: Номера страницы для загрузки данных. Значение ``None``
            указывает на необходимость загрузки всех страниц.

        :rtype: collections.Iterable
        """
        data = tuple(self.load_results(page))
        result = self._process_result(data)
        return result


class AddressObjectLoaderBase(LoaderBase):

    """Базовый класс для загрузчиков адресных объектов ФИАС.

    В терминологии ФИАС адресными объектами называются:

        * субъекты Федерации;
        * автономные округи;
        * районы субъектов Федерации;
        * города;
        * внутригородские территории;
        * населенные пункты;
        * элементы планировочной структуры;
        * дополнительные территории;
        * объекты, подчиненные дополнительным территориям;
        * улицы.
    """

    _path = '/'

    @cached_property
    def _fields(self):
        return list(self._mapper_class.fields_map.keys())

    @abstractproperty
    def _levels(self):
        """Уровни адресных объектов, для которых нужно искать данные в ФИАС.

        :rtype: tuple
        """

    def _get_params(self):
        """Возвращает параметры запроса к серверу ФИАС.

        :rtype: dict
        """
        result = super(AddressObjectLoaderBase, self)._get_params()
        result['scan'] = ','.join(
            word.replace('.', '')
            for word in self.filter_string.split()
        )
        if self._levels:
            result['aolevel'] = ','.join(map(str, self._levels))
        return result

    def _filter(self, object_data):
        return True

    def _sort_key(self, object_data):
        return object_data['fullName'] or ''


class AddressObjectLoader(AddressObjectLoaderBase):

    """Загрузчик адресных объектов ФИАС.

    Загружает информацию об адресных объектах, соответствующих строке
    фильтрации и находящихся на одном из указанных в параметрах экземпляра
    уровней иерархии адресных объектов.
    """

    _levels = None

    _mapper_class = AddressObjectMapper

    def __init__(self, filter_string, levels=None, parent_guid=None, **kwargs):
        """Инициализация экземпляра класса.

        :param unicode filter_string: Строка для фильтрации объектов.
        :param levels: Уровни адресных объектов.
        :param parent_guid: GUID родительского объекта.
        :param float timeout: Timeout запросов к серверу ФИАС в секундах.
        """
        super(AddressObjectLoader, self).__init__(filter_string, **kwargs)

        self._levels = levels
        self._parent_guid = _guid2str(parent_guid)

    def _get_params(self):
        result = super(AddressObjectLoader, self)._get_params()
        if self._parent_guid:
            result['parentguid'] = text_type(self._parent_guid)
        return result


class PlaceLoader(AddressObjectLoaderBase):

    """Загрузчик сведений о населенных пунктах.

    Загружает информацию об адресных объектах, соответствующих строке
    фильтрации, подчиненных указанному адресному объекту (опционально) и
    находящихся на одном из следующих уровней иерархии адресных объектов:

        * субъекты Федерации
          (:obj:`~m3_fias.constants.FIAS_LEVEL_REGION`);
        * автономные округи
          (:obj:`~m3_fias.constants.FIAS_LEVEL_AUTONOMUOS_DISTRICT`);
        * районы субъектов Федерации
          (:obj:`~m3_fias.constants.FIAS_LEVEL_DISTRICT`);
        * города
          (:obj:`~m3_fias.constants.FIAS_LEVEL_CITY`);
        * внутригородские территории
          (:obj:`~m3_fias.constants.FIAS_LEVEL_INTRACITY_TERRITORY`);
        * населенные пункты
          (:obj:`~m3_fias.constants.FIAS_LEVEL_SETTLEMENT`);
        * элементы планировочной структуры
          (:obj:`~m3_fias.constants.FIAS_LEVEL_PLANNING_STRUCTURE`);
        * дополнительные территории
          (:obj:`~m3_fias.constants.FIAS_LEVEL_ADDITIONAL_TERRITORY`).
    """

    _levels = FIAS_LEVELS_PLACE

    _mapper_class = UIAddressObjectMapper


class StreetLoader(AddressObjectLoaderBase):

    """Загрузчик сведений об улицах.

    Загружает информацию об адресных объектах, соответствующих строке
    фильтрации, подчиненных указанному адресному объекту (опционально) и
    находящихся на одном из следующих уровней иерархии адресных объектов:

        * улицы
          (:obj:`~m3_fias.constants.FIAS_LEVEL_STREET`);
        * объекты, подчиненные дополнительным территориям
          (:obj:`~m3_fias.constants.FIAS_LEVEL_ADDITIONAL_TERRITORY_OBJECT`).
    """

    _levels = FIAS_LEVELS_STREET

    _mapper_class = UIAddressObjectMapper

    def __init__(self, filter_string, parent_guid, **kwargs):
        """Инициализация экземпляра класса.

        :param unicode filter_string: Строка для фильтрации объектов.
        :param basestring parent_guid: GUID адресного объекта, в котором
            находится улица.
        :param float timeout: Timeout запросов к серверу ФИАС в секундах.
        """
        super(StreetLoader, self).__init__(filter_string, **kwargs)

        self.parent_guid = _guid2str(parent_guid)

    def _get_params(self):
        result = super(StreetLoader, self)._get_params()
        result['parentguid'] = self.parent_guid
        return result


class HouseLoader(LoaderBase):

    """Загрузчик сведений о зданиях.

    Основными параметрами здания являются:

        * номер дома;
        * номер корпуса;
        * номер строения.

    .. note:

       Записи о домах фильтруются в приложении (в Python), а не на сервере
       django-rest-fias.
    """

    _mapper_class = UIHouseMapper

    _fields = (
        'guid',
        'houseNumber',
        'buildingNumber',
        'structureNumber',
        'postalCode',
    )

    def __init__(self, address_object_guid, filter_string, **kwargs):
        """Инициализация класса.

        :param basestring address_object_guid: GUID адресного объекта, в
            котором находится здание.

        :param filter_string: Строка для поиска здания по номеру
            дома/корпуса/строения. Содержит первые символы в номере. Значение
            ``None`` указывает на необходимость загрузки сведений обо всех
            зданиях адресного объекта.
        :type filter_string: unicode or NoneType
        :param float timeout: Timeout запросов к серверу ФИАС в секундах.
        """
        super(HouseLoader, self).__init__(
            filter_string.lower() if filter_string else None,
            **kwargs
        )

        self.address_object_guid = _guid2str(address_object_guid)

    @property
    def _path(self):
        return '/{}/houses'.format(self.address_object_guid)

    @staticmethod
    def _split_number(number):
        """Разделяет номер на целочисленную и буквенную части.

        :param unicode number: Номер дома/корпуса/строения.

        :rtype: tuple
        """
        int_part = ''.join(ch for ch in number if ch.isdigit())
        str_part = number[len(int_part):]

        return int(int_part) if int_part else -1, str_part

    def _sort_key(self, object_data):
        return tuple(chain(*(
            self._split_number(object_data[number_type + 'Number'])
            for number_type in ('house', 'building', 'structure')
        )))

    def _filter(self, object_data):
        """Возвращает True для записей, соответствующих параметрам поиска.

        Запись считается соответствующей указанным при инициализации загрузчика
        параметрам поиска, если:

            * номер дома (если есть) в записи **начинается со строки**,
              указанной в аргументе ``filter_string``;
            * номер корпуса или строения (если номер дома отсутствует) в записи
              **начинается со строки**, указанной в аргументе
              ``filter_string``;
            * в аргументе ``filter_string`` конструктора класса было передано
              значение ``None``.

        :rtype: bool
        """
        if self.filter_string is None:
            result = True
        else:
            house = (object_data.get('houseNumber') or '').lower()

            if house:
                result = house.startswith(self.filter_string)
            else:
                building = (object_data.get('buildingNumber') or '').lower()
                structure = (object_data.get('structureNumber') or '').lower()
                result = (
                    building and building.startswith(self.filter_string) or
                    structure and structure.startswith(self.filter_string)
                )
        return result

    def _process_object_data(self, drf_object_data):
        house_data = super(HouseLoader, self)._process_object_data(
            drf_object_data
        )

        house_data['houseNumber'] = house_data['houseNumber'] or ''
        house_data['buildingNumber'] = house_data['buildingNumber'] or ''
        house_data['structureNumber'] = house_data['structureNumber'] or ''

        return house_data
# -----------------------------------------------------------------------------
# Функции для создания объектов m3-fias на основе данных django-rest-fias.


def get_address_object(guid, timeout=None):
    """Возвращает адресный объект, загруженный с сервера ФИАС.

    Если адресный объект не найден, возвращает ``None``.

    :param guid: GUID адресного объекта ФИАС.
    :param float timeout: timeout запроса к серверу ФИАС в секундах.

    :rtype: m3_fias.data.AddressObject or NoneType

    :raises requests.ConnectionError: если не удалось соединиться с
        сервером ФИАС
    """
    guid = _guid2str(guid)
    assert guid is not None

    response = server.get('/{}/'.format(guid), timeout=timeout)
    if response.status_code == http_client.OK:
        response_data = response.json()
        mapped_data = AddressObjectMapper(response_data)
        result = AddressObject(**mapped_data)
    else:
        result = None

    return result


def find_address_objects(filter_string, levels=None,
                         parent_guid=None, timeout=None):
    """Возвращает адресные объекты, соответствующие параметрам поиска.

    :param unicode filter_string: Строка поиска.
    :param levels: Уровни адресных объектов, среди которых нужно
        осуществлять поиск.
    :param parent_guid: GUID родительского объекта.
    :param float timeout: Timeout запросов к серверу ФИАС в секундах.

    :rtype: generator
    """
    return AddressObjectLoader(
        filter_string, levels, parent_guid, timeout=timeout
    ).load_results()


def get_house(guid, ao_guid, timeout=None):
    """Возвращает информацию о здании по его GUID-у в ФИАС.

    .. important::

       В ФИАС здания с разными корпусами/строениями имеют разные GUID-ы.
       Например, "д.1 корп. 1" и "д.1 корп. 2" будут иметь разные
       идентификаторы.

    :param guid: GUID здания.
    :param ao_guid: GUID адресного объекта, в котором находится здание.
    :param float timeout: Timeout запросов к серверу ФИАС в секундах.

    :rtype: m3_fias.data.House
    """
    guid, ao_guid = _guid2str(guid), _guid2str(ao_guid)
    assert guid is not None
    assert ao_guid is not None

    response = server.get(
        '/{}/houses/{}/'.format(ao_guid, guid),
        timeout=timeout,
    )
    if response.status_code == http_client.OK:
        house_data = HouseMapper(response.json())
        result = House(**house_data)
    else:
        result = None

    return result


def find_house(ao_guid, house_number='', building_number='',
               structure_number='', timeout=None):
    """Возвращает информацию о здании по его номеру.

    :param ao_guid: GUID адресного объекта.
    :param unicode house_number: Номер дома.
    :param unicode building_number: Номер корпуса.
    :param unicode structure_number: Номер строения.
    :param float timeout: Timeout запросов к серверу ФИАС в секундах.

    :rtype: m3_fias.data.House or NoneType
    """
    assert house_number or building_number or structure_number, (
        house_number, building_number, structure_number
    )

    houses = tuple(
        house_info['guid']
        for house_info in HouseLoader(
            ao_guid,
            house_number or building_number or structure_number,
            timeout=timeout,
        ).load()
        if (
            house_info['guid'] and
            house_info['houseNumber'] == (house_number or '') and
            house_info['buildingNumber'] == (building_number or '') and
            house_info['structureNumber'] == (structure_number or '')
        )
    )

    if len(houses) == 1:
        result = get_house(houses[0], ao_guid, timeout)
    else:
        result = None

    return result
# -----------------------------------------------------------------------------
