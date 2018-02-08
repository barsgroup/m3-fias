# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from importlib import import_module
import abc

from django.conf import settings
from six import with_metaclass

from .utils import cached_property


class Config(with_metaclass(abc.ABCMeta, object)):

    """Базовый класс для конфигурации пакета."""

    @cached_property
    def backend(self):
        """Бэкенд для доступа к данным ФИАС.

        :rtype: :class:`m3_fias.backends.base.BackendBase`
        """
        backend_class = import_module(settings.FIAS['BACKEND']).Backend
        return backend_class()


#: Конфигурация приложения ``m3_fias``.
#:
#: Заполняется экземпляром класса :class:`m3_fias.Config`, либо его потомком,
#: при инициализации проекта *до* инициализации приложения ``m3-fias``.
config = None
