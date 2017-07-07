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


#: Конфигурация приложения ``m3_fias``.
config = None
