#coding: utf-8

from django.conf import settings

import requests


def get_ao_object(guid):
    request_path = '{0}/objects/ao/{1}'.format(settings.FIAS_API_URL, guid)

    resp = requests.get(request_path, proxies={'http': '', 'https': ''})
    obj = resp.json()

    result = {
        'ao_guid': obj['guid'],
        'ao_level': obj['level'],
        'address': obj['address'],
        'shortname': obj['short_name'],
        'name': u'{0}. {1}'.format(obj['short_name'], obj['formal_name'])
    }
    return result