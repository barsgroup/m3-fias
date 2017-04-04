# coding: utf-8
from itertools import islice
import datetime
import json
import os
import re
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Q
from django.http import HttpResponse
from django.utils.functional import cached_property
import requests

# параметры кеширования данных ФИАС
_CACHE_KEY_PREFIX = 'm3-fias'
if hasattr(settings, 'FIAS_CACHE_PREFIX') and settings.FIAS_CACHE_PREFIX:
    _CACHE_KEY_PREFIX = settings.FIAS_CACHE_PREFIX

# таймаут кеширования, по умолчанию 1 сутки
_CACHE_TIMEOUT = 24 * 60 * 60
if hasattr(settings, 'FIAS_CACHE_TIMEOUT') and settings.FIAS_CACHE_TIMEOUT:
    _CACHE_TIMEOUT = settings.FIAS_CACHE_TIMEOUT


# сессия для доступа к серверу ФИАС по HTTP/1.1
fias_server_session = None


class FiasAddressObjectDoesNotExist(Exception):
    """Запрошенный объект не существует.
    """


class FiasServerError(IOError):
    """Ошибка на сервере ФИАС
    """
    def __init__(self, response):
        self.response = response


def get_verbose_name(address_object):
    """Возвращает имя нас. пункта в формате: г. Москва
    :param address_object: объект FiasAddressObject
    """
    return u'{0}. {1}'.format(address_object.short_name,
                              address_object.formal_name)


def get_ao_object(guid):
    """Подготовка данных для стора контрола на клиенте
    Для уровней "регион", "автономный округ", "улица" и "объект,
    подчиненный дополнительной территории"
    показываем в поле только наименование объекта, для других полный адрес.
    :param guid: идентификатор фиаса
    :rtype: str
    """
    address_object = FiasAddressObject.create(guid)
    result = {}
    if address_object is not None:
        name = (u'{0}. {1}'.format(
            address_object.short_name, address_object.formal_name)
            if address_object.level in [
                address_object.LEVEL_REGION,
                address_object.LEVEL_AUTONOMOUS_DISTRICT,
                address_object.LEVEL_STREET,
                address_object.LEVEL_AT_SUBORDINATED_OBJECT]
            else address_object.address)
        result = {
            'ao_guid': address_object.guid,
            'ao_level': address_object.level,
            'address': address_object.address,
            'shortname': address_object.short_name,
            'formal_name': address_object.formal_name,
            'name': name,
            'postal_code': address_object.postcode
        }
        list_parent = []
        if address_object.parent:
            district = address_object.parent
            if district.parent:
                region = district.parent
                list_parent.append(get_verbose_name(region))
            list_parent.append(get_verbose_name(district))
        list_parent.append(get_verbose_name(address_object))

        result['place_address'] = u', '.join(list_parent)

    return result


def extend_addresses(addresses):
    u"""Генератор адресных объектов с детальной информацией.

    Принимает набор адресных объектов и расширяет их дополнительной
    информацией.
    Если получить дополнительную информацию для адресного объекта не
    удалось, то он не будет отдан клиенту.
    """

    for address in addresses:
        ao_object = get_ao_object(address['aoguid'])

        if ao_object is not None:
            address.update(ao_object)
            yield address


def kladr2fias(kladr_code, generate_error=False):
    """Конвертация кода КЛАДР в код ФИАС.

    :param kladr_code: кода объекта в КЛАДР
    :generate_error bool generate_error: определяет, будут ли генерироваться
        исключения, если равен False, то в случае ошибки функция вернет пустую
        строку
    :return: UUID соответствущего объекта в ФИАС
    :rtype: str
    :raises ValueError: если *kladr_code* не является числом
    :raises m3_fias.helpers.FiasServerError: если во время выполнения запроса
        на сервере ФИАС возникла ошибка
    """
    kladr_code = unicode(kladr_code)

    if not kladr_code.isdigit():
        if generate_error:
            raise ValueError(kladr_code)
        else:
            return u''

    response = get_fias_service(
        '',
        {'code': kladr_code, 'view': 'simple'}
    )

    if response.status_code == 200:
        data = response.json()
        if data['count'] == 0:
            fias_code = u''
        else:
            fias_code = data['results'][0]['aoguid']
        return fias_code
    else:
        if generate_error:
            raise FiasServerError(response=response)
        else:
            return u''


