# coding: utf-8
from __future__ import unicode_literals

from itertools import chain

from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from m3.actions.urls import get_app_urlpatterns

from .controllers import controller
from .test_app.views import Index


urlpatterns = list(chain(
    [
        url('^$', Index.as_view()),
        url(*controller.urlpattern),
    ],
    staticfiles_urlpatterns(),
    get_app_urlpatterns(),
))
