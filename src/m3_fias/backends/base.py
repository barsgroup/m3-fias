# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

from six import with_metaclass


class BackendBase(with_metaclass(ABCMeta, object)):

    """Базовый класс для бэкендов."""

    @abstractproperty
    def place_search_url(self):
        """URL для поиска населенных пунктов.

        :rtype: str
        """

    @abstractproperty
    def street_search_url(self):
        """URL для поиска улиц.

        :rtype: str
        """

    @abstractproperty
    def house_search_url(self):
        """URL для запроса списка домов.

        :rtype: str
        """

    def configure_place_field(self, field):
        """Настраивает поле "Населенный пункт".

        :param field: Поле "Населенный пункт".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    def configure_street_field(self, field):
        """Настраивает поле "Улица".

        :param field: Поле "Улица".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    def configure_house_field(self, field):
        """Настраивает поле "Дом".

        :param field: Поле "Дом".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    @abstractmethod
    def find_address_objects(self, filter_string, levels=None,
                             parent_guid=None, timeout=None):
        """Возвращает адресные объекты, соответствующие параметрам поиска.

        :param unicode filter_string: Строка поиска.
        :param levels: Уровни адресных объектов, среди которых нужно
            осуществлять поиск.
        :param parent_guid: GUID родительского объекта.
        :param float timeout: Timeout запросов к серверу ФИАС в секундах.

        :rtype: generator
        """

    @abstractmethod
    def get_address_object(self, guid, timeout=None):
        """Возвращает адресный объект ФИАС по его GUID-у.

        :param guid: GUID адресного объекта ФИАС.
        :param float timeout: Timeout запросов к серверу ФИАС в секундах.

        :rtype: m3_fias.data.AddressObject
        """

    @abstractmethod
    def find_house(self, ao_guid, house_number, building_number='',
                   structure_number='', timeout=None):
        """Возвращает информацию о здании по его номеру.

        :param ao_guid: GUID адресного объекта.
        :param unicode house_number: Номер дома.
        :param unicode building_number: Номер корпуса.
        :param unicode structure_number: Номер строения.
        :param float timeout: Timeout запросов к серверу ФИАС в секундах.

        :rtype: m3_fias.data.House or NoneType
        """

    @abstractmethod
    def get_house(self, guid, ao_guid=None, timeout=None):
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
