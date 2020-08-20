# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractproperty
import hashlib
import json

from django.utils.functional import SimpleLazyObject
from requests import Session
from six import with_metaclass
from six.moves import http_client

from m3_fias.utils import cached_property


class ServerBase(with_metaclass(ABCMeta, object)):

    """Базовый класс для серверов ФИАС."""

    def __init__(self, **kwargs):
        self._base_url = kwargs['url']
        self._timeout = kwargs.get('timeout')

    @property
    def base_url(self):
        return self._base_url

    @abstractproperty
    def _session(self):
        """HTTP-сессия с серверов django-rest-fias.

        :rtype: requests.sessions.Session
        """

    def get(self, path, params=None, timeout=None):
        """Возвращает ответ на HTTP-запрос к API сервера ФИАС.

        :rtype: requests.models.Response
        """
        response = self._session.get(
            self.base_url.rstrip('/') + path,
            params=params or {},
            timeout=timeout or self._timeout,
        )
        return response


class CachingMixin(object):

    """Класс-примесь для кэширования ответов на запросы.

    Параметры:

        * ``cache`` --- объект кэша. Рекомендуется использовать
          ```django.core.cache.cache`.
        * ``cache_key_prefix`` --- префикс для ключей в кэше.
        * ``cache_timeout`` --- длительность кэширования (в секундах).
    """

    def __init__(self, **kwargs):
        super(CachingMixin, self).__init__(**kwargs)

        self._cache = kwargs['cache']
        self._cache_key_prefix = kwargs.get('cache_key_prefix', 'm3-fias')
        self._cache_timeout = kwargs.get('cache_timeout', 24 * 60 * 60)

    def get(self, path, params=None, timeout=None):
        hasher = hashlib.sha1()
        hasher.update(':'.join((
            self._cache_key_prefix,
            path,
            json.dumps(params, sort_keys=True)
        )).encode('utf-8'))
        cache_key = hasher.hexdigest()
        if cache_key in self._cache:
            response = self._cache.get(cache_key)
        else:
            response = super(CachingMixin, self).get(path, params, timeout)

            if response.status_code == http_client.OK:
                self._cache.set(cache_key, response,)

        return response


class SimpleServer(ServerBase):

    """Сервер ФИАС без аутентификации.

    Параметры:

        * ``url`` --- URL API сервера ФИАС.
        * ``timeout`` --- timeout запроса к серверу ФИАС в секундах.
    """

    @cached_property
    def _session(self):
        result = Session()

        result.trust_env = True

        return result


class SimpleCachingServer(CachingMixin, SimpleServer):

    u"""Сервер ФИАС с кешированием без аутентификации.

    Параметры:

        * ``url`` --- URL API сервера ФИАС.
        * ``timeout`` --- timeout запроса к серверу ФИАС в секундах.
        * ``cache`` --- объект кэша. Рекомендуется использовать
          ```django.core.cache.cache`.
        * ``cache_key_prefix`` --- префикс для ключей в кэше.
        * ``cache_timeout`` --- длительность кэширования (в секундах).
    """


