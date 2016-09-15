# coding: utf-8
from django.conf.urls import url

from .views import address_proxy_view
from .views import controller_view
from .views import houses_proxy_view


def register_actions():
    pass


def register_urlpatterns():
    return [
        url(
            r'^fias/remote/list/houses$',
            houses_proxy_view,
            name='houses_proxy_view'
        ),
        url(
            r'^fias/remote/search$',
            address_proxy_view,
            name='address_proxy_view'
        ),
        url(
            r'^fias/',
            controller_view
        )
    ]
