# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod

from django.http import HttpResponse
from m3.actions import Action
from m3.actions import ActionPack
from six import text_type
from six import with_metaclass
import django

from m3_fias.utils import correct_keyboard_layout

from .utils import HouseLoader
from .utils import PlaceLoader
from .utils import StreetLoader


if django.VERSION < (1, 8):
    # Backport JsonResponse from Django 1.11
    import datetime
    import json

    class DjangoJSONEncoder(json.JSONEncoder):

        def default(self, o):  # pylint: disable=method-hidden
            # See "Date Time String Format" in the ECMA-262 specification.
            if isinstance(o, datetime.datetime):
                r = o.isoformat()
                if o.microsecond:
                    r = r[:23] + r[26:]
                if r.endswith('+00:00'):
                    r = r[:-6] + 'Z'
                return r
            elif isinstance(o, datetime.date):
                return o.isoformat()
            else:
                return super(DjangoJSONEncoder, self).default(o)

    class _JsonResponse(HttpResponse):

        def __init__(self, data, encoder=DjangoJSONEncoder, safe=True,
                     json_dumps_params=None, **kwargs):
            if safe and not isinstance(data, dict):
                raise TypeError(
                    'In order to allow non-dict objects to be serialized set '
                    'the safe parameter to False.'
                )
            if json_dumps_params is None:
                json_dumps_params = {}
            kwargs.setdefault('content_type', 'application/json')
            data = json.dumps(data, cls=encoder, **json_dumps_params)
            super(_JsonResponse, self).__init__(content=data, **kwargs)

else:
    from django.http.response import JsonResponse as _JsonResponse


class ActionBase(with_metaclass(ABCMeta, Action)):

    u"""Базовый класс для обработчиков запросов на поиск данных в ФИАС."""

    @abstractmethod
    def _get_loader(self, context):
        """Возвращает загрузчик данных.

        :rtype: m3_fias.backends.django_rest_fias.proxy.utils.LoaderBase
        """

    def context_declaration(self):
        return dict(
            filter=dict(type='unicode', default=''),
        )

    def run(self, request, context):
        context.filter = correct_keyboard_layout(context.filter)

        loader = self._get_loader(context)
        rows = loader.load()
        return _JsonResponse(dict(
            rows=rows,
            total=len(rows),
        ))


class PlaceSearchAction(ActionBase):

    """Обработчик запросов на поиск населенных пунктов."""

    url = '/search/place'

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return PlaceLoader(context.filter)


class ParentMixin(object):

    def context_declaration(self):
        result = super(ParentMixin, self).context_declaration()
        result.update(
            parent=dict(type='m3-fias:guid'),
        )
        return result


class StreetSearchAction(ParentMixin, ActionBase):

    """Обработчик запросов на поиск улиц в населенном пункте."""

    url = '/search/street'

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return StreetLoader(context.filter, text_type(context.parent))


class HouseSearchAction(ParentMixin, ActionBase):

    """Обработчик запросов на поиск домов."""

    url = '/search/house'

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return HouseLoader(context.parent, context.filter)


class Pack(ActionPack):

    u"""Набор действий для проксирования запросов к серверу ФИАС."""

    url = '/fias'

    def __init__(self):
        super(Pack, self).__init__()

        self.place_search_action = PlaceSearchAction()
        self.street_search_action = StreetSearchAction()
        self.house_search_action = HouseSearchAction()

        self.actions.extend((
            self.place_search_action,
            self.street_search_action,
            self.house_search_action,
        ))
