# coding: utf-8
from __future__ import unicode_literals

from m3.actions import Action
from m3.actions import ActionPack
from m3_ext.ui.results import ExtUIScriptResult

from .ui import AddressWindow
from .ui import EditWindow


class AddressWindowAction(Action):

    """Действие для отображения окна с панелью редактирования адреса."""

    url = '/address-window'

    def run(self, request, context):
        window = AddressWindow()
        return ExtUIScriptResult(window)


class EditWindowAction(Action):

    url = '/edit-window'

    def run(self, request, context):
        window = EditWindow()
        return ExtUIScriptResult(window)


class Pack(ActionPack):

    """Пак для отображения тестового окна с панелью ввода адреса."""

    url = '/test'

    def __init__(self):
        super(Pack, self).__init__()

        self.address_window_action = AddressWindowAction()
        self.edit_window_action = EditWindowAction()
        self.actions.extend((
            self.address_window_action,
            self.edit_window_action,
        ))
