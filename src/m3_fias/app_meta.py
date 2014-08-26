#coding: utf-8
from django.conf.urls import url
try:
    # для django 1.3
    from django.conf.urls.defaults import patterns
except ImportError:
    # для django > 1.3
    from django.conf.urls import patterns

def register_actions():
    pass


def register_urlpatterns():
    return patterns('',
        url(r'^fias/remote/list/houses$', 'm3_fias.views.houses_proxy_view',
            name='houses_proxy_view'),
        url(r'^fias/remote/search$', 'm3_fias.views.address_proxy_view',
            name='address_proxy_view'),
        (r'^fias/', 'm3_fias.views.controller_view')
    )
