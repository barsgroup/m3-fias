# coding: utf-8
from m3_ext.ui.fields.simple import ExtStringField
from m3_fias.addrfield import ExtFiasAddrComponent
from objectpack.actions import ObjectPack
from objectpack.ui import BaseEditWindow

from m3_fias.demo.models import Residence


class FiasEditWindow(BaseEditWindow):
    def _init_components(self):
        super(FiasEditWindow, self)._init_components()
        self.description = ExtStringField(label=u'Наименование',
                                          name='description')
        self.addrfield = ExtFiasAddrComponent(use_corps=True)

    def _do_layout(self):
        super(FiasEditWindow, self)._do_layout()
        self.form.items.extend([
            self.description,
            self.addrfield
            ])

    def set_params(self, params):
        super(FiasEditWindow, self).set_params(params)
        self.width = 800


class FiasDemoPack(ObjectPack):
    title = u'Адресный элемент ФИАС'
    model = Residence
    add_window = edit_window = FiasEditWindow
    add_to_desktop = True
    add_to_menu = True

    columns = [{
        'data_index': 'description',
        'header': u'Наименование'
    },
    {
        'data_index': 'addr',
        'header': u'Адрес'
    }]

    def delete_row(self, obj_id, request, context):
        Residence.delete_by_id(obj_id)
