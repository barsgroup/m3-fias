# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from django.views.generic.base import TemplateView
from m3_ext.context_processors import DesktopProcessor


class Index(TemplateView):

    template_name = 'desktop.html'

    def get_context_data(self, **kwargs):
        result = super(Index, self).get_context_data(**kwargs)

        result.update(
            DesktopProcessor.process(self.request),
        )

        return result
