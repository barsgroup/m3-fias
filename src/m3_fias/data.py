# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractproperty
from collections import Mapping
from collections import MutableMapping
from collections import namedtuple
from datetime import date
from datetime import datetime
from functools import partial
from uuid import UUID

from six import iteritems
from six import iterkeys
from six import text_type
from six import with_metaclass

from m3_fias.constants import FIAS_LEVELS


FieldDescriptor = namedtuple('FieldDescriptor', ' '.join((
    'data_type',
    'required',
    'description'
)))


class ReadOnlyAttribute(object):

    def __init__(self, name, doc=None):
        self._name = name
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        return obj.__dict__[self._name] if obj else self

    def __set__(self, obj, value):
        raise AttributeError('{} is read only attribute'.format(self._name))

    def __delete__(self, obj):
        raise AttributeError('{} is read only attribute'.format(self._name))


class ObjectMeta(ABCMeta):

    def __new__(mcs, name, bases, namespace, **kwargs):  # @NoSelf
        cls = ABCMeta.__new__(mcs, name, bases, namespace)

        fields = namespace['fields']
        if isinstance(fields, dict):
            for field_name, field_descriptor in iteritems(fields):
                setattr(cls, field_name, ReadOnlyAttribute(
                    name=field_name,
                    doc=field_descriptor.description,
                ))

        return cls


class ObjectBase(with_metaclass(ObjectMeta, object)):

    """Базовый класс для объектов ФИАС.

    Обеспечивает неизменяемость данных (объекты только для чтения).
    """

    @abstractproperty
    def fields(self):
        """Описание полей объекта."""

    def __hash__(self):
        return hash(self.id)  # pylint: disable=no-member

    def __init__(self, **kwargs):
        for field_name, field_descriptor in iteritems(self.fields):
            if field_descriptor.required:
                if field_name in kwargs:
                    field_value = kwargs[field_name]
                else:
                    raise TypeError(
                        'argument {} is required'.format(field_name)
                    )
            else:
                field_value = kwargs.get(field_name, None)

            if field_value and field_descriptor.data_type:
                try:
                    field_value = field_descriptor.data_type(field_value)
                except ValueError:
                    raise ValueError('{} = {}'.format(field_name, field_value))

            self.__dict__[field_name] = field_value


# dict в списке базовых классов нужен для правильной обработки данных в M3.
class ObjectDictAdapter(Mapping, dict):

    """Адаптер для объектов ФИАС, преобразующий их к словарям."""

    def __init__(self, obj):  # pylint: disable=super-init-not-called
        """Инициализация экземпляра класса.

        :type obj: m3_fias.data.ObjectBase
        """
        assert isinstance(obj, ObjectBase), type(obj)
        self._obj = obj

    def __iter__(self):
        return iter(self._obj.fields)

    def __getitem__(self, key):
        return getattr(self._obj, key)

    def __len__(self):
        return len(self._obj.fields)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Переопределение методов, изменяющих данные (объект только для чтения).

    # pylint: disable=unused-argument
    @property
    def __readonly_exception(self):
        return TypeError("'{}' object is readonly".format(
            self.__class__.__name__
        ))

    def __setitem__(self, key, value):
        raise self.__readonly_exception

    def __delitem__(self, key):
        raise self.__readonly_exception

    def pop(self, *args):
        raise self.__readonly_exception

    def popitem(self):
        raise self.__readonly_exception

    def clear(self):
        raise self.__readonly_exception

    def update(self, *args, **kwargs):
        raise self.__readonly_exception

    def setdefault(self, key, default=None):
        raise self.__readonly_exception

    # pylint: enable=unused-argument
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def _unicode(value):
    return value if isinstance(value, text_type) else text_type(value)


def _unicode_or_empty(value):
    return _unicode(value) if value else ''


def _int(value):
    try:
        return int(value if isinstance(value, int) else int(value))
    except (TypeError, ValueError):
        raise ValueError(value)


def _int_or_none(value):
    return _int(value) if value else None


def _uuid(value):
    try:
        return text_type(value if isinstance(value, UUID) else UUID(value))
    except (AttributeError, TypeError, ValueError):
        raise ValueError(value)


