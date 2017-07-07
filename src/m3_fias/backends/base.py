# coding: utf-8
from abc import ABCMeta
from abc import abstractproperty


class BackendBase(object):

    u"""Базовый класс для бэкендов."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_address_panel(self):
        u"""Возвращает панель для ввода адреса."""

    @abstractproperty
    def address_object_url(self):
        u"""URL для запроса параметров адресного объекта.

        Для запрос информации о здании следует использовать :attr:`house_url`.

        :rtype: str
        """

    @abstractproperty
    def house_url(self):
        u"""URL для запроса параметров здания.

        :rtype: str
        """

    @abstractproperty
    def search_url(self):
        u"""URL для поисковых запросов.

        :rtype: str
        """