class FiasAddressObject(object):
    """Адресный объект ФИАС. Предоставляет интерфейс доступа к информации в
    базе ФИАС.
    """
    # регион
    LEVEL_REGION = 1
    # автономный округ
    LEVEL_AUTONOMOUS_DISTRICT = 2
    # район
    LEVEL_DISTRICT = 3
    # город
    LEVEL_CITY = 4
    # внутригородская территория
    LEVEL_CITY_TERRITORY = 5
    # населенный пункт
    LEVEL_PLACE = 6
    # улица
    LEVEL_STREET = 7
    # дополнительная территория
    LEVEL_ADDITIONAL_TERRITORY = 90
    # объект, подчиненный дополнительной территории
    LEVEL_AT_SUBORDINATED_OBJECT = 91

    # Уровень адресного объекта
    level = None
    # GUID объекта
    guid = None
    # GUID записи в базе ФИАС
    record_guid = None
    # GUID родительского объекта
    parent_guid = None
    # Формализованное наименование объекта
    formal_name = None
    # Официальное наименование объекта
    official_name = None
    # Краткое наименование типа объекта
    short_name = None
    # Адрес объекта
    address = None
    # Почтовый индекс
    postcode = None
    # Код ОКАТО
    okato = None
    # Код ОКТМО
    oktmo = None
    # Код ИФНС ФЛ
    ifnsfl = None
    # Код ИФНС ЮЛ
    ifnsul = None
    # Код территориального участка ИФНС ФЛ
    terr_ifnsfl = None
    # Код территориального участка ИФНС ЮЛ
    terr_ifnsul = None
    # Дата внесения (обновления) записи
    updated = None

    @staticmethod
    def _get_object_data(guid):
        """Загрузка данных с сервера ФИАС. Загружаемые данные кешируются.
        """
        response = get_fias_service(
            guid + '/'
        )

        if response.status_code == 200:
            result = response.json()
        elif response.status_code == 404:
            result = None
        else:
            raise FiasServerError(response=response)

        return result

    def _set_object_data(self, data):

        self.level = data['aolevel']
        self.record_guid = unicode(uuid.UUID(data['aoid']))
        self.formal_name = data['formalname']
        self.official_name = data['offname']
        self.short_name = data['shortname']
        self.address = data['fullname']
        self.postcode = data.get('postcode', '')
        self.okato = data.get('okato', '')
        self.oktmo = data.get('oktmo', '')
        self.ifnsfl = data.get('ifnsfl', '')
        self.ifnsul = data.get('ifnsul', '')
        self.terr_ifnsfl = data.get('terr_ifnsfl', '')
        self.terr_ifnsul = data.get('terr_ifnsul', '')

        if data['parentguid']:
            self.parent_guid = unicode(uuid.UUID(data['parentguid']))

        if data.get('updated'):
            self.updated = datetime.datetime.strptime(data['updated'],
                                                      '%d.%m.%Y')

    def __init__(self, guid):
        self.guid = unicode(uuid.UUID(guid))

    @staticmethod
    def create(guid, generate_error=False):
        """Возвращает адресный объект, заполненный данными, полученными с
        сервера ФИАС. Если generate_error == True, то в случае проблем будут
        генерироваться исключения, иначе метод вернет None.

        :param unicode guid: GUID адресного объекта.
        :param bool generate_error: флаг, определяющий необходимость генерации
            исключений в случае ошибок.
        :rtype: FiasAddressObject | NoneType
        :raises ValueError: если значение аргумента guid не является
            идентификатором GUID.
        :raises FiasAddressObjectDoesNotExist: если адресный объект с указанным
            идентификатором не существует в базе ФИАС.
        :raises FiasServerError: если во время запроса данных с сервера ФИАС
            произошла ошибка.
        :raises requests.ConnectionError: если не удалось соединиться с
            сервером ФИАС
        """
        try:
            object_data = FiasAddressObject._get_object_data(guid)
        except (requests.ConnectionError, FiasServerError):
            if generate_error:
                raise
            else:
                return None

        if object_data is None:
            if generate_error:
                raise FiasAddressObjectDoesNotExist()
            else:
                return None
        else:
            result = FiasAddressObject(guid)
            result._set_object_data(object_data)
            return result

    @cached_property
    def parent(self):
        """Родительский адресный объект.
        """
        if self.parent_guid:
            return FiasAddressObject.create(self.parent_guid)
        else:
            return None