def _uuid_or_none(value):
    return _uuid(value) if value else None


def _date(value):
    if isinstance(value, date):
        result = value
    else:
        try:
            result = datetime.strptime(value, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            raise ValueError(value)

    return result


def _choices(valid_values, value_type, raw_value):
    value = value_type(raw_value)
    if value in valid_values:
        return value
    else:
        raise ValueError(raw_value)


class AddressObject(ObjectBase):

    """Адресный объект."""

    #: Поля объекта и признак обязательности значения.
    fields = {
        'id': FieldDescriptor(
            _uuid,
            True,
            'Уникальный идентификатор записи (ключевое поле).',
        ),
        'previous_id': FieldDescriptor(
            _uuid_or_none,
            False,
            'Идентификатор записи связывания с предыдушей исторической '
            'записью.',
        ),
        'next_id': FieldDescriptor(
            _uuid_or_none,
            False,
            'Идентификатор записи  связывания с последующей исторической '
            'записью.',
        ),
        'guid': FieldDescriptor(
            _uuid,
            True,
            'Глобальный уникальный идентификатор адресного объекта.',
        ),
        'parent_guid': FieldDescriptor(
            _uuid_or_none,
            False,
            'Идентификатор родительского объекта.',
        ),
        'level': FieldDescriptor(
            partial(_choices, FIAS_LEVELS, _int),
            True,
            'Уровень адресного объекта.',
        ),
        'ifns_fl_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код ИФНС для физических лиц.',
        ),
        'ifns_fl_territorial_district_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код территориального участка ИФНС ФЛ.',
        ),
        'ifns_ul_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код ИФНС для юридических лиц.',
        ),
        'ifns_ul_territorial_district_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код территориального участка ИФНС ЮЛ.',
        ),
        'okato': FieldDescriptor(
            _unicode_or_empty,
            False,
            'ОКАТО.',
        ),
        'oktmo': FieldDescriptor(
            _unicode_or_empty,
            False,
            'ОКТМО.',
        ),
        'kladr_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код адресного объекта одной строкой с признаком актуальности из '
            'КЛАДР 4.0.',
        ),
        'kladr_plain_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код адресного объекта из КЛАДР 4.0 одной строкой без признака '
            'актуальности (последних двух цифр).',
        ),
        'kladr_status': FieldDescriptor(
            _unicode,
            True,
            'Статус актуальности КЛАДР 4 (последние две цифры в коде).',
        ),
        'actual': FieldDescriptor(
            bool,
            True,
            'Статус последней исторической записи в жизненном цикле адресного '
            'объекта: 0 – Не последняя, 1 - Последняя'
        ),
        'centre': FieldDescriptor(
            _int,
            True,
            'Статус центра',
        ),
        'operation': FieldDescriptor(
            _int,
            True,
            'Статус действия над записью – причина появления записи',
        ),
        'region_code': FieldDescriptor(
            _unicode,
            True,
            'Код региона',
        ),
        'autonomy_code': FieldDescriptor(
            _unicode,
            True,
            'Код автономии',
        ),
        'area_code': FieldDescriptor(
            _unicode,
            True,
            'Код района',
        ),
        'city_code': FieldDescriptor(
            _unicode,
            True,
            'Код города',
        ),
        'city_area_code': FieldDescriptor(
            _unicode,
            True,
            'Код внутригородского района',
        ),
        'place_code': FieldDescriptor(
            _unicode,
            True,
            'Код населенного пункта',
        ),
        'street_code': FieldDescriptor(
            _unicode,
            True,
            'Код улицы',
        ),
        'extra_code': FieldDescriptor(
            _unicode,
            True,
            'Код дополнительного адресообразующего элемента',
        ),
        'secondary_extra_code': FieldDescriptor(
            _unicode,
            True,
            'Код подчиненного дополнительного адресообразующего элемента',
        ),
        'short_name': FieldDescriptor(
            _unicode,
            True,
            'Краткое наименование типа объекта',
        ),
        'official_name': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Официальное наименование',
        ),
        'formal_name': FieldDescriptor(
            _unicode,
            True,
            'Формализованное наименование',
        ),
        'postal_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Почтовый индекс',
        ),
        'date_of_creation': FieldDescriptor(
            _date,
            True,
            'Начало действия записи',
        ),
        'date_of_update': FieldDescriptor(
            _date,
            True,
            'Дата  внесения (обновления) записи',
        ),
        'date_of_expiration': FieldDescriptor(
            _date,
            True,
            'Окончание действия записи',
        ),
        'normative_document_guid': FieldDescriptor(
            _uuid_or_none,
            False,
            'Внешний ключ (GUID) на нормативный документ',
        ),
        'live_status': FieldDescriptor(
            _int,
            True,
            'Статус актуальности адресного объекта ФИАС на текущую дату: '
            '0 – Не актуальный, 1 - Актуальный',
        ),
        'full_name': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Полный адрес',
        ),
    }


