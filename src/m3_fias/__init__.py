# coding: utf-8
import abc


class Config(object):

    u"""Базовый класс для конфигурации пакета."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def controller(self):
        u"""Контроллер, в котором будут регистрироваться паки приложения.

        :rtype: :class:`m3.actions.ActionController`
        """

    @abc.abstractproperty
    def backend(self):
        u"""Бэкенд для доступа к данным ФИАС.

        :rtype: :class:`m3_fias.backends.base.BackendBase`
        """


#: Конфигурация приложения ``m3_fias``.
config = None
