# coding: utf-8
import uuid
import requests
from django.conf import settings


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
