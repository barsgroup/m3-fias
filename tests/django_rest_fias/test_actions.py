# coding: utf-8
# pylint: disable=protected-access
from __future__ import unicode_literals

from unittest import skipUnless
import httplib
import json

from django import test
from django.conf import settings
from django.test import Client

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

        self.assertEqual(response.status_code, httplib.OK)
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

        self.assertEqual(response.status_code, httplib.OK)
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

        self.assertEqual(response.status_code, httplib.OK)
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

    def test__zip_code_action(self):
        """Проверка ZipCodeAction."""
        def send_request(ao_guid, house_guid=None):
            params = dict(
                address_object_guid=ao_guid,
            )
            if house_guid:
                params['house_guid'] = house_guid

            client = Client()

            return client.post('/actions/fias/zip-code', params)

        for ao_guid, house_guid, zip_code in (
            (
                # г Новосибирск
                '8dea00e3-9aab-4d8e-887c-ef2aaa546456',
                None,
                None
            ), (
                # Мурманская обл, г Полярные Зори, нп Зашеек: индекс есть
                'b04bec8c-8d21-4b96-8ec1-7412bb50914e',
                None,
                '184230'
            ), (
                # г. Новосибирск, ул. Ленина: индекс нет.
                '29090f1c-d114-430a-83bd-a4c254ef8ee9',
                None,
                None
            ), (
                # Забайкальский край, г Чита, пер 2-й Рабочий: индекс есть
                'd4b170d2-2fbe-4e84-81cf-6ca77a0a14be',
                None,
                '672040'
            ), (
                # г Чита, ул Ленина, д. 159: индекс есть
                '0d5c91c9-433f-43be-bc20-e7ebf352ccad',
                '0d1ad06b-0f7f-493f-9076-0a05225af36c',
                '672000'
            )
        ):
            response = send_request(ao_guid, house_guid)
            self.assertEqual(response.status_code, httplib.OK)
            response_data = json.loads(response.content)
            self.assertIn('zipCode', response_data)
            self.assertEqual(response_data['zipCode'], zip_code)
