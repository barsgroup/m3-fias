# coding: utf-8
# pylint: disable=import-error
from __future__ import absolute_import
from __future__ import unicode_literals

from contextlib import closing
from os.path import dirname
from os.path import join
from threading import Thread
import json

from django.conf import settings
from six import iteritems
from six import text_type
from six.moves import http_client
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler
from six.moves.BaseHTTPServer import HTTPServer
from six.moves.urllib.parse import parse_qs
from six.moves.urllib.parse import unquote
from six.moves.urllib.parse import urlparse

from m3_fias.utils import cached_property


class DjangoRestFiasServerMock(BaseHTTPRequestHandler):

    """HTTP-сервер, имитирующий сервер django-rest-fias."""

    def log_request(self, code='-', size='-'):
        pass

    @staticmethod
    def _get_file_content(file_name):
        file_path = join(dirname(__file__), file_name)
        with open(file_path, 'r') as infile:
            return json.load(infile)

    @cached_property
    def _files_map(self):
        """Соответствие между запросами и именами файлов с ответами.

        Данные загружаются из файла ``map.json``.
        """
        return self._get_file_content('map.json')

    @staticmethod
    def _parse_path(path):
        """Возвращает путь и параметры HTTP-запроса."""
        if not isinstance(path, text_type):
            path = text_type(path, 'utf-8')
        parsed_path = urlparse(path)
        params = parse_qs(parsed_path.query)
        return parsed_path.path, params

    def _get_file_name(self):
        """Возвращает путь к файлу, соответствующему пути в HTTP-запросе.

        :rtype: unicode
        """
        parsed_request_path = self._parse_path(unquote(self.path))

        for path, file_name in iteritems(self._files_map):
            if parsed_request_path == self._parse_path(path):
                return file_name

    def do_GET(self):
        response_file_name = self._get_file_name()

        if response_file_name is None:
            self.send_response(http_client.NOT_FOUND, 'NOT FOUND')
            self.end_headers()
        else:
            self.send_response(http_client.OK, 'OK')
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()

            response_data = self._get_file_content(response_file_name)

            drf_url = 'http://fias.bars-open.ru/fias/v1/ao'
            if (
                isinstance(response_data, dict) and
                'next' in response_data and
                response_data['next'] and
                response_data['next'].startswith(drf_url)
            ):
                response_data['next'] = (
                    settings.FIAS['URL'] + response_data['next'][len(drf_url):]
                )

            self.wfile.write(json.dumps(response_data).encode('utf-8'))
