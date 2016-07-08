# coding: utf-8
from m3.actions import ActionController
from objectpack.desktop import uificate_the_controller

from m3_fias.demo.actions import FiasDemoPack


fias_controller = ActionController(url='/fias')


def register_actions():
    fias_controller.packs.extend([
        FiasDemoPack()
        ])


def register_desktop_menu():
    uificate_the_controller(fias_controller)
