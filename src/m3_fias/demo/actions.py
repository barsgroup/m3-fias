#coding: utf-8

from m3.actions import ActionPack, Action
from m3_ext.ui.windows import ExtEditWindow
from m3_ext.ui.containers import ExtContextMenu, ExtForm
from m3_ext.ui.controls.buttons import ExtButton
from m3_ext.ui.shortcuts import js_close_window
from m3_ext.ui.results import ExtUIScriptResult

from m3_fias.addrfield import ExtFiasAddrComponent
from m3.actions.results import OperationResult


class FiasWindow(ExtEditWindow):

    def __init__(self, *args, **kwargs):
        super(ExtEditWindow, self).__init__(*args, **kwargs)

        self.width = 500

        self.form = ExtForm()
        self.data_url = '/asd'
        self.addrfield = ExtFiasAddrComponent(use_corps=True)

        self.form.items.append(self.addrfield)

        save_btn = ExtButton(text=u'Выбрать', handler="""function(){
            var form = Ext.getCmp('%s').form;
            form.submit();
        }""" % self.form.client_id);
        cancel_btn = ExtButton(text=u'Отмена', handler=js_close_window(self))
        self.buttons.extend([save_btn, cancel_btn])        
        self.items.append(self.form)

class FiasWindowAction(Action):
    url = '/window'

    def run(self, request, context):
        win = FiasWindow()
        return ExtUIScriptResult(win)


class FiasDemoPack(ActionPack):
    url = '/demo'

    def __init__(self, *args, **kwargs):
        super(FiasDemoPack, self).__init__(*args, **kwargs)
        self.window_action = FiasWindowAction()
        self.actions.append(self.window_action)
