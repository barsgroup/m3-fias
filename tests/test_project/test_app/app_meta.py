# coding: utf-8
from __future__ import unicode_literals

from m3.actions import ControllerCache
from m3_ext.ui.app_ui import DesktopLoader
from m3_ext.ui.app_ui import add_desktop_launcher

from ..controllers import controller
from .actions import Pack


def register_actions():
    controller.extend_packs((
        Pack(),
    ))


def register_desktop_menu():
    pack = ControllerCache.find_pack(Pack)
    add_desktop_launcher(
        name='Тестовое окно',
        url=pack.address_window_action.get_absolute_url(),
        metaroles='generic',
        places=DesktopLoader.START_MENU,
    )
    add_desktop_launcher(
        name='Окно с формой',
        url=pack.edit_window_action.get_absolute_url(),
        metaroles='generic',
        places=DesktopLoader.START_MENU,
    )
