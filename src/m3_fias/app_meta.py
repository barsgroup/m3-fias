#coding: utf-8

from django.conf import urls

def register_actions():
    pass


def register_urlpatterns():
    return urls.defaults.patterns('', 
    	urls.url(r'^fias/remote/(.*)', 
                 'm3_fias.views.post_proxy_view', 
                 name='fias_proxy_view'),
    	(r'^fias/', 'm3_fias.views.controller_view')
    )
