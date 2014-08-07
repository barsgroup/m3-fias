# coding: utf-8
import uuid
import datetime
import requests
from django.conf import settings
from django.utils.functional import cached_property
from django.core.cache import cache


# сессия для доступа к серверу ФИАС по HTTP/1.1
fias_server_session = requests.Session()


class FiasAddressObjectDoesNotExist():
    """Запрошенный объект не существует.
    """


class FiasServerError(IOError):
    """Ошибка на сервере ФИАС
    """
    def __init__(self, response):
        self.response = response


def get_ao_object(guid):
    address_object = FiasAddressObject.create(guid)
    result = {}
    if address_object is not None:
        name = u'{0}. {1}'.format(address_object.short_name,
                                  address_object.formal_name)
        result = {
            'ao_guid': address_object.guid,
            'ao_level': address_object.level,
            'address': address_object.address,
            'shortname': address_object.short_name,
            'formal_name': address_object.formal_name,
            'name': name,
        }

    return result


def kladr2fias(code, generate_error=False):
    """Конвертация кода КЛАДР в код ФИАС.

    :param code: кода объекта в КЛАДР
    :generate_error bool generate_error: определяет, будут ли генерироваться
        исключения, если равен False, то в случае ошибки функция вернет пустую
        строку
    :return: UUID соответствущего объекта в ФИАС
    :rtype: str
    :raises ValueError: если *code* не является числом
    :raises m3_fias.helpers.FiasServerError: если во время выполнения запроса
        на сервере ФИАС возникла ошибка
    """
    code = str(code)

    if not code.isdigit():
        if generate_error:
            raise ValueError(code)
        else:
            return u''

    response = fias_server_session.post(
        settings.FIAS_API_URL + '/translate',
        data=dict(kladr=code)
    )

    if response.status_code == 404:
        # объект с указанным кодом не найден
        return u''
    elif response.status_code == 200:
        data = response.json()
        if data['total'] == 0:
            return u''
        else:
            return data['codes'][code]
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

        response = fias_server_session.get(
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
        """
        object_data = FiasAddressObject._get_object_data(guid)
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
