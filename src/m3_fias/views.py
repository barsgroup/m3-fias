#coding: utf-8
import json
from django.core.cache import cache
from django.http import HttpResponse
from m3_fias.helpers import FiasAddressObject, get_fias_service, get_ao_object
from m3_fias.demo.app_meta import fias_controller

# Признак успешности выполнения запроса
STATUS_CODE_OK = 200


def address_proxy_view(request):
    u"""Запрос списка адресных объктов."""
    cache_key = ':'.join((FiasAddressObject._CACHE_KEY_PREFIX, request.body))
    data = cache.get(cache_key)
    if data is None:
        data = {
            'aolevel': ','.join(request.POST.getlist('levels')),
            'scan': request.POST.get('filter'),
        }
        if request.POST.get('boundary'):
            data['parentguid'] = request.POST.get('boundary')

        resp = get_fias_service(
            '',
            data
        )

        if resp.status_code == STATUS_CODE_OK:  # запрос выполнен успешно
            data = resp.json()
            data['status_code'] = resp.status_code
            data['Content-Type'] = resp.headers['Content-Type']
            cache.set(cache_key, data, FiasAddressObject._CACHE_TIMEOUT)

    for obj in data['results']:
        obj.update(get_ao_object(obj['aoguid']))

    result = {
        'rows': data['results'],
        'total': data['count'],
    }

    return HttpResponse(
        json.dumps(result),
        content_type=data['Content-Type'],
        status=data['status_code']
    )


def houses_proxy_view(request):
    """Запрос списка домов по улице, если она существует, либо по нас. пункту
    """
    cache_key = ':'.join((FiasAddressObject._CACHE_KEY_PREFIX, request.body))
    data = cache.get(cache_key)
    street = request.POST.get('street')
    place = request.POST.get('place')
    if data is None:
        data = {
            'search': request.POST.get('part'),
        }
        address_object = street if street else place

        resp = get_fias_service(
            address_object + '/houses/',
            data
        )
        if resp.status_code == STATUS_CODE_OK:  # запрос выполнен успешно
            data = resp.json()
            data['status_code'] = resp.status_code
            data['Content-Type'] = resp.headers['Content-Type']
            cache.set(cache_key, data, FiasAddressObject._CACHE_TIMEOUT)

    for obj in data.get('results', []):
        obj['house_number'] = obj['housenum']
        obj['postal_code'] = obj['postalcode']

    result = {
        'rows': data.get('results', []),
        'total': data.get('count', 0),
    }
    if data.get('Content-Type'):
        return HttpResponse(
            json.dumps(result),
            content_type=data['Content-Type'],
            status=data['status_code']
        )
    else:
        return HttpResponse(json.dumps(result))


def controller_view(request):
    return fias_controller.process_request(request)
