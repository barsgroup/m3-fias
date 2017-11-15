# coding: utf-8
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod

from django.http.response import JsonResponse
from m3.actions import Action
from m3.actions import ActionPack

from m3_fias.utils import correct_keyboard_layout

from .utils import HouseLoader
from .utils import PlaceLoader
from .utils import StreetLoader


class ActionBase(Action):

    u"""Базовый класс для обработчиков запросов на поиск данных в ФИАС."""

    __metaclass__ = ABCMeta

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
        return JsonResponse(dict(
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
        return StreetLoader(context.filter, unicode(context.parent))


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
