# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import m3_fias


def register_actions():
    m3_fias.config.backend.register_packs()
