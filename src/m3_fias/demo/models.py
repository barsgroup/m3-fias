#coding: utf-8

from objectpack.models import VirtualModel


residencies = {}


class Residence(VirtualModel):

    @classmethod
    def _get_ids(self):
        return iter(residencies.values())

    def __init__(self, data=None):
        self.description = u''
        self.house_guid = None
        self.house = None
        self.street = None
        self.place = None
        self.addr = None
        self.flat = None
        self.corps = None

        self.__dict__.update(data or {})

    @classmethod
    def delete_by_id(self, obj_id):
        residencies.pop(obj_id)

    def save(self):
        if not getattr(self, 'id', None):
            self.id = len(residencies) + 1
        residencies[self.id] = self.__dict__.copy()
        
    def delete(self):
        residencies.pop(self.id)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.description, self.addr)

    class _meta:
        verbose_name = u'Места проживания'