class OAuth2Server(ServerBase):  # pragma: no cover

    """Сервер ФИАС с аутентификацией OAuth2.

    Параметры:

        * ``url`` --- URL API сервера ФИАС.
        * ``timeout`` --- timeout запроса к серверу ФИАС в секундах.
        * ``token_url`` --- Token endpoint URL, must use HTTPS.
        * ``client_id``.
        * ``user_name`` --- Username used by LegacyApplicationClients..
        * ``password`` --- Password used by LegacyApplicationClients..
        * ``client_secret``.

    .. seealso::

       :meth:`requests_oauthlib.OAuth2Session.fetch_token`
    """

    def __init__(self, **kwargs):
        super(OAuth2Server, self).__init__(**kwargs)

        self.token_url = kwargs['token_url']
        self.client_id = kwargs['client_id']
        self.user_name = kwargs['user_name']
        self.password = kwargs['password']
        self.client_secret = kwargs['client_secret']

    @cached_property
    def _session(self):
        from requests_oauthlib import OAuth2Session
        from oauthlib.oauth2 import LegacyApplicationClient

        result = OAuth2Session(
            client=LegacyApplicationClient(self.client_id)
        )
        result.trust_env = True
        result.fetch_token(
            token_url=self.token_url,
            username=self.user_name,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        return result


class OAuth2CachingServer(CachingMixin, OAuth2Server):

    """Сервер ФИАС с кешированием и аутентификацией OAuth2.

    Параметры:

        * ``url`` --- URL API сервера ФИАС.
        * ``timeout`` --- timeout запроса к серверу ФИАС в секундах.
        * ``token_url`` --- Token endpoint URL, must use HTTPS.
        * ``client_id``.
        * ``user_name`` --- Username used by LegacyApplicationClients..
        * ``password`` --- Password used by LegacyApplicationClients..
        * ``client_secret``.
        * ``cache`` --- объект кэша. Рекомендуется использовать
          ```django.core.cache.cache`.
        * ``cache_key_prefix`` --- префикс для ключей в кэше.
        * ``cache_timeout`` --- длительность кэширования (в секундах).

    .. seealso::

       :meth:`requests_oauthlib.OAuth2Session.fetch_token`
    """


def get_server():
    """Возвращает сервер ФИАС, созданный в соответствии с настройками m3-fias.

    Параметры подключения к серверу django-rest-fias должны быть размещены в
    настройках Django (``django.conf.settings``) в параметре ``FIAS``, который
    должен содержать словарь со следующими ключами:

        - ``URL`` --- URL API сервера ФИАС.
        - ``TIMEOUT`` --- timeout запроса к серверу ФИАС в секундах.
        - ``USE_CACHE`` --- определяет необходимость кеширования HTTP-запросов
          к серверу django-rest-fias. Значение по умолчанию: ``False``
        - ``OAUTH2`` --- параметры OAuth2 (если не указан, то аутентификация
          не используется):

          - ``TOKEN_URL`` --- Token endpoint URL, must use HTTPS.
          - ``CLIENT_ID``
          - ``USER_NAME``
          - ``PASSWORD``
          - ``CLIENT_SECRET``

    :rtype: m3_fias.backends.django_rest_fias.ServerBase
    """
    from django.conf import settings

    if settings.FIAS.get('USE_CACHE', False):
        from django.core.cache import cache

        if 'OAUTH2' in settings.FIAS:  # pragma: no cover
            result = OAuth2CachingServer(
                url=settings.FIAS['URL'],
                timeout=settings.FIAS.get('TIMEOUT'),
                cache=cache,
                token_url=settings.FIAS['OAUTH2']['TOKEN_URL'],
                client_id=settings.FIAS['OAUTH2']['CLIENT_ID'],
                user_name=settings.FIAS['OAUTH2'].get('USER_NAME'),
                password=settings.FIAS['OAUTH2'].get('PASSWORD'),
                client_secret=settings.FIAS['OAUTH2'].get('CLIENT_SECRET'),
            )

        else:
            result = SimpleCachingServer(
                url=settings.FIAS['URL'],
                timeout=settings.FIAS.get('TIMEOUT'),
                cache=cache,
            )

    else:
        if 'OAUTH2' in settings.FIAS:  # pragma: no cover
            result = OAuth2Server(
                url=settings.FIAS['URL'],
                timeout=settings.FIAS.get('TIMEOUT'),
                token_url=settings.FIAS['OAUTH2']['TOKEN_URL'],
                client_id=settings.FIAS['OAUTH2']['CLIENT_ID'],
                user_name=settings.FIAS['OAUTH2'].get('USER_NAME'),
                password=settings.FIAS['OAUTH2'].get('PASSWORD'),
                client_secret=settings.FIAS['OAUTH2'].get('CLIENT_SECRET'),
            )

        else:
            result = SimpleServer(
                url=settings.FIAS['URL'],
                timeout=settings.FIAS.get('TIMEOUT'),
            )

    return result


server = SimpleLazyObject(get_server)
