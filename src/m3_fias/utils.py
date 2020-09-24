# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from .data import AddressObject
from .data import House


class cached_property(property):

    """Кешируемое свойство.

    В отличие от :class:`django.utils.functional.cached_property`, наследуется
    от property и копирует строку документации, что актуально при генерации
    документации средствами Sphinx.
    """

    def __init__(self, method):
        super(cached_property, self).__init__(method)

        self.__doc__ = method.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.fget.__name__ not in instance.__dict__:
            instance.__dict__[self.fget.__name__] = self.fget(instance)

        return instance.__dict__[self.fget.__name__]


def correct_keyboard_layout(text):
    """При необходимости меняет раскладку клавиатуры.

    :param unicode text: Текстовая строка, подлежащая корректировке.

    :rtype: unicode
    """
    en_chars = (
        '`~@#$^&'
        'qwertyuiop[]'
        'QWERTYUIOP{}'
        'asdfghjkl;\''
        'ASDFGHJKL:"|'
        'zxcvbnm,./'
        'ZXCVBNM<>?'
    )
    ru_chars = (
        'ёЁ"№;:?'
        'йцукенгшщзхъ'
        'ЙЦУКЕНГШЩЗХЪ'
        'фывапролджэ'
        'ФЫВАПРОЛДЖЭ/'
        'ячсмитьбю.'
        'ЯЧСМИТЬБЮ,'
    )
    assert len(en_chars) == len(ru_chars)

    ru_only_chars = set(ru_chars) - set(en_chars)
    if set(text).isdisjoint(ru_only_chars):
        # Текст не содержит ни одного символа из русской раскладки, значит
        # раскладку надо поменять.

        def translate():
            for char in text:
                position = en_chars.find(char)
                yield char if position == -1 else ru_chars[position]

        result = ''.join(translate())
    else:
        result = text

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
    from m3_fias import config

    return config.backend.find_address_objects(
        filter_string, levels, parent_guid, timeout
    )


def get_address_object(guid, timeout=None):
    """Возвращает адресный объект ФИАС по его GUID-у.

    :param guid: GUID адресного объекта ФИАС.
    :param float timeout: Timeout запросов к серверу ФИАС в секундах.

    :rtype: m3_fias.data.AddressObject
    """
    from m3_fias import config

    return config.backend.get_address_object(guid, timeout)


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
    from m3_fias import config

    return config.backend.find_house(
        ao_guid, house_number, building_number, structure_number, timeout
    )


def get_house(guid, ao_guid=None, timeout=None):
    """Возвращает информацию о здании по его GUID-у в ФИАС.

    .. important::

       В ФИАС здания с разными корпусами/строениями имеют разные GUID-ы.
       Например, "д.1 корп. 1" и "д.1 корп. 2" будут иметь разные
       идентификаторы.

    :param guid: GUID здания.
    :param ao_guid: GUID адресного объекта, в котором находится здание.
        Необходимость указывать GUID определяется используемым бэкендом.
    :param float timeout: Timeout запросов к серверу ФИАС в секундах.

    :rtype: m3_fias.data.House
    """
    from m3_fias import config

    return config.backend.get_house(guid, ao_guid, timeout)


def get_address_object_name(address_object):
    """Возвращает наименование объекта с кратким наименованием его типа.

    Примеры:

      * Забайкальский край
      * ул. Ленина
      * г. Казань

    :type address_object: m3_fias.data.AddressObject

    :rtype: unicode
    """
    if address_object.guid == 'd66e5325-3a25-4d29-ba86-4ca351d9704b':
        # Ханты-Мансийский Автономный округ - Югра
        result = address_object.formal_name
    elif address_object.short_name in ('край', 'АО', 'Аобл', 'обл'):
        result = '{} {}'.format(
            address_object.formal_name, address_object.short_name
        )
    else:
        result = '{}. {}'.format(
            address_object.short_name, address_object.formal_name
        )

    return result


def get_house_name(house):
    """Возвращает полное наименование здания.

    Примеры:

      * д. 1
      * д. 2 корп. 3
      * корп. 5
      * д. 4 стр. 5
      * стр. 9
      * д. 6 корп. 7 стр. 8

    :type house: m3_fias.data.House

    :rtype: unicode
    """
    assert isinstance(house, House), type(house)

    names = []
    if house.house_number:
        names.append('д. ' + house.house_number)
    if house.building_number:
        names.append('корп. ' + house.building_number)
    if house.structure_number:
        names.append('стр. ' + house.structure_number)

    return ', '.join(names)


def get_full_name(obj, timeout=None):
    """Возвращает полное наименование адресного объекта или здания.

    Примеры:

      * Забайкальский край, г. Чита
      * Новосибирская обл., г. Новосибирск, ул. Вокзальная магистраль, д. 1/1
      * д. 1 корп. 3 стр. 2

    :type obj: m3_fias.data.AddressObject or m3_fias.data.House
    :param float timeout: Timeout запросов к серверу ФИАС в секундах.

    :rtype: unicode
    """
    postal_code = None
    names = []

    if not isinstance(obj, (House, AddressObject)):
        raise TypeError(obj)

    if isinstance(obj, House):
        if obj.postal_code:
            postal_code = obj.postal_code

        names.append(get_house_name(obj))

        obj = get_address_object(obj.parent_guid, timeout)

    if isinstance(obj, AddressObject):
        while obj:
            if postal_code is None and obj.postal_code:
                postal_code = obj.postal_code

            names.insert(0, get_address_object_name(obj))

            if obj.parent_guid:
                obj = get_address_object(obj.parent_guid, timeout)
            else:
                break

    if postal_code is not None:
        names.insert(0, postal_code)

    return ', '.join(names)
