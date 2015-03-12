#coding: utf-8
import json
from django.core.cache import cache
from django.http import HttpResponse
from m3_fias.helpers import FiasAddressObject, get_fias_service
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
        if 'aolevel' in obj and obj['aolevel'] in [6]:
            address_object = FiasAddressObject.create(obj['aoguid'])
            if address_object:
                district = address_object.parent
                region = district.parent
                if region is not None:
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
            obj['name'] = '%s. %s' % (obj['shortname'], obj['formalname'])

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
    u"""Запрос списка домов."""
    cache_key = ':'.join((FiasAddressObject._CACHE_KEY_PREFIX, request.body))
    data = cache.get(cache_key)
    street = request.POST.get('street')
    if not street:
        return HttpResponse(
            json.dumps({
                'rows': [],
                'total': 0,
            }),
            content_type='application/json',
            status=STATUS_CODE_OK
        )

    if data is None:
        data = {
            'search': request.POST.get('part'),
        }

        resp = get_fias_service(
            street + '/houses/',
            data
        )

        if resp.status_code == STATUS_CODE_OK:  # запрос выполнен успешно
            data = resp.json()
            data['status_code'] = resp.status_code
            data['Content-Type'] = resp.headers['Content-Type']
            cache.set(cache_key, data, FiasAddressObject._CACHE_TIMEOUT)

    for obj in data['results']:
        obj['house_number'] = obj['housenum']
        obj['postal_code'] = obj['postalcode']

    result = {
        'rows': data['results'],
        'total': data['count'],
    }

    return HttpResponse(
        json.dumps(result),
        content_type=data['Content-Type'],
        status=data['status_code']
    )


def controller_view(request):
    return fias_controller.process_request(request)