# валидатор для полей моделей, содержащих коды адресных объектов ФИАС
fias_field_validator = RegexValidator(
    regex=re.compile(
        '^$|^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    ),
    message=u'Указан неверный код адресного объекта ФИАС'
)


def get_fias_service(url='', params=None):
    u""" Запрос к rest-сервису ФИАС
    """
    cache_key = ':'.join((_CACHE_KEY_PREFIX, url, json.dumps(params)))
    resp = cache.get(cache_key)
    if resp is not None:
        return resp

    global fias_server_session
    if fias_server_session is None:
        if hasattr(settings, 'FIAS_OAUTH2'):
            from requests_oauthlib import OAuth2Session
            from oauthlib.oauth2 import LegacyApplicationClient
            if __debug__:
                os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', 'True')
            fias_server_session = OAuth2Session(
                client=LegacyApplicationClient(settings.FIAS_OAUTH2['CLIENT_ID'])
            )
            fias_server_session.trust_env = True
            fias_server_session.fetch_token(
                token_url=settings.FIAS_OAUTH2['TOKEN_URL'],
                username=settings.FIAS_OAUTH2['USERNAME'],
                password=settings.FIAS_OAUTH2['PASSWORD'],
                client_id=settings.FIAS_OAUTH2['CLIENT_ID'],
                client_secret=settings.FIAS_OAUTH2['CLIENT_SECRET']
            )
        else:
            fias_server_session = requests.Session()
            fias_server_session.trust_env = True

    resp = fias_server_session.get(
        settings.FIAS_API_URL + url,
        params=params,
        headers={'Content-Type': 'application/json'}
    )

    # Сохранять в кэш только ответы на запросы, завершившиеся успешно.
    if resp.status_code == 200:
        cache.set(cache_key, resp, _CACHE_TIMEOUT)

    return resp


def translate_kladr_codes(query, field_names, clean_invalid=False,
                          batch_size=100):
    u"""Выполняет перевод кодов КЛАДР в коды ФИАС в указанных полях модели.

    Соответствующие коды ФИАС запрашиваются на сервере ФИАС.

    :param query: запрос на выборку записей, в которых нужно выполнить замену
        кодов адресных объектов
    :type query: django.db.models.query.QuerySet

    :param str field_names: список названий полей модели, в которых будет
        осуществляться поиск и замена кодов КЛАДР.

    :param bool clean_invalid: флаг, определяющих необходимость удаления
        непреобразованных кодов путем замены их пустой строкой

    :param int batch_size: количество кодов КЛАДР, отправляемых на сервер ФИАС,
        в одном запросе.

    :raises requests.exceptions.ConnectionError: если не удалось
        подключиться к серверу ФИАС
    """
    # перевод кодов адресных объектов из КЛАДР в ФИАС
    for field_name in field_names:
        kladr_codes = query.exclude(
            Q(**{field_name: u''}) | Q(**{field_name + '__isnull': True})
        ).values_list(field_name, flat=True).distinct().iterator()

        batch = u','.join(islice(kladr_codes, 0, batch_size))
        if not batch:
            continue

        response = get_fias_service('', dict(code=batch, view='simple'))
        if response.status_code != 200 or not response.json()['count']:
            continue

        for record in response.json()['results']:
            query.filter(
                **{field_name: record['code']}
            ).update(
                **{field_name: record['aoguid']}
            )

    # удаление непреобразованных данных
    if clean_invalid:
        for obj in query.iterator():
            changed = False
            for field_name in field_names:
                field_value = getattr(obj, field_name)
                if not field_value:
                    continue

                try:
                    fias_field_validator(field_value)
                except ValidationError:
                    setattr(obj, field_name, u'')
                    changed = True

            if changed:
                obj.save()


def get_response(data, result):
    u"""Возвращает объект HttpResponse, с результатом запроса к ФИАС.

    Если запрос к ФИАС выполнился успешно, то вернет объект со свойствами
    content_type и status_code и результатом, если нет, то вернет с пустым
    результатом.

    :param dict data: Словарь с данными ответа от ФИАС.
    :param dict result: Словарь, готовый к передаче ответ.

    :rtype HttpResponse.
    """
    if data.get('Content-Type'):
        return HttpResponse(
            json.dumps(result),
            content_type=data['Content-Type'],
            status=data['status_code']
        )
    else:
        return HttpResponse(json.dumps(result))