class House(ObjectBase):

    """Дом."""

    fields = {
        'id': FieldDescriptor(
            _uuid,
            True,
            'Уникальный идентификатор записи дома',
        ),
        'guid': FieldDescriptor(
            _uuid,
            True,
            'Глобальный уникальный идентификатор дома',
        ),
        'parent_guid': FieldDescriptor(
            _uuid,
            True,
            'Идентификатор родительского объекта (улицы, города, населенного '
            'пункта и т.п.)'
        ),
        'ifns_fl_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код ИФНС для физических лиц.',
        ),
        'ifns_fl_territorial_district_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код территориального участка ИФНС ФЛ.',
        ),
        'ifns_ul_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код ИФНС для юридических лиц.',
        ),
        'ifns_ul_territorial_district_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Код территориального участка ИФНС ЮЛ.',
        ),
        'okato': FieldDescriptor(
            _unicode_or_empty,
            False,
            'ОКАТО.',
        ),
        'oktmo': FieldDescriptor(
            _unicode_or_empty,
            False,
            'ОКТМО.',
        ),
        'postal_code': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Почтовый индекс',
        ),
        'house_number': FieldDescriptor(
            _unicode,
            True,
            'Номер дома',
        ),
        'estate_status': FieldDescriptor(
            _int,
            True,
            'Признак владения',
        ),
        'building_number': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Номер корпуса',
        ),
        'structure_number': FieldDescriptor(
            _unicode_or_empty,
            False,
            'Номер строения',
        ),
        'structure_status': FieldDescriptor(
            _int,
            True,
            'Статус строения',
        ),
        'kladr_counter': FieldDescriptor(
            _int_or_none,
            False,
            'Счетчик записей домов для КЛАДР 4',
        ),
        'date_of_creation': FieldDescriptor(
            _date,
            True,
            'Начало действия записи',
        ),
        'date_of_update': FieldDescriptor(
            _date,
            True,
            'Дата  внесения (обновления) записи',
        ),
        'date_of_end': FieldDescriptor(
            _date,
            True,
            'Окончание действия записи',
        ),
        'state_status': FieldDescriptor(
            _int,
            True,
            'Состояние дома',
        ),
        'normative_document_guid': FieldDescriptor(
            _uuid_or_none,
            False,
            'Внешний ключ (GUID) на нормативный документ',
        ),
    }


class ObjectMapper(with_metaclass(ABCMeta, MutableMapping)):

    """Обертка над словарями, преобразующая ключи."""

    @abstractproperty
    def fields_map(self):
        """Список соответствия ключей.

        :rtype: dict
        """

    def __init__(self, data):  # pylint: disable=super-init-not-called
        assert isinstance(data, dict), type(data)

        self._data = data

    def __len__(self):
        i = 0
        for i, _ in enumerate(iterkeys(self), 1):
            pass
        return i

    def __iter__(self):
        return (
            key
            for key, mapped_key in iteritems(self.fields_map)
            if mapped_key in self._data
        )

    def __getitem__(self, key):
        return self._data[self.fields_map[key]]

    def __setitem__(self, key, value):
        self._data[self.fields_map[key]] = value

    def __delitem__(self, key):
        del self._data[self.fields_map[key]]

    def __bool__(self):
        return bool(self._data)
    __nonzero__ = __bool__
