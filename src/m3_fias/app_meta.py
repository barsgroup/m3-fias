#coding: utf-8

from django.conf import urls

def register_actions():
    pass


def register_urlpatterns():
    return urls.defaults.patterns('',
        urls.url(r'^fias/remote/list/houses$', 'm3_fias.views.houses_proxy_view',
                 name='houses_proxy_view'),
        urls.url(r'^fias/remote/search$', 'm3_fias.views.address_proxy_view',
                 name='address_proxy_view'),
    	(r'^fias/', 'm3_fias.views.controller_view')
    )
