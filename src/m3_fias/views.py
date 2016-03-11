# coding: utf-8
from m3_fias.demo.app_meta import fias_controller
from m3_fias.helpers import get_fias_service, get_ao_object, get_response

# Признак успешности выполнения запроса
STATUS_CODE_OK = 200


def address_proxy_view(request):
    u"""Запрос списка адресных объктов."""
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

    for obj in data.get('results', []):
        obj.update(get_ao_object(obj['aoguid']))

    result = {
        'rows': data.get('results', []),
        'total': data.get('count', 0),
    }

    return get_response(data, result)


def houses_proxy_view(request):
    """Запрос списка домов по улице, если она существует, либо по нас. пункту
    """
    street = request.POST.get('street')
    place = request.POST.get('place')
    data = {
        'search': request.POST.get('part'),
    }
    address_object = street or place or ''

    resp = get_fias_service(
        address_object + '/houses/',
        data
    )
    if resp.status_code == STATUS_CODE_OK:  # запрос выполнен успешно
        data = resp.json()
        data['status_code'] = resp.status_code
        data['Content-Type'] = resp.headers['Content-Type']

    for obj in data.get('results', []):
        obj['house_number'] = obj['housenum']
        obj['postal_code'] = obj['postalcode']

    result = {
        'rows': data.get('results', []),
        'total': data.get('count', 0),
    }

    return get_response(data, result)


def controller_view(request):
    return fias_controller.process_request(request)