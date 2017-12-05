# coding: utf-8
from __future__ import unicode_literals

from BaseHTTPServer import HTTPServer
from threading import Thread

from django.conf import settings
from django_rest_fias.server_mock import DjangoRestFiasServerMock
from m3_fias.utils import cached_property
from test_project.controllers import controller
import m3_fias


def _is_drf_proxy():
    """Возвращает True, если используется бэкенд для django-rest-fias.

    :rtype: bool
    """
    backend = settings.FIAS['BACKEND']
    return backend == 'm3_fias.backends.django_rest_fias.proxy'


def _configure_m3_fias():
    if _is_drf_proxy():

        class Config(m3_fias.Config):

            @cached_property
            def controller(self):
                return controller

        m3_fias.config = Config()
    else:
        m3_fias.config = m3_fias.Config()


def _start_drf_server_mock():
    """Запускает mock-сервер, имитирующий django-rest-fias.

    Имитация используется при запуске тестов.
    """
    drf_server = HTTPServer(
        ('127.0.0.1', settings.DRF_SERVER_PORT), DjangoRestFiasServerMock
    )
    drf_thread = Thread(target=drf_server.serve_forever)
    drf_thread.setDaemon(True)
    drf_thread.start()


if m3_fias.config is None:
    _configure_m3_fias()

    if _is_drf_proxy() and settings.FIAS_DRF_SERVER_MOCK:
        _start_drf_server_mock()
