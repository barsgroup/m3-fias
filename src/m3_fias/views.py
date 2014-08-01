#coding: utf-8

import requests

from django.conf import settings
from django.http import HttpResponse

from m3_fias.demo.app_meta import fias_controller

def post_proxy_view(request, path):
    dest_url = '{0}/{1}'.format(settings.FIAS_API_URL, path)

    resp = requests.post(dest_url,
                         params={'trust_env': False},
                         cookies=request.COOKIES,
                         data=request.body,
                         headers={'Content-Type': request.META['CONTENT_TYPE']})
    return HttpResponse(resp.content,
                        content_type=resp.headers['Content-Type'],
                        status=resp.status_code)


def controller_view(request):
    return fias_controller.process_request(request)
