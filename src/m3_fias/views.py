#coding: utf-8
import json
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from m3_fias.helpers import FiasAddressObject, fias_server_session
from m3_fias.demo.app_meta import fias_controller


def address_proxy_view(request):
    u"""
    Запрос списка адресных объктов
    """
    cache_key = ':'.join((FiasAddressObject._CACHE_KEY_PREFIX, request.body))
    resp = cache.get(cache_key)
    if resp is None:
        dest_url = settings.FIAS_API_URL
        data = {
            'aolevel': ','.join(request.POST.getlist('levels')),
            'search': request.POST.get('filter'),
        }
        if request.POST.get('boundary'):
            data['parentguid'] = request.POST.get('boundary')

        resp = fias_server_session.get(
            dest_url,
            params=data,
            headers={'Content-Type': 'application/json'}
        )

        if resp.status_code == 200:  # запрос выполнен успешно
            cache.set(cache_key, resp, FiasAddressObject._CACHE_TIMEOUT)

    data = resp.json()

    for obj in data['results']:
        if 'aolevel' in obj and obj['aolevel'] in [6]:
            address_object = FiasAddressObject.create(obj['aoguid'])
            if address_object:
                district = address_object.parent
                region = district.parent
                obj['place_address'] = u', '.join((
                    u''.join((region.short_name, u'. ',
                              region.formal_name)),
                    u''.join((district.short_name, u'. ',
                              district.formal_name)),
                    u''.join((address_object.short_name, u'. ',
                              address_object.formal_name)),
                ))

        obj['postal_code'] = obj['postalcode']
        obj['ao_level'] = obj['aolevel']
        obj['ao_guid'] = obj['aoguid']
        obj['address'] = obj['fullname']
        obj['name'] = obj['fullname']
        obj['formal_name'] = obj['formalname']

        if 'aolevel' in obj and obj['aolevel'] in [7]:
            obj['name'] = '%s. %s'% (obj['shortname'], obj['formalname'])

    result = {
        'rows': data['results'],
        'total': data['count'],
    }

    return HttpResponse(json.dumps(result),
                        content_type=resp.headers['Content-Type'],
                        status=resp.status_code)


def houses_proxy_view(request):
    u"""
    Запрос списка домов
    """
    cache_key = ':'.join((FiasAddressObject._CACHE_KEY_PREFIX, request.body))
    resp = cache.get(cache_key)
    if resp is None:
        if request.POST.get('street'):
            street = request.POST.get('street')
        else:
            street = ''
        dest_url = '{0}{1}/houses/'.format(settings.FIAS_API_URL, street)
        data = {
            'search': request.POST.get('part'),
        }

        resp = fias_server_session.get(
            dest_url,
            params=data,
            headers={'Content-Type': 'application/json'}
        )

        if resp.status_code == 200:  # запрос выполнен успешно
            cache.set(cache_key, resp, FiasAddressObject._CACHE_TIMEOUT)

    data = resp.json()

    for obj in data['results']:
        obj['house_number'] = obj['housenum']
        obj['postal_code'] = obj['postalcode']

    result = {
        'rows': data['results'],
        'total': data['count'],
    }

    return HttpResponse(json.dumps(result),
                        content_type=resp.headers['Content-Type'],
                        status=resp.status_code)


def controller_view(request):
    return fias_controller.process_request(request)
