#coding: utf-8

from m3.actions import ActionController, ControllerCache

from m3_fias.demo.actions import FiasDemoPack

from m3_ext.ui.app_ui import add_desktop_launcher
from objectpack import uificate_the_controller


fias_controller = ActionController(url='/fias')


def register_actions():
    fias_controller.packs.extend([
        FiasDemoPack()
        ])

def register_desktop_menu():
    uificate_the_controller(fias_controller)
	# pack = ControllerCache.find_pack(FiasDemoPack)
	# add_desktop_launcher(u'Адресный компонент ФИАС', 
	# 					 metaroles=('none'),
	# 					 places=(1),
	# 					 url=pack.window_action.get_absolute_url())