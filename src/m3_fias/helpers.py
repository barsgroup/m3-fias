# coding: utf-8
import uuid
import datetime
import requests
from django.conf import settings
from django.utils.functional import cached_property
from django.core.cache import cache


class FiasServerError(IOError):
    """Ошибка на сервере ФИАС
    """
    def __init__(self, response):
        self.response = response


def get_ao_object(guid):
    uuid.UUID(guid)  # проверка, GUID это или нет

    request_path = '{0}/objects/ao/{1}'.format(settings.FIAS_API_URL, guid)
    response = requests.get(request_path, params={'trust_env': False})

    if response.status_code == 404:
        # объект с указанным GUID не найден в ФИАС
        return None
    elif response.status_code == 200:
        obj = response.json()

        return {
            'ao_guid': obj['guid'],
            'ao_level': obj['level'],
            'address': obj['address'],
            'shortname': obj['short_name'],
            'formal_name': obj['formal_name'],
            'name': u'{0}. {1}'.format(obj['short_name'], obj['formal_name'])
        }
    else:
        raise FiasServerError(response=response)


def kladr2fias(code):
    """Конвертация кода КЛАДР в код ФИАС.

    :param code: кода объекта в КЛАДР
    :return: UUID соответствущего объекта в ФИАС
    :rtype: str
    :raises ValueError: если *code* не является числом
    :raises m3_fias.helpers.FiasServerError: если во время выполнения запроса
        на сервере ФИАС возникла ошибка
    """
    code = str(code)

    if not code.isdigit():
        raise ValueError(code)

    response = requests.post(
        settings.FIAS_API_URL + '/translate',
        data=dict(kladr=code)
    )

    if response.status_code == 404:
        # объект с указанным кодом не найден
        return None
    elif response.status_code == 200:
        data = response.json()
        if data['total'] == 0:
            return None
        else:
            return data['codes'][code]
    else:
        raise FiasServerError(response=response)


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

    # параметры кеширования данных ФИАС
    _CACHE_KEY_PREFIX = 'm3-fias'
    _CACHE_TIMEOUT = 24 * 60 * 60  # таймаут кеширования - 1 сутки

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
        cache_key = ':'.join((FiasAddressObject._CACHE_KEY_PREFIX, guid))
        result = cache.get(cache_key)
        if result is not None:
            return result

        response = requests.get(
            '/'.join((settings.FIAS_API_URL, 'objects', 'ao', guid)),
            params={'trust_env': False}
        )

        if response.status_code == 200:
            result = response.json()
        elif response.status_code == 404:
            result = None
        else:
            raise FiasServerError(response=response)

        cache.set(cache_key, result, FiasAddressObject._CACHE_TIMEOUT)

        return result

    def _set_object_data(self, data):
        self.level = data['level']
        self.record_guid = unicode(uuid.UUID(data['_record']))
        self.formal_name = data['formal_name']
        self.official_name = data['official_name']
        self.short_name = data['short_name']
        self.address = data['address']
        self.postcode = data['postcode']
        self.okato = data['okato']
        self.oktmo = data['oktmo']
        self.ifnsfl = data['ifnsfl']
        self.ifnsul = data['ifnsul']
        self.terr_ifnsfl = data['terr_ifnsfl']
        self.terr_ifnsul = data['terr_ifnsul']

        if data['parent_guid']:
            self.parent_guid = unicode(uuid.UUID(data['parent_guid']))

        if data['updated']:
            self.updated = datetime.datetime.strptime(data['updated'],
                                                      '%d.%m.%Y')

    def __init__(self, guid):
        self.guid = unicode(uuid.UUID(guid))

        object_data = FiasAddressObject._get_object_data(self.guid)
        if object_data is not None:
            self._set_object_data(object_data)

    @cached_property
    def parent(self):
        """Родительский адресный объект.
        """
        if self.parent_guid:
            return FiasAddressObject(self.parent_guid)
        else:
            return None
