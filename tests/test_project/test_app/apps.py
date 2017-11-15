# coding: utf-8
from __future__ import unicode_literals

from BaseHTTPServer import HTTPServer
from importlib import import_module
from threading import Thread

from django import apps
from django.conf import settings

from m3_fias.utils import cached_property
import m3_fias


class AppConfig(apps.AppConfig):

    name = __package__

    @staticmethod
    def _is_drf_proxy():
        """Возвращает True, если используется бэкенд для django-rest-fias.

        :rtype: bool
        """
        backend = settings.FIAS['BACKEND']
        return backend == 'm3_fias.backends.django_rest_fias.proxy'

    def _init_m3_fias(self):
        """Настраивает django-приложение m3-fias."""
        if self._is_drf_proxy():
            class Config(m3_fias.Config):
                @cached_property
                def controller(self):
                    from ..controllers import controller
                    return controller
        else:
            Config = m3_fias.Config

        m3_fias.config = Config()

    def _start_drf_server_mock(self):
        """Запускает mock-сервер, имитирующий django-rest-fias.

        Имитация используется при запуске тестов.
        """
        from django_rest_fias.server_mock import DjangoRestFiasServerMock

        self.drf_server = HTTPServer(
            ('127.0.0.1', settings.DRF_SERVER_PORT), DjangoRestFiasServerMock
        )
        self.drf_thread = Thread(target=self.drf_server.serve_forever)
        self.drf_thread.setDaemon(True)
        self.drf_thread.start()

    def ready(self):
        super(AppConfig, self).ready()

        self._init_m3_fias()

        if self._is_drf_proxy() and settings.FIAS_DRF_SERVER_MOCK:
            self._start_drf_server_mock()
