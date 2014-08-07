#coding: utf-8
import json
from django.conf import settings
from django.http import HttpResponse
from m3_fias.helpers import FiasAddressObject, fias_server_session
from m3_fias.demo.app_meta import fias_controller


def post_proxy_view(request, path):
    dest_url = '{0}/{1}'.format(settings.FIAS_API_URL, path)

    resp = fias_server_session.post(
        dest_url,
        params={'trust_env': False},
        cookies=request.COOKIES,
        data=request.body,
        headers={'Content-Type': request.META['CONTENT_TYPE']}
    )

    data = resp.json()
    for obj in data['rows']:
        if 'ao_level' in obj and obj['ao_level'] == 6:
            address_object = FiasAddressObject.create(obj['ao_guid'])
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

    return HttpResponse(json.dumps(data),
                        content_type=resp.headers['Content-Type'],
                        status=resp.status_code)


def controller_view(request):
    return fias_controller.process_request(request)
