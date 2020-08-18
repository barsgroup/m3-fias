# coding: utf-8
"""Бэкенд, проксирующий запросы через веб-приложение."""
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import abstractmethod
from uuid import UUID

from m3.actions import ControllerCache
from m3_ext.ui.misc.store import ExtJsonStore
from six import text_type

from m3_fias.backends.base import BackendBase
from m3_fias.utils import cached_property

from .utils import find_address_objects
from .utils import find_house
from .utils import get_address_object
from .utils import get_house


class Backend(BackendBase):

    """Бэкенд для работы с сервером django-rest-fias."""

    def __init__(self, *args, **kwargs):
        super(Backend, self).__init__(*args, **kwargs)

        self._pack = None

    @staticmethod
    def _register_parsers():
        """Регистрация парсеров для параметров контекста."""
        from m3.actions.context import DeclarativeActionContext

        params = (
            (
                'm3-fias:unicode-or-none',
                lambda s: text_type(s) if s else None
            ),
            (
                'm3-fias:int-list',
                lambda s: [int(x) for x in s.split(',')]
            ),
            (
                'm3-fias:guid',
                UUID
            ),
            (
                'm3-fias:guid-or-none',
                lambda x: UUID(x) if x else None
            ),
        )

        for name, parser in params:
            DeclarativeActionContext.register_parser(name, parser)

    def register_packs(self):
        """Регистрирует наборы действий в M3."""
        from m3_fias import config
        from .actions import Pack

        self._register_parsers()

        self._pack = Pack()

        config.controller.extend_packs((
            self._pack,
        ))

    def place_search_url(self):
        """URL для поиска населенных пунктов.

        :rtype: str
        """
        return self._pack.place_search_action.get_absolute_url()

    def street_search_url(self):
        """URL для поиска улиц.

        :rtype: str
        """
        return self._pack.street_search_action.get_absolute_url()

    def house_search_url(self):
        """URL для запроса списка домов.

        :rtype: str
        """
        return self._pack.house_search_action.get_absolute_url()

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
        return find_address_objects(filter_string, levels, parent_guid, timeout)

    def get_address_object(self, guid, timeout=None):
        """Возвращает адресный объект ФИАС по его GUID-у.

        :param guid: GUID адресного объекта ФИАС.
        :param float timeout: Timeout запросов к серверу ФИАС в секундах.

        :rtype: m3_fias.data.AddressObject
        """
        return get_address_object(guid, timeout)

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
        return find_house(
            ao_guid, house_number, building_number, structure_number, timeout
        )

    def get_house(self, guid, ao_guid, timeout=None):  # pylint: disable=signature-differs
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
        return get_house(guid, ao_guid, timeout)
