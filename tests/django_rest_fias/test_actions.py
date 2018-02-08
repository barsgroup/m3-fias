# coding: utf-8
# pylint: disable=protected-access
from __future__ import absolute_import
from __future__ import unicode_literals

from unittest import skipUnless
import json

from django import test
from django.conf import settings
from django.test import Client
from six.moves import http_client

from m3_fias.backends.django_rest_fias.proxy.utils import HouseLoader
from m3_fias.backends.django_rest_fias.proxy.utils import PlaceLoader
from m3_fias.backends.django_rest_fias.proxy.utils import StreetLoader


@skipUnless(
    settings.FIAS['BACKEND'] == 'm3_fias.backends.django_rest_fias.proxy',
    'Another backend used'
)
class TestCase(test.SimpleTestCase):

    """Проверка обработчиков действий, обеспечивающих поддержку панели ввода.

    Про вводе данных в поля "Населенный пункт", "Улица" и "Дом" осуществляется
    поиск данных, соответствующих введенной строке, на сервере
    django-rest-fias.
    """

    def test__place_search_action(self):
        """Проверка PlaceSearchAction."""
        client = Client()

        response = client.post('/actions/fias/search/place', dict(
            # Запрос населенных пунктов, в наименовании которых содержится
            # "лени".
            filter='лени',
        ))

        self.assertEqual(response.status_code, http_client.OK)
        response_data = json.loads(response.content)
        self.assertIn('total', response_data)
        self.assertIsInstance(response_data['total'], int)
        self.assertIn('rows', response_data)
        self.assertIsInstance(response_data['rows'], list)
        self.assertEqual(
            len(response_data['rows']), response_data['total']
        )

        for row_data in response_data['rows']:
            self.assertIsInstance(row_data, dict)
            for name in PlaceLoader._mapper_class.fields_map:
                self.assertIn(name, row_data)

    def test__street_search_action(self):
        """Проверка StreetSearchAction."""
        client = Client()

        response = client.post('/actions/fias/search/street', dict(
            # Запрос улиц, в наименовании которых содержится "ленина"
            # в г. Новосибирске.
            parent='8dea00e3-9aab-4d8e-887c-ef2aaa546456',
            filter='ленина',
        ))

        self.assertEqual(response.status_code, http_client.OK)
        response_data = json.loads(response.content)
        self.assertIn('total', response_data)
        self.assertIsInstance(response_data['total'], int)
        self.assertIn('rows', response_data)
        self.assertIsInstance(response_data['rows'], list)
        self.assertEqual(
            len(response_data['rows']), response_data['total']
        )

        for row_data in response_data['rows']:
            self.assertIsInstance(row_data, dict)
            for name in StreetLoader._mapper_class.fields_map:
                self.assertIn(name, row_data)

    def test__house_search_action(self):
        """Проверка HouseSearchAction."""
        client = Client()

        response = client.post('/actions/fias/search/house', dict(
            # Запрос домов, номер которых начинается на "1" на ул. Ленина
            # в г. Новосибирске.
            parent='29090f1c-d114-430a-83bd-a4c254ef8ee9',
            filter='1',
        ))

        self.assertEqual(response.status_code, http_client.OK)
        response_data = json.loads(response.content)
        self.assertIn('total', response_data)
        self.assertIsInstance(response_data['total'], int)
        self.assertIn('rows', response_data)
        self.assertIsInstance(response_data['rows'], list)
        self.assertEqual(
            len(response_data['rows']), response_data['total']
        )

        for row_data in response_data['rows']:
            self.assertIsInstance(row_data, dict)
            for name in HouseLoader._mapper_class.fields_map:
                self.assertIn(name, row_data)
